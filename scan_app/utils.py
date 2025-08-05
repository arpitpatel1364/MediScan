import os
import json
import requests
from PIL import Image
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def process_medicine_image(image_file):
    """
    Process uploaded medicine image using AI/ML service
    This is a mock implementation - replace with actual AI service
    """
    try:
        # Mock medicine database
        mock_medicines = {
            'paracetamol': {
                'name': 'Paracetamol',
                'generic_name': 'Acetaminophen',
                'uses': 'Pain relief, fever reduction',
                'dosage': '500mg-1000mg every 4-6 hours',
                'side_effects': 'Liver damage with overdose, nausea',
                'precautions': 'Do not exceed 4g per day. Avoid alcohol.',
                'mrp': '₹15-25',
                'alternatives': [
                    {'name': 'Crocin', 'price': '₹20'},
                    {'name': 'Dolo 650', 'price': '₹18'},
                    {'name': 'Calpol', 'price': '₹22'}
                ],
                'manufacturer': 'Various',
                'composition': 'Paracetamol 500mg',
                'storage': 'Store below 30°C, keep dry'
            },
            'ibuprofen': {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'uses': 'Pain relief, anti-inflammatory, fever reduction',
                'dosage': '200mg-400mg every 4-6 hours',
                'side_effects': 'Stomach upset, dizziness, headache',
                'precautions': 'Take with food. Avoid in kidney disease.',
                'mrp': '₹25-35',
                'alternatives': [
                    {'name': 'Brufen', 'price': '₹30'},
                    {'name': 'Advil', 'price': '₹35'},
                    {'name': 'Combiflam', 'price': '₹28'}
                ],
                'manufacturer': 'Various',
                'composition': 'Ibuprofen 400mg',
                'storage': 'Store below 25°C'
            },
            'aspirin': {
                'name': 'Aspirin',
                'generic_name': 'Acetylsalicylic acid',
                'uses': 'Pain relief, anti-inflammatory, blood thinner',
                'dosage': '75mg-300mg daily',
                'side_effects': 'Stomach bleeding, allergic reactions',
                'precautions': 'Not for children under 16. Take with food.',
                'mrp': '₹8-15',
                'alternatives': [
                    {'name': 'Disprin', 'price': '₹12'},
                    {'name': 'Ecosprin', 'price': '₹10'},
                    {'name': 'Loprin', 'price': '₹8'}
                ],
                'manufacturer': 'Various',
                'composition': 'Aspirin 325mg',
                'storage': 'Store in cool, dry place'
            }
        }
        
        # Simulate AI processing delay
        import time
        time.sleep(1)
        
        # Mock OCR/Image recognition
        # In reality, this would use computer vision APIs
        detected_text = extract_text_from_image(image_file)
        medicine_name = identify_medicine_from_text(detected_text)
        
        # Get medicine info
        medicine_info = mock_medicines.get(medicine_name.lower(), {
            'name': medicine_name,
            'uses': 'Information not available',
            'dosage': 'Consult doctor',
            'side_effects': 'Consult doctor',
            'precautions': 'Consult doctor',
            'mrp': 'Not available',
            'alternatives': [],
            'manufacturer': 'Unknown',
            'composition': 'Not available',
            'storage': 'Follow package instructions'
        })
        
        # Calculate confidence score
        confidence = calculate_confidence_score(detected_text, medicine_name)
        
        return {
            'success': True,
            'medicine_name': medicine_info['name'],
            'medicine_info': medicine_info,
            'confidence': confidence,
            'detected_text': detected_text
        }
        
    except Exception as e:
        logger.error(f"Error processing medicine image: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'medicine_name': 'Unknown',
            'medicine_info': {},
            'confidence': 0.0
        }

def extract_text_from_image(image_file):
    """
    Extract text from image using OCR
    Mock implementation - replace with actual OCR service
    """
    try:
        # Mock text extraction
        mock_texts = [
            'PARACETAMOL 500MG',
            'IBUPROFEN 400MG',
            'ASPIRIN 325MG',
            'CROCIN ADVANCE',
            'DOLO 650',
            'BRUFEN PLUS'
        ]
        
        # Return random mock text for demo
        import random
        return random.choice(mock_texts)
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

