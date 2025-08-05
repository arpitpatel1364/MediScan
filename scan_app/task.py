from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

from .models import Reminder, UserProfile, MedicineScan, HealthInsight
from .utils import send_reminder_notification, check_medicine_interactions

logger = logging.getLogger(__name__)

@shared_task
def send_reminder_notifications():
    """
    Periodic task to send medicine reminder notifications
    Run this task every 5 minutes
    """
    try:
        current_time = timezone.now()
        
        # Get reminders that are due within the next 5 minutes
        due_reminders = Reminder.objects.filter(
            is_active=True,
            next_reminder__lte=current_time + timedelta(minutes=5),
            next_reminder__gte=current_time - timedelta(minutes=5)
        )
        
        notifications_sent = 0
        
        for reminder in due_reminders:
            try:
                # Check if notification was already sent for this time slot
                if reminder.last_notification_sent:
                    time_diff = current_time - reminder.last_notification_sent
                    if time_diff.total_seconds() < 300:  # Less than 5 minutes ago
                        continue
                
                # Send notification
                success = send_reminder_notification(reminder.user, reminder)
                
                if success:
                    # Update last notification sent time
                    reminder.last_notification_sent = current_time
                    
                    # Calculate next reminder time
                    next_time = reminder.next_due_time
                    if next_time:
                        reminder.next_reminder = next_time
                    
                    reminder.save()
                    notifications_sent += 1
                    
                    logger.info(f"Reminder notification sent to {reminder.user.username} for {reminder.medicine_name}")
                
            except Exception as e:
                logger.error(f"Error sending reminder notification for {reminder.id}: {str(e)}")
        
        logger.info(f"Sent {notifications_sent} reminder notifications")
        return f"Sent {notifications_sent} notifications"
        
    except Exception as e:
        logger.error(f"Error in send_reminder_notifications task: {str(e)}")
        raise

@shared_task
def cleanup_old_scans():
    """
    Clean up old medicine scans to save storage space
    Run this task daily
    """
    try:
        # Delete scans older than 1 year that are not favorites
        cutoff_date = timezone.now() - timedelta(days=365)
        
        old_scans = MedicineScan.objects.filter(
            created_at__lt=cutoff_date,
            is_favorite=False
        )
        
        deleted_count = 0
        
        for scan in old_scans:
            try:
                # Delete associated image file
                if scan.image:
                    scan.image.delete(save=False)
                
                scan.delete()
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Error deleting scan {scan.id}: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} old scans")
        return f"Deleted {deleted_count} old scans"
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_scans task: {str(e)}")
        raise

@shared_task
def generate_health_insights():
    """
    Generate health insights for users based on their medicine history
    Run this task daily
    """
    try:
        users = User.objects.filter(is_active=True)
        insights_generated = 0
        
        for user in users:
            try:
                # Get user's active reminders
                active_reminders = Reminder.objects.filter(user=user, is_active=True)
                
                if not active_reminders.exists():
                    continue
                
                # Check for medicine interactions
                medicine_names = [r.medicine_name for r in active_reminders]
                interactions = check_medicine_interactions(medicine_names)
                
                if interactions:
                    for interaction in interactions:
                        # Create health insight for interaction
                        HealthInsight.objects.get_or_create(
                            user=user,
                            insight_type='interaction',
                            title=f"Medicine Interaction Alert",
                            defaults={
                                'description': f"Potential interaction between {interaction['medicine1']} and {interaction['medicine2']}: {interaction['description']}",
                                'priority': 'high' if interaction['severity'] == 'major' else 'medium'
                            }
                        )
                        insights_generated += 1
                
                # Check adherence rate
                adherence_insights = generate_adherence_insights(user)
                insights_generated += len(adherence_insights)
                
                # Check for missed doses
                missed_dose_insights = generate_missed_dose_insights(user)
                insights_generated += len(missed_dose_insights)
                
            except Exception as e:
                logger.error(f"Error generating insights for user {user.id}: {str(e)}")
        
        logger.info(f"Generated {insights_generated} health insights")
        return f"Generated {insights_generated} insights"
        
    except Exception as e:
        logger.error(f"Error in generate_health_insights task: {str(e)}")
        raise

