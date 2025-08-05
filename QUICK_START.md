# Quick Start Guide - MediScan Pro

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (or use Command Prompt on other systems)

### Step 1: Download and Extract
1. Download the project files
2. Extract to a folder (e.g., `C:\medicine_scanner`)

### Step 2: Run Setup (Windows)
```bash
# Double-click or run in Command Prompt:
setup_env.bat
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up database
- ✅ Create superuser (optional)

### Step 3: Start the Application
```bash
# Double-click or run in Command Prompt:
start.bat
```

### Step 4: Access the Application
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🎯 What You Can Do

### For New Users
1. **Create Account** - Sign up at http://127.0.0.1:8000/accounts/signup/
2. **Scan Medicine** - Upload medicine images for AI identification
3. **Set Reminders** - Create medication schedules
4. **View History** - Track all your scans

### For Administrators
1. **Access Admin** - http://127.0.0.1:8000/admin/
2. **Manage Users** - View and manage user accounts
3. **Monitor Data** - Check system statistics

## 📱 Features Overview

### Core Features
- 🔍 **AI Medicine Recognition** - Upload images to identify medicines
- ⏰ **Smart Reminders** - Set up medication schedules
- 📊 **Health Analytics** - View usage statistics and insights
- 📱 **Mobile Friendly** - Works on all devices
- 🔒 **Secure** - User authentication and data protection

### Advanced Features
- 📅 **Calendar View** - Visual reminder calendar
- ❤️ **Favorites** - Save frequently used medicines
- 📈 **Reports** - Detailed health analytics
- 🔄 **History** - Complete scan history

## 🛠️ Manual Setup (Alternative)

If the batch files don't work:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

## 🔧 Troubleshooting

### Common Issues
- **"Python not found"** - Install Python from https://python.org
- **"Port already in use"** - Use `python manage.py runserver 8001`
- **"Template errors"** - All templates have been fixed

### Get Help
- Check `TROUBLESHOOTING.md` for detailed solutions
- Run `python manage.py check` to verify setup
- Check console output for error messages

## 📁 Project Structure

```
medicine_scanner/
├── setup_env.bat      # Complete environment setup
├── start.bat          # Start the application
├── requirements.txt   # Python dependencies
├── README.md         # Detailed documentation
├── TROUBLESHOOTING.md # Common issues and solutions
├── medicine_scanner/  # Django project settings
└── scan_app/         # Main application
    ├── templates/    # HTML templates
    ├── static/       # CSS, JS, images
    ├── models.py     # Database models
    ├── views.py      # Application logic
    └── urls.py       # URL routing
```

## 🎉 Success!

Once the server is running, you'll see:
```
Starting development server at http://127.0.0.1:8000/
```

Open your browser and start using MediScan Pro!

## 📞 Support

If you need help:
1. Check the troubleshooting guide
2. Verify your setup with `python manage.py check`
3. Look for error messages in the console
4. Ensure all files are in the correct locations

---

**MediScan Pro** - Smart Medicine Management Made Simple! 🏥💊 