def identify_medicine_from_text(text):
    """
    Identify medicine name from extracted text
    """
    text = text.lower()
    
    # Medicine name mapping
    medicine_keywords = {
        'paracetamol': ['paracetamol', 'crocin', 'dolo', 'calpol', 'tylenol'],
        'ibuprofen': ['ibuprofen', 'brufen', 'advil', 'combiflam'],
        'aspirin': ['aspirin', 'disprin', 'ecosprin', 'loprin'],
    }
    
    for medicine, keywords in medicine_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return medicine.title()
    
    # If no match found, extract the first word that looks like a medicine name
    words = text.split()
    for word in words:
        if len(word) > 3 and word.isalpha():
            return word.title()
    
    return "Unknown Medicine"

def calculate_confidence_score(detected_text, medicine_name):
    """
    Calculate confidence score based on text clarity and medicine match
    """
    if not detected_text or medicine_name == "Unknown Medicine":
        return 0.3
    
    # Simple confidence calculation
    text_length = len(detected_text.strip())
    has_numbers = any(char.isdigit() for char in detected_text)
    has_medicine_keywords = any(keyword in detected_text.lower() 
                               for keyword in ['mg', 'tablet', 'capsule', 'syrup'])
    
    confidence = 0.5  # Base confidence
    
    if text_length > 10:
        confidence += 0.2
    if has_numbers:
        confidence += 0.2
    if has_medicine_keywords:
        confidence += 0.1
    
    return min(confidence, 0.95)  # Cap at 95%

def get_medicine_info(medicine_name):
    """
    Get detailed medicine information from database or API
    """
    # This would typically query a medicine database or API
    # For now, return mock data
    return {
        'name': medicine_name,
        'uses': 'Information not available',
        'dosage': 'Consult doctor',
        'side_effects': 'Consult doctor',
        'precautions': 'Consult doctor',
        'mrp': 'Not available',
        'alternatives': [],
        'manufacturer': 'Unknown',
        'composition': 'Not available'
    }

def send_reminder_notification(user, reminder):
    """
    Send reminder notification to user
    """
    try:
        if user.userprofile.notifications_enabled:
            # Send email notification
            if user.userprofile.email_reminders and user.email:
                send_email_reminder(user, reminder)
            
            # Send SMS notification (implement with SMS service)
            if user.userprofile.sms_reminders and user.userprofile.phone:
                send_sms_reminder(user, reminder)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending reminder notification: {str(e)}")
        return False