def generate_adherence_insights(user):
    """Generate adherence-related insights for a user"""
    insights = []
    
    try:
        # Get reminders from last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_reminders = Reminder.objects.filter(
            user=user,
            is_active=True,
            created_at__gte=week_ago
        )
        
        for reminder in recent_reminders:
            # Calculate expected vs actual doses
            days_active = min(7, (timezone.now().date() - reminder.start_date).days)
            expected_doses = days_active * len(reminder.reminder_times)
            actual_doses = reminder.times_taken
            
            if expected_doses > 0:
                adherence_rate = (actual_doses / expected_doses) * 100
                
                if adherence_rate < 70:  # Poor adherence
                    insight, created = HealthInsight.objects.get_or_create(
                        user=user,
                        insight_type='adherence',
                        title=f"Low Adherence: {reminder.medicine_name}",
                        defaults={
                            'description': f"Your adherence rate for {reminder.medicine_name} is {adherence_rate:.1f}%. Consider setting more frequent reminders or adjusting your schedule.",
                            'priority': 'medium'
                        }
                    )
                    if created:
                        insights.append(insight)
                
                elif adherence_rate >= 90:  # Excellent adherence
                    insight, created = HealthInsight.objects.get_or_create(
                        user=user,
                        insight_type='adherence',
                        title=f"Excellent Adherence: {reminder.medicine_name}",
                        defaults={
                            'description': f"Great job! Your adherence rate for {reminder.medicine_name} is {adherence_rate:.1f}%. Keep up the good work!",
                            'priority': 'low'
                        }
                    )
                    if created:
                        insights.append(insight)
    
    except Exception as e:
        logger.error(f"Error generating adherence insights: {str(e)}")
    
    return insights

def generate_missed_dose_insights(user):
    """Generate insights about missed doses"""
    insights = []
    
    try:
        today = timezone.now().date()
        
        # Check reminders that should have been taken today but weren't
        todays_reminders = Reminder.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=today
        )
        
        missed_count = 0
        
        for reminder in todays_reminders:
            # Check if any doses were missed today
            if reminder.last_taken:
                last_taken_date = reminder.last_taken.date()
                if last_taken_date < today:
                    missed_count += 1
            else:
                # Never taken
                missed_count += 1
        
        if missed_count > 0:
            insight, created = HealthInsight.objects.get_or_create(
                user=user,
                insight_type='missed_dose',
                title=f"Missed Doses Today",
                defaults={
                    'description': f"You have {missed_count} missed dose(s) today. Please take your medicines as prescribed and consider adjusting your reminder times.",
                    'priority': 'high'
                }
            )
            if created:
                insights.append(insight)
    
    except Exception as e:
        logger.error(f"Error generating missed dose insights: {str(e)}")
    
    return insights

@shared_task
def send_weekly_report():
    """
    Send weekly health report to users
    Run this task weekly (every Sunday)
    """
    try:
        users_with_reminders = User.objects.filter(
            reminder__isnull=False,
            userprofile__notifications_enabled=True,
            userprofile__email_reminders=True
        ).distinct()
        
        reports_sent = 0
        
        for user in users_with_reminders:
            try:
                # Generate weekly report
                report_data = generate_weekly_report_data(user)
                
                if report_data:
                    # Send email report
                    send_weekly_report_email(user, report_data)
                    reports_sent += 1
                    
            except Exception as e:
                logger.error(f"Error sending weekly report to user {user.id}: {str(e)}")
        
        logger.info(f"Sent {reports_sent} weekly reports")
        return f"Sent {reports_sent} weekly reports"
        
    except Exception as e:
        logger.error(f"Error in send_weekly_report task: {str(e)}")
        raise

