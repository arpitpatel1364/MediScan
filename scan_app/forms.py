from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reminder, UserProfile, MedicineScan

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Email address'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Phone number (optional)'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ReminderForm(forms.ModelForm):
    time_1 = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        }),
        required=True
    )
    time_2 = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        }),
        required=False
    )
    time_3 = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        }),
        required=False
    )
    time_4 = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        }),
        required=False
    )
    
    class Meta:
        model = Reminder
        fields = ['medicine_name', 'dosage', 'frequency', 'notes', 'start_date', 'duration', 'notification_sound']
        widgets = {
            'medicine_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Enter medicine name'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'e.g., 500mg, 1 tablet'
            }),
            'frequency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'onchange': 'updateTimeFields(this.value)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'rows': 3,
                'placeholder': 'Any additional notes (optional)'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'duration': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }),
            'notification_sound': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }, choices=[
                ('default', 'Default'),
                ('gentle', 'Gentle Bell'),
                ('chime', 'Chime'),
                ('beep', 'Beep'),
                ('melody', 'Melody'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notification_sound'].choices = [
            ('default', 'Default'),
            ('gentle', 'Gentle Bell'),
            ('chime', 'Chime'),
            ('beep', 'Beep'),
            ('melody', 'Melody'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')
        
        # Validate time fields based on frequency
        times = []
        if frequency == 'once':
            if cleaned_data.get('time_1'):
                times.append(cleaned_data['time_1'].strftime('%H:%M'))
        elif frequency == 'twice':
            if cleaned_data.get('time_1') and cleaned_data.get('time_2'):
                times.append(cleaned_data['time_1'].strftime('%H:%M'))
                times.append(cleaned_data['time_2'].strftime('%H:%M'))
            else:
                raise forms.ValidationError("Please provide both time slots for twice daily frequency.")
        elif frequency == 'thrice':
            if cleaned_data.get('time_1') and cleaned_data.get('time_2') and cleaned_data.get('time_3'):
                times.append(cleaned_data['time_1'].strftime('%H:%M'))
                times.append(cleaned_data['time_2'].strftime('%H:%M'))
                times.append(cleaned_data['time_3'].strftime('%H:%M'))
            else:
                raise forms.ValidationError("Please provide all three time slots for thrice daily frequency.")
        elif frequency == 'four':
            if all([cleaned_data.get(f'time_{i}') for i in range(1, 5)]):
                for i in range(1, 5):
                    times.append(cleaned_data[f'time_{i}'].strftime('%H:%M'))
            else:
                raise forms.ValidationError("Please provide all four time slots for four times daily frequency.")
        
        cleaned_data['reminder_times'] = times
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.reminder_times = self.cleaned_data['reminder_times']
        if commit:
            instance.save()
        return instance

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'profile_picture', 'notifications_enabled', 'email_reminders', 'sms_reminders', 'reminder_sound']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'placeholder': 'Phone number'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
                'accept': 'image/*'
            }),
            'notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
            }),
            'email_reminders': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
            }),
            'sms_reminders': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
            }),
            'reminder_sound': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
            }, choices=[
                ('default', 'Default'),
                ('gentle', 'Gentle Bell'),
                ('chime', 'Chime'),
                ('beep', 'Beep'),
                ('melody', 'Melody'),
            ]),
        }

class MedicineScanForm(forms.ModelForm):
    class Meta:
        model = MedicineScan
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'medicine-image-input'
            })
        }

class QuickReminderForm(forms.Form):
    medicine_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Medicine name'
        })
    )
    dosage = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Dosage (e.g., 500mg)'
        })
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        })
    )

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500',
            'placeholder': 'Search medicines or scan history...'
        })
    )

class DateFilterForm(forms.Form):
    DATE_CHOICES = [
        ('all', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
    ]
    
    filter = forms.ChoiceField(
        choices=DATE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500'
        }),
        required=False
    )