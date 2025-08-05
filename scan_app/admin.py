from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import MedicineScan, Reminder, UserProfile, MedicineInteraction, HealthInsight

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'notifications_enabled', 'email_reminders', 'created_at']
    list_filter = ['notifications_enabled', 'email_reminders', 'sms_reminders', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'profile_picture')
        }),
        ('Notification Settings', {
            'fields': ('notifications_enabled', 'email_reminders', 'sms_reminders', 'reminder_sound')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MedicineScan)
class MedicineScanAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'user', 'confidence_percentage', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'created_at', 'confidence_score']
    search_fields = ['medicine_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'confidence_percentage', 'image_preview']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('user', 'medicine_name', 'confidence_score', 'confidence_percentage')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Medicine Details', {
            'fields': ('medicine_info', 'is_favorite')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def confidence_percentage(self, obj):
        return f"{obj.confidence_percentage}%"
    confidence_percentage.short_description = 'Confidence'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    actions = ['mark_as_favorite', 'remove_from_favorites']
    
    def mark_as_favorite(self, request, queryset):
        queryset.update(is_favorite=True)
        self.message_user(request, f"{queryset.count()} scans marked as favorite.")
    mark_as_favorite.short_description = "Mark selected scans as favorite"
    
    def remove_from_favorites(self, request, queryset):
        queryset.update(is_favorite=False)
        self.message_user(request, f"{queryset.count()} scans removed from favorites.")
    remove_from_favorites.short_description = "Remove selected scans from favorites"

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'user', 'frequency', 'is_active', 'next_due', 'times_taken', 'created_at']
    list_filter = ['frequency', 'is_active', 'duration', 'created_at']
    search_fields = ['medicine_name', 'user__username', 'dosage']
    readonly_fields = ['created_at', 'updated_at', 'next_due', 'adherence_rate']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'medicine_name', 'dosage')
        }),
        ('Schedule', {
            'fields': ('frequency', 'reminder_times', 'start_date', 'end_date', 'duration')
        }),
        ('Status', {
            'fields': ('is_active', 'last_taken', 'next_reminder', 'times_taken')
        }),
        ('Settings', {
            'fields': ('notification_sound', 'notes')
        }),
        ('Statistics', {
            'fields': ('adherence_rate', 'next_due'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def next_due(self, obj):
        next_time = obj.next_due_time
        if next_time:
            return next_time.strftime('%Y-%m-%d %H:%M')
        return "Not scheduled"
    next_due.short_description = 'Next Due'
    
    def adherence_rate(self, obj):
        # Calculate simple adherence rate
        days_since_start = (timezone.now().date() - obj.start_date).days
        if days_since_start == 0:
            return "N/A"
        
        expected_doses = days_since_start * len(obj.reminder_times)
        if expected_doses == 0:
            return "N/A"
        
        rate = (obj.times_taken / expected_doses) * 100
        return f"{rate:.1f}%"
    adherence_rate.short_description = 'Adherence Rate'
    
    actions = ['activate_reminders', 'deactivate_reminders', 'reset_counters']
    
    def activate_reminders(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} reminders activated.")
    activate_reminders.short_description = "Activate selected reminders"
    
    def deactivate_reminders(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} reminders deactivated.")
    deactivate_reminders.short_description = "Deactivate selected reminders"
    
    def reset_counters(self, request, queryset):
        queryset.update(times_taken=0, last_taken=None)
        self.message_user(request, f"Counters reset for {queryset.count()} reminders.")
    reset_counters.short_description = "Reset counters for selected reminders"

@admin.register(MedicineInteraction)
class MedicineInteractionAdmin(admin.ModelAdmin):
    list_display = ['medicine1', 'medicine2', 'interaction_type', 'severity_level', 'created_at']
    list_filter = ['interaction_type', 'severity_level', 'created_at']
    search_fields = ['medicine1', 'medicine2', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Medicines', {
            'fields': ('medicine1', 'medicine2')
        }),
        ('Interaction Details', {
            'fields': ('interaction_type', 'severity_level', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(HealthInsight)
class HealthInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'title', 'priority', 'is_read', 'created_at']
    list_filter = ['insight_type', 'priority', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Insight Details', {
            'fields': ('insight_type', 'title', 'description', 'priority')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} insights marked as read.")
    mark_as_read.short_description = "Mark selected insights as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} insights marked as unread.")
    mark_as_unread.short_description = "Mark selected insights as unread"

# Custom admin site configuration
admin.site.site_header = "MediScan Pro Administration"
admin.site.site_title = "MediScan Pro Admin"
admin.site.index_title = "Welcome to MediScan Pro Administration"

# Add custom admin views for statistics
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg
from django.urls import path

@staff_member_required
def admin_statistics(request):
    """Custom admin view for statistics"""
    from django.contrib.auth.models import User
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(days=30)).count()
    
    # Scan statistics
    total_scans = MedicineScan.objects.count()
    avg_confidence = MedicineScan.objects.aggregate(avg=Avg('confidence_score'))['avg'] or 0
    popular_medicines = MedicineScan.objects.values('medicine_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Reminder statistics
    total_reminders = Reminder.objects.count()
    active_reminders = Reminder.objects.filter(is_active=True).count()
    
    context = {
        'title': 'Statistics Dashboard',
        'total_users': total_users,
        'active_users': active_users,
        'total_scans': total_scans,
        'avg_confidence': round(avg_confidence * 100, 1),
        'popular_medicines': popular_medicines,
        'total_reminders': total_reminders,
        'active_reminders': active_reminders,
    }
    
    return render(request, 'admin/statistics.html', context)

# Add custom URL pattern for statistics
def get_admin_urls():
    return [
        path('statistics/', admin_statistics, name='admin_statistics'),
    ]

# Register custom admin URLs
from django.contrib import admin
original_get_urls = admin.site.get_urls
admin.site.get_urls = lambda: get_admin_urls() + original_get_urls()