def generate_weekly_report_data(user):
    """Generate weekly report data for a user"""
    try:
        week_ago = timezone.now() - timedelta(days=7)
        
        # Get user's reminders and scans from last week
        reminders = Reminder.objects.filter(user=user, is_active=True)
        scans = MedicineScan.objects.filter(user=user, created_at__gte=week_ago)
        
        # Calculate statistics
        total_expected_doses = 0
        total_taken_doses = 0
        
        for reminder in reminders:
            days_in_period = min(7, (timezone.now().date() - max(reminder.start_date, week_ago.date())).days)
            expected = days_in_period * len(reminder.reminder_times)
            total_expected_doses += expected
            
            # Count doses taken in the last week
            if reminder.last_taken and reminder.last_taken >= week_ago:
                total_taken_doses += reminder.times_taken
        
        adherence_rate = (total_taken_doses / max(total_expected_doses, 1)) * 100
        
        report_data = {
            'week_period': f"{week_ago.strftime('%B %d')} - {timezone.now().strftime('%B %d, %Y')}",
            'total_reminders': reminders.count(),
            'total_scans': scans.count(),
            'adherence_rate': round(adherence_rate, 1),
            'medicines_scanned': list(scans.values_list('medicine_name', flat=True).distinct()),
            'active_medicines': list(reminders.values_list('medicine_name', flat=True)),
        }
        
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating weekly report data: {str(e)}")
        return None