def send_email_reminder(user, reminder):
    """
    Send email reminder to user
    """
    try:
        subject = f"Medicine Reminder: {reminder.medicine_name}"
        message = f"""
        Hi {user.first_name or user.username},
        
        This is a reminder to take your medicine:
        
        Medicine: {reminder.medicine_name}
        Dosage: {reminder.dosage}
        Time: {timezone.now().strftime('%I:%M %p')}
        
        Notes: {reminder.notes if reminder.notes else 'None'}
        
        Take care of your health!
        
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
        
        logger.info(f"Email reminder sent to {user.email} for {reminder.medicine_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email reminder: {str(e)}")
        return False

def send_sms_reminder(user, reminder):
    """
    Send SMS reminder to user
    Implement with your preferred SMS service (Twilio, AWS SNS, etc.)
    """
    try:
        # Mock SMS implementation
        # Replace with actual SMS service integration
        phone = user.userprofile.phone
        message = f"MediScan Reminder: Take {reminder.medicine_name} ({reminder.dosage}) now."
        
        # Example with Twilio (uncomment and configure)
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        # client.messages.create(
        #     body=message,
        #     from_=settings.TWILIO_PHONE,
        #     to=phone
        # )
        
        logger.info(f"SMS reminder would be sent to {phone} for {reminder.medicine_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending SMS reminder: {str(e)}")
        return False

def validate_medicine_name(name):
    """
    Validate and normalize medicine name
    """
    if not name or len(name.strip()) < 2:
        return False, "Medicine name must be at least 2 characters long"
    
    # Check for invalid characters
    invalid_chars = ['<', '>', '&', '"', "'"]
    if any(char in name for char in invalid_chars):
        return False, "Medicine name contains invalid characters"
    
    return True, name.strip().title()

def get_medicine_alternatives(medicine_name):
    """
    Get alternative medicines for a given medicine
    """
    # Mock alternatives database
    alternatives_db = {
        'paracetamol': [
            {'name': 'Crocin', 'price': '₹20', 'strength': '500mg'},
            {'name': 'Dolo 650', 'price': '₹18', 'strength': '650mg'},
            {'name': 'Calpol', 'price': '₹22', 'strength': '500mg'}
        ],
        'ibuprofen': [
            {'name': 'Brufen', 'price': '₹30', 'strength': '400mg'},
            {'name': 'Advil', 'price': '₹35', 'strength': '200mg'},
            {'name': 'Combiflam', 'price': '₹28', 'strength': '400mg'}
        ]
    }
    
    return alternatives_db.get(medicine_name.lower(), [])

def calculate_medicine_cost_savings(original_medicine, alternatives):
    """
    Calculate potential cost savings with alternative medicines
    """
    if not alternatives:
        return None
    
    # Extract price from string (₹XX)
    def extract_price(price_str):
        try:
            return float(price_str.replace('₹', '').split('-')[0])
        except:
            return 0
    
    original_price = extract_price(original_medicine.get('mrp', '₹0'))
    if original_price == 0:
        return None
    
    savings = []
    for alt in alternatives:
        alt_price = extract_price(alt.get('price', '₹0'))
        if alt_price > 0 and alt_price < original_price:
            saving = original_price - alt_price
            savings.append({
                'name': alt['name'],
                'original_price': original_price,
                'alternative_price': alt_price,
                'savings': saving,
                'savings_percentage': round((saving / original_price) * 100, 1)
            })
    
    return sorted(savings, key=lambda x: x['savings'], reverse=True)

def generate_medicine_report(user, start_date=None, end_date=None):
    """
    Generate medicine usage report for user
    """
    from .models import MedicineScan, Reminder
    
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now()
    
    # Get user's scans and reminders
    scans = MedicineScan.objects.filter(
        user=user,
        created_at__range=[start_date, end_date]
    )
    
    reminders = Reminder.objects.filter(
        user=user,
        created_at__range=[start_date, end_date]
    )
    
    # Calculate statistics
    total_scans = scans.count()
    unique_medicines = scans.values('medicine_name').distinct().count()
    avg_confidence = scans.aggregate(avg=models.Avg('confidence_score'))['avg'] or 0
    
    # Most scanned medicines
    medicine_counts = {}
    for scan in scans:
        medicine_counts[scan.medicine_name] = medicine_counts.get(scan.medicine_name, 0) + 1
    
    most_scanned = sorted(medicine_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Reminder statistics
    active_reminders = reminders.filter(is_active=True).count()
    completed_reminders = reminders.filter(last_taken__isnull=False).count()
    
    report = {
        'period': {
            'start': start_date,
            'end': end_date,
            'days': (end_date - start_date).days
        },
        'scan_stats': {
            'total_scans': total_scans,
            'unique_medicines': unique_medicines,
            'average_confidence': round(avg_confidence, 1),
            'most_scanned': most_scanned
        },
        'reminder_stats': {
            'active_reminders': active_reminders,
            'completed_reminders': completed_reminders,
            'completion_rate': round((completed_reminders / max(active_reminders, 1)) * 100, 1)
        },
        'generated_at': timezone.now()
    }
    
    return report

def check_medicine_interactions(medicine_list):
    """
    Check for potential interactions between medicines
    """
    # Mock interaction database
    interactions_db = {
        ('aspirin', 'warfarin'): {
            'severity': 'major',
            'description': 'Increased risk of bleeding',
            'recommendation': 'Monitor bleeding time closely'
        },
        ('ibuprofen', 'metformin'): {
            'severity': 'moderate',
            'description': 'May affect kidney function',
            'recommendation': 'Monitor kidney function'
        },
        ('omeprazole', 'clopidogrel'): {
            'severity': 'moderate',
            'description': 'Reduced effectiveness of clopidogrel',
            'recommendation': 'Consider alternative PPI'
        }
    }
    
    interactions = []
    medicine_list = [med.lower() for med in medicine_list]
    
    for i, med1 in enumerate(medicine_list):
        for med2 in medicine_list[i+1:]:
            interaction_key = tuple(sorted([med1, med2]))
            if interaction_key in interactions_db:
                interaction = interactions_db[interaction_key]
                interactions.append({
                    'medicine1': med1.title(),
                    'medicine2': med2.title(),
                    'severity': interaction['severity'],
                    'description': interaction['description'],
                    'recommendation': interaction['recommendation']
                })
    
    return interactions

def optimize_reminder_schedule(user_reminders):
    """
    Optimize reminder schedule to avoid conflicts and improve adherence
    """
    # Group reminders by time
    time_groups = {}
    for reminder in user_reminders:
        for time_str in reminder.reminder_times:
            if time_str not in time_groups:
                time_groups[time_str] = []
            time_groups[time_str].append(reminder)
    
    # Find conflicts (more than 3 medicines at same time)
    conflicts = []
    for time_str, reminders in time_groups.items():
        if len(reminders) > 3:
            conflicts.append({
                'time': time_str,
                'count': len(reminders),
                'medicines': [r.medicine_name for r in reminders]
            })
    
    # Generate optimization suggestions
    suggestions = []
    for conflict in conflicts:
        suggestions.append({
            'type': 'time_conflict',
            'message': f"You have {conflict['count']} medicines scheduled at {conflict['time']}. Consider spacing them out.",
            'affected_medicines': conflict['medicines'],
            'priority': 'medium'
        })
    
    return {
        'conflicts': conflicts,
        'suggestions': suggestions,
        'total_reminders': len(user_reminders),
        'optimization_score': calculate_schedule_score(time_groups)
    }

def calculate_schedule_score(time_groups):
    """
    Calculate a score for how well-optimized the reminder schedule is
    """
    total_reminders = sum(len(reminders) for reminders in time_groups.values())
    if total_reminders == 0:
        return 100
    
    # Penalize time slots with too many reminders
    penalty = 0
    for time_str, reminders in time_groups.items():
        if len(reminders) > 3:
            penalty += (len(reminders) - 3) * 10
        elif len(reminders) > 2:
            penalty += (len(reminders) - 2) * 5
    
    score = max(0, 100 - penalty)
    return round(score, 1)

def export_user_data_json(user):
    """
    Export all user data in JSON format
    """
    from .models import MedicineScan, Reminder, UserProfile
    
    # Get user data
    profile = UserProfile.objects.filter(user=user).first()
    scans = MedicineScan.objects.filter(user=user)
    reminders = Reminder.objects.filter(user=user)
    
    # Build export data
    export_data = {
        'user_info': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
        },
        'profile': {
            'phone': profile.phone if profile else '',
            'notifications_enabled': profile.notifications_enabled if profile else True,
            'email_reminders': profile.email_reminders if profile else True,
            'sms_reminders': profile.sms_reminders if profile else False,
        },
        'scans': [
            {
                'id': scan.id,
                'medicine_name': scan.medicine_name,
                'confidence_score': scan.confidence_score,
                'medicine_info': scan.medicine_info,
                'is_favorite': scan.is_favorite,
                'created_at': scan.created_at.isoformat(),
            }
            for scan in scans
        ],
        'reminders': [
            {
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'reminder_times': reminder.reminder_times,
                'notes': reminder.notes,
                'is_active': reminder.is_active,
                'times_taken': reminder.times_taken,
                'created_at': reminder.created_at.isoformat(),
            }
            for reminder in reminders
        ],
        'export_info': {
            'exported_at': timezone.now().isoformat(),
            'total_scans': scans.count(),
            'total_reminders': reminders.count(),
        }
    }
    
    return export_data

def validate_image_file(image_file):
    """
    Validate uploaded image file
    """
    # Check file size (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return False, "Image file size must be less than 5MB"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return False, "Only JPEG, PNG, and WebP images are allowed"
    
    # Check image dimensions
    try:
        image = Image.open(image_file)
        width, height = image.size
        if width < 100 or height < 100:
            return False, "Image must be at least 100x100 pixels"
        if width > 4000 or height > 4000:
            return False, "Image dimensions must be less than 4000x4000 pixels"
    except Exception:
        return False, "Invalid image file"
    
    return True, "Valid image file"

def compress_image(image_file, max_size_mb=2):
    """
    Compress image if it's too large
    """
    try:
        image = Image.open(image_file)
        
        # Calculate compression ratio
        original_size = image_file.size / (1024 * 1024)  # Size in MB
        if original_size <= max_size_mb:
            return image_file
        
        compression_ratio = max_size_mb / original_size
        new_quality = int(85 * compression_ratio)
        new_quality = max(30, min(85, new_quality))  # Keep quality between 30-85
        
        # Compress image
        from io import BytesIO
        output = BytesIO()
        image.save(output, format='JPEG', quality=new_quality, optimize=True)
        output.seek(0)
        
        return output
        
    except Exception as e:
        logger.error(f"Error compressing image: {str(e)}")
        return image_file