from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'scanner'

urlpatterns = [
    # Authentication URLs
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),  # Redirects to dashboard on success
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # Main app URLs
    path('', views.upload_image, name='upload_image'),  # Homepage for image upload
    path('scan/', views.upload_image, name='scan'),  # Alias for image upload
    path('results/', views.results, name='results'),  # Scan results page
    path('history/', views.history, name='history'),  # User scan history
    
    # Medicine management
    path('medicine/<int:scan_id>/', views.medicine_detail, name='medicine_detail'),  # Medicine details
    path('medicine/<int:scan_id>/delete/', views.delete_scan, name='delete_scan'),  # Delete scan
    path('medicine/<int:scan_id>/favorite/', views.favorite_medicine, name='favorite_medicine'),  # Toggle favorite
    path('medicine/<int:scan_id>/share/', views.share_medicine, name='share_medicine'),  # Share medicine
    path('medicine/<int:scan_id>/download/', views.download_medicine_info, name='download_medicine_info'),  # Download medicine info
    
    # Reminder management
    path('reminders/', views.reminders, name='reminders'),  # List all reminders
    path('reminders/add/', views.add_reminder, name='add_reminder'),  # Add new reminder
    path('reminders/<int:reminder_id>/', views.get_reminder, name='get_reminder'),  # Get reminder details
    path('reminders/<int:reminder_id>/edit/', views.edit_reminder, name='edit_reminder'),  # Edit reminder
    path('reminders/<int:reminder_id>/delete/', views.delete_reminder, name='delete_reminder'),  # Delete reminder
    path('reminders/<int:reminder_id>/complete/', views.mark_reminder_complete, name='mark_reminder_complete'),  # Mark reminder complete
    path('reminders/<int:reminder_id>/snooze/', views.snooze_reminder, name='snooze_reminder'),  # Snooze reminder
    path('reminders/<int:reminder_id>/pause/', views.pause_reminder, name='pause_reminder'),  # Pause reminder
    path('reminders/<int:reminder_id>/resume/', views.resume_reminder, name='resume_reminder'),  # Resume reminder
    
    # User profile and settings
    path('profile/', views.user_profile, name='user_profile'),  # User profile page
    path('settings/', views.user_settings, name='user_settings'),  # User settings page
    path('export-data/', views.export_user_data, name='export_user_data'),  # Export user data
    
    # Health insights and analytics
    path('insights/', views.health_insights, name='health_insights'),  # Health insights page
    path('interactions/', views.medicine_interactions, name='medicine_interactions'),  # Medicine interactions
    
    # API endpoints
    path('api/search/', views.search_medicines, name='search_medicines'),  # Search medicines API
    path('api/suggestions/', views.medicine_suggestions, name='medicine_suggestions'),  # Medicine suggestions API
    path('api/reminder-stats/', views.reminder_stats, name='reminder_stats'),  # Reminder statistics API
    
    # PWA support
    path('manifest.json', views.manifest, name='manifest'),  # PWA manifest
    path('sw.js', views.service_worker, name='service_worker'),  # Service worker
    path('offline/', views.offline, name='offline'),  # Offline page
    
    # Additional utility URLs
    path('dashboard/', views.dashboard, name='dashboard'),  # User dashboard (login redirect target)
    path('favorites/', views.favorites, name='favorites'),  # Favorite medicines
    path('calendar/', views.reminder_calendar, name='reminder_calendar'),  # Reminder calendar
    path('reports/', views.medicine_reports, name='medicine_reports'),  # Medicine reports
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)