def send_weekly_report_email(user, report_data):
    """Send weekly report email to user"""
    try:
        subject = "Your Weekly MediScan Health Report"
        
        message = f"""
Hi {user.first_name or user.username},

Here's your weekly health summary for {report_data['week_period']}:

📊 ADHERENCE SUMMARY
• Adherence Rate: {report_data['adherence_rate']}%
• Active Medicines: {report_data['total_reminders']}
• Medicine Scans: {report_data['total_scans']}

💊 ACTIVE MEDICINES
{chr(10).join('• ' + med for med in report_data['active_medicines'])}

📱 RECENT SCANS
{chr(10).join('• ' + med for med in report_data['medicines_scanned']) if report_data['medicines_scanned'] else '• No scans this week'}

Keep up the great work managing your health! 

Best regards,
The MediScan Pro Team

---
Visit your dashboard: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Weekly report sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Error sending weekly report email: {str(e)}")
        raise

@shared_task
def update_reminder_schedules():
    """
    Update next reminder times for all active reminders
    Run this task every hour
    """
    try:
        active_reminders = Reminder.objects.filter(is_active=True)
        updated_count = 0
        
        for reminder in active_reminders:
            try:
                next_time = reminder.next_due_time
                if next_time and next_time != reminder.next_reminder:
                    reminder.next_reminder = next_time
                    reminder.save(update_fields=['next_reminder'])
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating reminder schedule for {reminder.id}: {str(e)}")
        
        logger.info(f"Updated {updated_count} reminder schedules")
        return f"Updated {updated_count} schedules"
        
    except Exception as e:
        logger.error(f"Error in update_reminder_schedules task: {str(e)}")
        raise

@shared_task
def backup_user_data():
    """
    Create backup of user data
    Run this task daily
    """
    try:
        from django.core.management import call_command
        from django.conf import settings
        import os
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'mediscan_backup_{timestamp}.json')
        
        # Create database backup
        with open(backup_file, 'w') as f:
            call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)
        
        logger.info(f"Database backup created: {backup_file}")
        
        # Clean up old backups (keep only last 30 days)
        cutoff_date = timezone.now() - timedelta(days=30)
        for filename in os.listdir(backup_dir):
            if filename.startswith('mediscan_backup_'):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_date.replace(tzinfo=None):
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {filename}")
        
        return f"Backup created successfully: {backup_file}"
        
    except Exception as e:
        logger.error(f"Error in backup_user_data task: {str(e)}")
        raise

@shared_task
def process_medicine_image_async(scan_id):
    """
    Process medicine image asynchronously
    Called when a new scan is uploaded
    """
    try:
        from .utils import process_medicine_image, get_medicine_info
        
        scan = MedicineScan.objects.get(id=scan_id)
        
        # Process the image
        result = process_medicine_image(scan.image)
        
        if result['success']:
            # Update scan with results
            scan.medicine_name = result['medicine_name']
            scan.confidence_score = result['confidence']
            scan.medicine_info = result['medicine_info']
            scan.save()
            
            logger.info(f"Processed scan {scan_id}: {result['medicine_name']} ({result['confidence']:.1%})")
            
            # Generate health insights if confidence is high
            if result['confidence'] > 0.8:
                generate_scan_insights.delay(scan.user.id, scan.id)
        
        else:
            logger.error(f"Failed to process scan {scan_id}: {result.get('error', 'Unknown error')}")
        
        return f"Processed scan {scan_id}"
        
    except MedicineScan.DoesNotExist:
        logger.error(f"Scan {scan_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error processing scan {scan_id}: {str(e)}")
        raise

@shared_task
def generate_scan_insights(user_id, scan_id):
    """
    Generate insights based on a new medicine scan
    """
    try:
        user = User.objects.get(id=user_id)
        scan = MedicineScan.objects.get(id=scan_id)
        
        # Check if user already has this medicine in reminders
        existing_reminder = Reminder.objects.filter(
            user=user,
            medicine_name__icontains=scan.medicine_name,
            is_active=True
        ).first()
        
        if not existing_reminder:
            # Suggest creating a reminder
            HealthInsight.objects.get_or_create(
                user=user,
                insight_type='reminder_suggestion',
                title=f"Set Reminder for {scan.medicine_name}",
                defaults={
                    'description': f"You scanned {scan.medicine_name}. Would you like to set up a reminder to take this medicine regularly?",
                    'priority': 'medium'
                }
            )
        
        # Check for potential interactions with existing medicines
        user_medicines = list(Reminder.objects.filter(
            user=user,
            is_active=True
        ).values_list('medicine_name', flat=True))
        
        user_medicines.append(scan.medicine_name)
        interactions = check_medicine_interactions(user_medicines)
        
        if interactions:
            for interaction in interactions:
                if scan.medicine_name.lower() in [interaction['medicine1'].lower(), interaction['medicine2'].lower()]:
                    HealthInsight.objects.get_or_create(
                        user=user,
                        insight_type='interaction',
                        title=f"Interaction Alert: {scan.medicine_name}",
                        defaults={
                            'description': f"The scanned medicine {scan.medicine_name} may interact with {interaction['medicine1'] if interaction['medicine2'].lower() == scan.medicine_name.lower() else interaction['medicine2']}: {interaction['description']}",
                            'priority': 'high'
                        }
                    )
        
        logger.info(f"Generated insights for scan {scan_id}")
        return f"Generated insights for scan {scan_id}"
        
    except (User.DoesNotExist, MedicineScan.DoesNotExist):
        logger.error(f"User {user_id} or scan {scan_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error generating scan insights: {str(e)}")
        raise

@shared_task
def send_medication_refill_reminders():
    """
    Send reminders to users when their medication might be running low
    Run this task daily
    """
    try:
        # Get reminders that have been active for a while
        reminders = Reminder.objects.filter(
            is_active=True,
            duration='1_month',  # Focus on monthly prescriptions
            start_date__lte=timezone.now().date() - timedelta(days=25)  # 25 days old
        )
        
        notifications_sent = 0
        
        for reminder in reminders:
            # Check if we've already sent a refill reminder recently
            recent_insight = HealthInsight.objects.filter(
                user=reminder.user,
                insight_type='refill_reminder',
                title__icontains=reminder.medicine_name,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).exists()
            
            if not recent_insight:
                HealthInsight.objects.create(
                    user=reminder.user,
                    insight_type='refill_reminder',
                    title=f"Refill Reminder: {reminder.medicine_name}",
                    description=f"Your {reminder.medicine_name} prescription may be running low. Consider refilling it soon to avoid missing doses.",
                    priority='medium'
                )
                
                # Send email notification if enabled
                if (reminder.user.userprofile.email_reminders and 
                    reminder.user.userprofile.notifications_enabled):
                    send_refill_reminder_email.delay(reminder.user.id, reminder.medicine_name)
                
                notifications_sent += 1
        
        logger.info(f"Sent {notifications_sent} refill reminders")
        return f"Sent {notifications_sent} refill reminders"
        
    except Exception as e:
        logger.error(f"Error in send_medication_refill_reminders task: {str(e)}")
        raise

@shared_task
def send_refill_reminder_email(user_id, medicine_name):
    """Send refill reminder email to user"""
    try:
        user = User.objects.get(id=user_id)
        
        subject = f"Refill Reminder: {medicine_name}"
        message = f"""
