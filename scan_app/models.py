from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    sms_reminders = models.BooleanField(default=False)
    reminder_sound = models.CharField(max_length=50, default='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class MedicineScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='medicine_scans/')
    medicine_name = models.CharField(max_length=255, blank=True)
    confidence_score = models.FloatField(default=0.0)
    medicine_info = models.JSONField(default=dict, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.medicine_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def confidence_percentage(self):
        return round(self.confidence_score * 100, 1)

class Reminder(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once a day'),
        ('twice', 'Twice a day'),
        ('thrice', 'Three times a day'),
        ('four', 'Four times a day'),
        ('custom', 'Custom frequency'),
    ]
    
    DURATION_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('1_week', '1 Week'),
        ('2_weeks', '2 Weeks'),
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('custom', 'Custom duration'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    reminder_times = models.JSONField(default=list)  # Store list of times
    notes = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='ongoing')
    is_active = models.BooleanField(default=True)
    last_taken = models.DateTimeField(null=True, blank=True)
    next_reminder = models.DateTimeField(null=True, blank=True)
    times_taken = models.IntegerField(default=0)
    notification_sound = models.CharField(max_length=50, default='default')
    schedule = models.CharField(max_length=255, blank=True)  # For display purposes
    completion_rate = models.FloatField(default=0.0)  # Percentage of completed reminders
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.medicine_name} - {self.frequency}"

    def save(self, *args, **kwargs):
        # Set end date based on duration
        if self.duration != 'ongoing' and self.duration != 'custom' and not self.end_date:
            duration_map = {
                '1_week': 7,
                '2_weeks': 14,
                '1_month': 30,
                '3_months': 90,
                '6_months': 180,
            }
            if self.duration in duration_map:
                self.end_date = self.start_date + timedelta(days=duration_map[self.duration])
        
        super().save(*args, **kwargs)

    @property
    def is_due_today(self):
        today = timezone.now().date()
        return (self.is_active and 
                self.start_date <= today and 
                (not self.end_date or self.end_date >= today))

    @property
    def next_due_time(self):
        if not self.reminder_times or not self.is_active:
            return None
        
        now = timezone.now()
        today = now.date()
        
        # Check if already taken today
        if self.last_taken and self.last_taken.date() == today:
            # Find next time after last taken
            last_taken_time = self.last_taken.time()
            for time_str in self.reminder_times:
                reminder_time = datetime.strptime(time_str, '%H:%M').time()
                if reminder_time > last_taken_time:
                    return datetime.combine(today, reminder_time)
            # If no more times today, return first time tomorrow
            tomorrow = today + timedelta(days=1)
            first_time = datetime.strptime(self.reminder_times[0], '%H:%M').time()
            return datetime.combine(tomorrow, first_time)
        else:
            # Find next time today
            current_time = now.time()
            for time_str in self.reminder_times:
                reminder_time = datetime.strptime(time_str, '%H:%M').time()
                if reminder_time > current_time:
                    return datetime.combine(today, reminder_time)
            # If no more times today, return first time tomorrow
            tomorrow = today + timedelta(days=1)
            first_time = datetime.strptime(self.reminder_times[0], '%H:%M').time()
            return datetime.combine(tomorrow, first_time)

class MedicineInteraction(models.Model):
    medicine1 = models.CharField(max_length=255)
    medicine2 = models.CharField(max_length=255)
    interaction_type = models.CharField(max_length=50)  # 'major', 'moderate', 'minor'
    description = models.TextField()
    severity_level = models.IntegerField(default=1)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['medicine1', 'medicine2']

    def __str__(self):
        return f"{self.medicine1} + {self.medicine2} ({self.interaction_type})"

class HealthInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insight_type = models.CharField(max_length=50)  # 'adherence', 'interaction', 'frequency'
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, default='medium')  # 'low', 'medium', 'high'
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"