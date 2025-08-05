from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from django.conf import settings
import json
from datetime import datetime, timedelta

# Assuming these are defined in your models.py
from .models import MedicineScan, Reminder, UserProfile
from .forms import CustomUserCreationForm, ReminderForm, UserProfileForm

# Stub for undefined utility functions
def process_medicine_image(image_file):
    # Placeholder: In production, replace with actual AI/ML image processing
    return {
        'medicine_name': 'Sample Medicine',
        'confidence': 0.95,
        'medicine_info': {
            'uses': 'Pain relief',
            'dosage': '500mg every 6 hours',
            'side_effects': 'Nausea, dizziness',
            'mrp': '10 USD',
            'alternatives': ['Paracetamol', 'Ibuprofen']
        }
    }

def get_medicine_info(medicine_name):
    # Placeholder: In production, replace with database or API call
    return {
        'name': medicine_name,
        'uses': 'Pain relief',
        'dosage': '500mg every 6 hours',
        'side_effects': 'Nausea, dizziness',
        'mrp': '10 USD'
    }

def send_reminder_notification(user, reminder):
    # Placeholder: In production, implement actual notification logic
    pass

def classify_medicine_category(medicine_name):
    # Simplified medicine classification
    categories = {
        'Pain Relief': ['paracetamol', 'ibuprofen', 'aspirin', 'diclofenac'],
        'Antibiotics': ['amoxicillin', 'azithromycin', 'ciprofloxacin'],
        'Diabetes': ['metformin', 'glimepiride', 'insulin'],
        'Heart': ['atorvastatin', 'losartan', 'amlodipine'],
        'Stomach': ['omeprazole', 'ranitidine', 'pantoprazole'],
    }
    medicine_lower = medicine_name.lower()
    for category, medicines in categories.items():
        if any(med in medicine_lower for med in medicines):
            return category
    return 'Other'

def check_medicine_interactions(medicines):
    # Simplified interaction checker
    known_interactions = {
        ('aspirin', 'warfarin'): 'Increased bleeding risk',
        ('metformin', 'alcohol'): 'Risk of lactic acidosis',
        ('omeprazole', 'clopidogrel'): 'Reduced effectiveness of clopidogrel',
    }
    interactions = []
    for i, med1 in enumerate(medicines):
        for med2 in medicines[i+1:]:
            interaction_key = tuple(sorted([med1.lower(), med2.lower()]))
            if interaction_key in known_interactions:
                interactions.append({
                    'medicine1': med1,
                    'medicine2': med2,
                    'warning': known_interactions[interaction_key],
                    'severity': 'moderate'
                })
    return interactions

# Authentication Views
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('scanner:login')

class CustomLoginView(LoginView):
    template_name = 'scanner/login.html'  # Consistent template path
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('scanner:dashboard')  # Redirect to dashboard after login

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'scanner/signup.html'
    success_url = reverse_lazy('scanner:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        UserProfile.objects.create(
            user=user,
            phone=form.cleaned_data.get('phone', ''),
            notifications_enabled=True
        )
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response

# Main App Views
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            result = process_medicine_image(image_file)
            
            if request.user.is_authenticated:
                scan = MedicineScan.objects.create(
                    user=request.user,
                    image=image_file,
                    medicine_name=result.get('medicine_name', 'Unknown'),
                    confidence_score=result.get('confidence', 0.0),
                    medicine_info=result.get('medicine_info', {})
                )
                request.session['last_scan_id'] = scan.id
            
            request.session['scan_result'] = {
                'medicine_name': result.get('medicine_name', 'Unknown'),
                'medicine_info': result.get('medicine_info', {}),
                'image_url': image_file.url if hasattr(image_file, 'url') else None,
                'confidence': result.get('confidence', 0.0)
            }
            return redirect('scanner:results')
        except Exception as e:
            messages.error(request, f'Error processing image: {str(e)}')
    
    recent_scans = []
    if request.user.is_authenticated:
        recent_scans = MedicineScan.objects.filter(
            user=request.user
        ).order_by('-created_at')[:3]
    
    context = {'recent_scans': recent_scans}
    return render(request, 'scanner/index.html', context)