Hi {user.first_name or user.username},

This is a friendly reminder that your {medicine_name} prescription may be running low.

To ensure you don't miss any doses, please consider:
• Checking your current medicine supply
• Contacting your doctor for a new prescription
• Visiting your pharmacy to refill

Staying consistent with your medication is important for your health.

Best regards,
MediScan Pro Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Refill reminder email sent to {user.email} for {medicine_name}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for refill reminder")
    except Exception as e:
        logger.error(f"Error sending refill reminder email: {str(e)}")
        raise

@shared_task
def analyze_user_medicine_patterns():
    """
    Analyze user medicine patterns and generate insights
    Run this task weekly
    """
    try:
        users = User.objects.filter(is_active=True)
        insights_generated = 0
        
        for user in users:
            try:
                # Analyze scanning patterns
                scans = MedicineScan.objects.filter(user=user)
                
                if scans.count() >= 5:  # Minimum scans for analysis
                    # Find most scanned medicines
                    medicine_counts = {}
                    for scan in scans:
                        medicine_counts[scan.medicine_name] = medicine_counts.get(scan.medicine_name, 0) + 1
                    
                    # Sort by frequency
                    frequent_medicines = sorted(medicine_counts.items(), key=lambda x: x[1], reverse=True)
                    
                    # Check if user has reminders for frequently scanned medicines
                    for medicine_name, count in frequent_medicines[:3]:  # Top 3
                        has_reminder = Reminder.objects.filter(
                            user=user,
                            medicine_name__icontains=medicine_name,
                            is_active=True
                        ).exists()
                        
                        if not has_reminder and count >= 3:
                            HealthInsight.objects.get_or_create(
                                user=user,
                                insight_type='pattern_analysis',
                                title=f"Frequent Scan Pattern: {medicine_name}",
                                defaults={
                                    'description': f"You've scanned {medicine_name} {count} times. Consider setting up a reminder to help with regular dosing.",
                                    'priority': 'low'
                                }
                            )
                            insights_generated += 1
                
                # Analyze reminder patterns
                reminders = Reminder.objects.filter(user=user, is_active=True)
                
                if reminders.count() > 5:  # Many active reminders
                    HealthInsight.objects.get_or_create(
                        user=user,
                        insight_type='pattern_analysis',
                        title="Multiple Active Reminders",
                        defaults={
                            'description': f"You have {reminders.count()} active reminders. Consider reviewing and organizing your medication schedule for better management.",
                            'priority': 'low'
                        }
                    )
                    insights_generated += 1
                
            except Exception as e:
                logger.error(f"Error analyzing patterns for user {user.id}: {str(e)}")
        
        logger.info(f"Generated {insights_generated} pattern analysis insights")
        return f"Generated {insights_generated} pattern insights"
        
    except Exception as e:
        logger.error(f"Error in analyze_user_medicine_patterns task: {str(e)}")
        raise

@shared_task
def cleanup_expired_insights():
    """
    Clean up old and read health insights
    Run this task weekly
    """
    try:
        # Delete read insights older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_insights = HealthInsight.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        )
        
        deleted_count = old_insights.count()
        old_insights.delete()
        
        # Delete unread low priority insights older than 7 days
        week_ago = timezone.now() - timedelta(days=7)
        old_low_priority = HealthInsight.objects.filter(
            priority='low',
            created_at__lt=week_ago
        )
        
        deleted_low_priority = old_low_priority.count()
        old_low_priority.delete()
        
        total_deleted = deleted_count + deleted_low_priority
        
        logger.info(f"Cleaned up {total_deleted} old insights")
        return f"Cleaned up {total_deleted} insights"
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_insights task: {str(e)}")
        raise