import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediscan.settings')

app = Celery('mediscan')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Send reminder notifications every 5 minutes
    'send-reminder-notifications': {
        'task': 'scanner.tasks.send_reminder_notifications',
        'schedule': 300.0,  # 5 minutes
    },
    
    # Update reminder schedules every hour
    'update-reminder-schedules': {
        'task': 'scanner.tasks.update_reminder_schedules',
        'schedule': 3600.0,  # 1 hour
    },
    
    # Generate health insights daily at 9 AM
    'generate-health-insights': {
        'task': 'scanner.tasks.generate_health_insights',
        'schedule': {
            'hour': 9,
            'minute': 0,
        },
    },
    
    # Send weekly reports every Sunday at 8 AM
    'send-weekly-report': {
        'task': 'scanner.tasks.send_weekly_report',
        'schedule': {
            'day_of_week': 0,  # Sunday
            'hour': 8,
            'minute': 0,
        },
    },
    
    # Clean up old scans daily at 2 AM
    'cleanup-old-scans': {
        'task': 'scanner.tasks.cleanup_old_scans',
        'schedule': {
            'hour': 2,
            'minute': 0,
        },
    },
    
    # Backup user data daily at 3 AM
    'backup-user-data': {
        'task': 'scanner.tasks.backup_user_data',
        'schedule': {
            'hour': 3,
            'minute': 0,
        },
    },
    
    # Send refill reminders daily at 10 AM
    'send-refill-reminders': {
        'task': 'scanner.tasks.send_medication_refill_reminders',
        'schedule': {
            'hour': 10,
            'minute': 0,
        },
    },
    
    # Analyze user patterns weekly on Monday at 11 AM
    'analyze-user-patterns': {
        'task': 'scanner.tasks.analyze_user_medicine_patterns',
        'schedule': {
            'day_of_week': 1,  # Monday
            'hour': 11,
            'minute': 0,
        },
    },
    
    # Clean up expired insights weekly on Saturday at 1 AM
    'cleanup-expired-insights': {
        'task': 'scanner.tasks.cleanup_expired_insights',
        'schedule': {
            'day_of_week': 6,  # Saturday
            'hour': 1,
            'minute': 0,
        },
    },
}

# Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'scanner.tasks.send_reminder_notifications': {'queue': 'notifications'},
        'scanner.tasks.process_medicine_image_async': {'queue': 'image_processing'},
        'scanner.tasks.generate_health_insights': {'queue': 'analytics'},
        'scanner.tasks.send_weekly_report': {'queue': 'reports'},
        'scanner.tasks.backup_user_data': {'queue': 'maintenance'},
    },
    
    # Task time limits
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Task retry configuration
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    
    # Timezone
    timezone=settings.TIME_ZONE,
    enable_utc=True,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed successfully'