def results(request):
    scan_result = request.session.get('scan_result')
    scan_id = request.session.get('last_scan_id')
    
    if not scan_result:
        messages.error(request, 'No scan result found. Please scan a medicine first.')
        return redirect('scanner:upload_image')
    
    context = {
        'medicine_name': scan_result.get('medicine_name', 'Unknown'),
        'medicine_info': scan_result.get('medicine_info', {}),
        'image_url': scan_result.get('image_url'),
        'confidence': scan_result.get('confidence', 0),
        'scan_id': scan_id,
        'scan_date': timezone.now()
    }
    return render(request, 'scanner/results.html', context)

@login_required
def history(request):
    scans = MedicineScan.objects.filter(user=request.user).order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        scans = scans.filter(
            Q(medicine_name__icontains=search_query) |
            Q(medicine_info__uses__icontains=search_query)
        )
    
    date_filter = request.GET.get('filter', 'all')
    if date_filter == 'today':
        scans = scans.filter(created_at__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        scans = scans.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        scans = scans.filter(created_at__gte=month_ago)
    
    paginator = Paginator(scans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'scans': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'date_filter': date_filter,
    }
    return render(request, 'scanner/history.html', context)

# Medicine Management
@login_required
def medicine_detail(request, scan_id):
    scan = get_object_or_404(MedicineScan, id=scan_id, user=request.user)
    context = {
        'scan': scan,
        'medicine_name': scan.medicine_name,
        'medicine_info': scan.medicine_info,
        'image_url': scan.image.url,
        'confidence': scan.confidence_score,
        'scan_date': scan.created_at,
    }
    return render(request, 'scanner/medicine_detail.html', context)

@login_required
def delete_scan(request, scan_id):
    if request.method == 'POST':  # Changed to POST for consistency with other AJAX views
        try:
            scan = get_object_or_404(MedicineScan, id=scan_id, user=request.user)
            scan.delete()
            messages.success(request, 'Scan deleted successfully!')
            return JsonResponse({'success': True, 'message': 'Scan deleted successfully!'})
        except Exception as e:
            messages.error(request, f'Error deleting scan: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error deleting scan: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def favorite_medicine(request, scan_id):
    if request.method == 'POST':
        try:
            scan = get_object_or_404(MedicineScan, id=scan_id, user=request.user)
            scan.is_favorite = not scan.is_favorite
            scan.save()
            status = 'added to' if scan.is_favorite else 'removed from'
            messages.success(request, f'Medicine {status} favorites!')
            return JsonResponse({
                'success': True,
                'message': f'Medicine {status} favorites!',
                'is_favorite': scan.is_favorite
            })
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def share_medicine(request, scan_id):
    if request.method == 'POST':
        try:
            scan = get_object_or_404(MedicineScan, id=scan_id, user=request.user)
            share_url = request.build_absolute_uri(reverse_lazy('scanner:medicine_detail', args=[scan_id]))
            messages.success(request, 'Medicine share URL generated!')
            return JsonResponse({
                'success': True,
                'share_url': share_url,
                'medicine_name': scan.medicine_name
            })
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def download_medicine_info(request, scan_id):
    try:
        scan = get_object_or_404(MedicineScan, id=scan_id, user=request.user)
        content = f"""Medicine Information - {scan.medicine_name}
Generated by MediScan Pro

Medicine Name: {scan.medicine_name}
Uses: {scan.medicine_info.get('uses', 'Not available')}
Dosage: {scan.medicine_info.get('dosage', 'Consult doctor')}
Side Effects: {scan.medicine_info.get('side_effects', 'Consult doctor')}
MRP: {scan.medicine_info.get('mrp', 'Not available')}

Scan Date: {scan.created_at.strftime('%B %d, %Y at %I:%M %p')}
Confidence: {scan.confidence_score}%

Alternatives:
"""
        alternatives = scan.medicine_info.get('alternatives', [])
        content += "\n".join([f"- {alt.get('name', alt)}" if isinstance(alt, dict) else f"- {alt}" for alt in alternatives]) or "None found"
        content += f"""

Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

Disclaimer: This information is for educational purposes only. 
Always consult with a healthcare professional before taking any medication.
"""
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{scan.medicine_name}_info.txt"'
        return response
    except Exception as e:
        messages.error(request, f'Error generating download: {str(e)}')
        return JsonResponse({'success': False, 'message': f'Error generating download: {str(e)}'}, status=400)

# Reminder Management
@login_required
def reminders(request):
    user_reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')
    today = timezone.now().date()
    todays_reminders = user_reminders.filter(next_reminder__date=today, is_active=True).order_by('next_reminder')
    active_reminders = user_reminders.filter(is_active=True)
    completed_today = user_reminders.filter(last_taken__date=today).count()
    streak_days = calculate_reminder_streak(request.user)

    for reminder in user_reminders:
        times_str = ', '.join(reminder.reminder_times) if reminder.reminder_times else 'Once daily'
        reminder.schedule = f"{times_str} ({reminder.frequency})"
        total_possible = 30
        reminder.completion_rate = min(100, (reminder.times_taken / total_possible) * 100) if total_possible > 0 else 0

    context = {
        'reminders': user_reminders,
        'todays_reminders': todays_reminders,
        'active_reminders': active_reminders,
        'completed_today': completed_today,
        'streak_days': streak_days,
        'current_date': timezone.now(),
    }
    return render(request, 'scanner/reminders.html', context)

@login_required
def add_reminder(request):
    if request.method == 'POST':
        try:
            data = {
                'medicine_name': request.POST.get('medicine_name'),
                'dosage': request.POST.get('dosage'),
                'frequency': request.POST.get('frequency', 'once'),
                'notes': request.POST.get('notes', ''),
                'start_date': request.POST.get('start_date'),
                'duration': request.POST.get('duration', 'ongoing'),
                'sound': request.POST.get('sound', 'default'),
            }
            times = []
            frequency = data['frequency']
            if frequency == 'once':
                times = [request.POST.get('time_1', '08:00')]
            elif frequency == 'twice':
                times = [request.POST.get('time_1', '08:00'), request.POST.get('time_2', '20:00')]
            elif frequency == 'thrice':
                times = [request.POST.get('time_1', '08:00'), request.POST.get('time_2', '14:00'), request.POST.get('time_3', '20:00')]
            elif frequency == 'four':
                times = [request.POST.get('time_1', '08:00'), request.POST.get('time_2', '12:00'), 
                        request.POST.get('time_3', '16:00'), request.POST.get('time_4', '20:00')]
            
            reminder = Reminder.objects.create(
                user=request.user,
                medicine_name=data['medicine_name'],
                dosage=data['dosage'],
                frequency=frequency,
                reminder_times=times,
                notes=data['notes'],
                start_date=data['start_date'],
                duration=data['duration'],
                notification_sound=data['sound'],
                is_active=True
            )
            messages.success(request, 'Reminder created successfully!')
            return JsonResponse({
                'success': True,
                'message': 'Reminder created successfully!',
                'redirect': reverse_lazy('scanner:reminders')
            })
        except Exception as e:
            messages.error(request, f'Error creating reminder: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error creating reminder: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def edit_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        try:
            reminder.medicine_name = request.POST.get('medicine_name')
            reminder.dosage = request.POST.get('dosage')
            reminder.frequency = request.POST.get('frequency')
            reminder.notes = request.POST.get('notes', '')
            reminder.save()
            messages.success(request, 'Reminder updated successfully!')
            return JsonResponse({'success': True, 'message': 'Reminder updated successfully!'})
        except Exception as e:
            messages.error(request, f'Error updating reminder: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error updating reminder: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def delete_reminder(request, reminder_id):
    if request.method == 'POST':  # Changed to POST for consistency
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            reminder.delete()
            messages.success(request, 'Reminder deleted successfully!')
            return JsonResponse({'success': True, 'message': 'Reminder deleted successfully!'})
        except Exception as e:
            messages.error(request, f'Error deleting reminder: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error deleting reminder: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def get_reminder(request, reminder_id):
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
        data = {
            'medicine_name': reminder.medicine_name,
            'dosage': reminder.dosage,
            'frequency': reminder.frequency,
            'notes': reminder.notes,
            'reminder_times': reminder.reminder_times,
            'start_date': reminder.start_date.isoformat() if reminder.start_date else '',
            'duration': reminder.duration,
            'notification_sound': reminder.notification_sound,
        }
        return JsonResponse(data)
    except Exception as e:
        messages.error(request, f'Error retrieving reminder: {str(e)}')
        return JsonResponse({'error': str(e)}, status=404)

@login_required
def mark_reminder_complete(request, reminder_id):
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            reminder.last_taken = timezone.now()
            reminder.times_taken += 1
            reminder.save()
            messages.success(request, 'Reminder marked as taken!')
            return JsonResponse({'success': True, 'message': 'Reminder marked as taken!'})
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def snooze_reminder(request, reminder_id):
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            data = json.loads(request.body)
            minutes = data.get('minutes', 15)
            reminder.next_reminder = timezone.now() + timedelta(minutes=minutes)
            reminder.save()
            messages.success(request, f'Reminder snoozed for {minutes} minutes')
            return JsonResponse({'success': True, 'message': f'Reminder snoozed for {minutes} minutes'})
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def pause_reminder(request, reminder_id):
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            reminder.is_active = False
            reminder.save()
            messages.success(request, 'Reminder paused')
            return JsonResponse({'success': True, 'message': 'Reminder paused'})
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def resume_reminder(request, reminder_id):
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            reminder.is_active = True
            reminder.save()
            messages.success(request, 'Reminder resumed')
            return JsonResponse({'success': True, 'message': 'Reminder resumed'})
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

# User Profile and Settings
@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('scanner:user_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    total_scans = MedicineScan.objects.filter(user=request.user).count()
    total_reminders = Reminder.objects.filter(user=request.user).count()
    active_reminders = Reminder.objects.filter(user=request.user, is_active=True).count()
    
    context = {
        'form': form,
        'profile': profile,
        'total_scans': total_scans,
        'total_reminders': total_reminders,
        'active_reminders': active_reminders,
    }
    return render(request, 'scanner/profile.html', context)

@login_required
def user_settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
        profile.email_reminders = request.POST.get('email_reminders') == 'on'
        profile.sms_reminders = request.POST.get('sms_reminders') == 'on'
        profile.reminder_sound = request.POST.get('reminder_sound', 'default')
        profile.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('scanner:user_settings')
    
    context = {'profile': profile}
    return render(request, 'scanner/settings.html', context)

@login_required
def export_user_data(request):
    scans = MedicineScan.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)
    data = {
        'user_info': {
            'username': request.user.username,
            'email': request.user.email,
            'date_joined': request.user.date_joined.isoformat(),
        },
        'scans': [
            {
                'medicine_name': scan.medicine_name,
                'scan_date': scan.created_at.isoformat(),
                'confidence': scan.confidence_score,
                'medicine_info': scan.medicine_info,
            }
            for scan in scans
        ],
        'reminders': [
            {
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'frequency': reminder.frequency,
                'created_date': reminder.created_at.isoformat(),
                'is_active': reminder.is_active,
            }
            for reminder in reminders
        ]
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="mediscan_data_{request.user.username}.json"'
    return response

# Health Insights
@login_required
def health_insights(request):
    scans = MedicineScan.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)
    
    total_medicines = scans.count()
    unique_medicines = scans.values('medicine_name').distinct().count()
    avg_confidence = scans.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
    
    medicine_categories = {}
    for scan in scans:
        category = classify_medicine_category(scan.medicine_name)
        medicine_categories[category] = medicine_categories.get(category, 0) + 1
    
    active_reminders_count = reminders.filter(is_active=True).count()
    completed_today = reminders.filter(last_taken__date=timezone.now().date()).count()
    adherence_rate = (completed_today / active_reminders_count * 100) if active_reminders_count > 0 else 0
    
    context = {
        'total_medicines': total_medicines,
        'unique_medicines': unique_medicines,
        'avg_confidence': round(avg_confidence, 1),
        'medicine_categories': medicine_categories,
        'active_reminders': active_reminders_count,
        'adherence_rate': round(adherence_rate, 1),
        'recent_scans': scans.order_by('-created_at')[:5],
    }
    return render(request, 'scanner/insights.html', context)

@login_required
def medicine_interactions(request):
    active_medicines = Reminder.objects.filter(user=request.user, is_active=True).values_list('medicine_name', flat=True)
    interactions = check_medicine_interactions(list(active_medicines))
    context = {
        'active_medicines': active_medicines,
        'interactions': interactions,
    }
    return render(request, 'scanner/interactions.html', context)

# Additional Utility Views
@login_required
def dashboard(request):
    total_scans = MedicineScan.objects.filter(user=request.user).count()
    total_reminders = Reminder.objects.filter(user=request.user).count()
    active_reminders = Reminder.objects.filter(user=request.user, is_active=True).count()
    recent_scans = MedicineScan.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_scans': total_scans,
        'total_reminders': total_reminders,
        'active_reminders': active_reminders,
        'recent_scans': recent_scans,
        'recent_reminders': recent_reminders,
    }
    return render(request, 'scanner/dashboard.html', context)

@login_required
def favorites(request):
    favorite_scans = MedicineScan.objects.filter(user=request.user, is_favorite=True).order_by('-created_at')
    context = {'favorite_scans': favorite_scans}
    return render(request, 'scanner/favorites.html', context)

@login_required
def reminder_calendar(request):
    today = timezone.now().date()
    reminders = Reminder.objects.filter(user=request.user, is_active=True)
    context = {
        'reminders': reminders,
        'current_date': today,
    }
    return render(request, 'scanner/calendar.html', context)

@login_required
def medicine_reports(request):
    scans = MedicineScan.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user)
    
    total_medicines = scans.count()
    unique_medicines = scans.values('medicine_name').distinct().count()
    avg_confidence = scans.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
    
    medicine_categories = {}
    for scan in scans:
        category = classify_medicine_category(scan.medicine_name)
        medicine_categories[category] = medicine_categories.get(category, 0) + 1
    
    context = {
        'total_medicines': total_medicines,
        'unique_medicines': unique_medicines,
        'avg_confidence': avg_confidence,
        'medicine_categories': medicine_categories,
        'total_reminders': reminders.count(),
        'active_reminders': reminders.filter(is_active=True).count(),
    }
    return render(request, 'scanner/reports.html', context)

# API Endpoints
def search_medicines(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    mock_results = [
        {'name': 'Paracetamol', 'generic_name': 'Acetaminophen'},
        {'name': 'Ibuprofen', 'generic_name': 'Ibuprofen'},
        {'name': 'Aspirin', 'generic_name': 'Acetylsalicylic acid'},
    ]
    filtered_results = [result for result in mock_results if query.lower() in result['name'].lower()]
    return JsonResponse({'results': filtered_results})

def medicine_suggestions(request):
    suggestions = [
        'Paracetamol', 'Ibuprofen', 'Aspirin', 'Amoxicillin', 
        'Metformin', 'Atorvastatin', 'Omeprazole', 'Losartan'
    ]
    return JsonResponse({'suggestions': suggestions})

@login_required
def reminder_stats(request):
    try:
        today = timezone.now().date()
        pending_reminders = Reminder.objects.filter(
            user=request.user,
            is_active=True,
            next_reminder__date=today,
            last_taken__date__lt=today
        ).order_by('next_reminder')
        
        pending_data = [
            {
                'id': reminder.id,
                'medicine_name': reminder.medicine_name,
                'dosage': reminder.dosage,
                'next_due': reminder.next_reminder.isoformat()
            }
            for reminder in pending_reminders
        ]
        return JsonResponse({
            'pending_count': len(pending_data),
            'pending_reminders': pending_data,
            'total_active': Reminder.objects.filter(user=request.user, is_active=True).count()
        })
    except Exception as e:
        messages.error(request, f'Error retrieving stats: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)

# PWA Support
def manifest(request):
    manifest_data = {
        "name": "MediScan Pro",
        "short_name": "MediScan",
        "description": "Smart Medicine Scanner and Health Management",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#059669",
        "icons": [
            {"src": "/static/images/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/images/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    return JsonResponse(manifest_data)

def service_worker(request):
    sw_content = """
const CACHE_NAME = 'mediscan-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/js/script.js',
  '/static/images/icon-192.png',
  '/offline/'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
"""
    return HttpResponse(sw_content, content_type='application/javascript')

def offline(request):
    return render(request, 'scanner/offline.html')

# Utility Functions
def calculate_reminder_streak(user):
    today = timezone.now().date()
    streak = 0
    current_date = today
    while True:
        day_reminders = Reminder.objects.filter(user=user, last_taken__date=current_date)
        if day_reminders.exists():
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    return streak