# Troubleshooting Guide - MediScan Pro

## Common Issues and Solutions

### 1. Template Errors

#### Issue: `TemplateDoesNotExist: registration/login.html`
**Solution:** The registration templates have been created. Make sure you're using the latest version of the code.

#### Issue: `Invalid block tag: 'static'`
**Solution:** The `{% load static %}` tag has been added to base.html. All templates should now work correctly.

### 2. Database Issues

#### Issue: `No module named 'corsheaders'`
**Solution:** Install dependencies using:
```bash
pip install -r requirements.txt
```

#### Issue: Migration errors
**Solution:** Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Static Files Issues

#### Issue: Static files not loading
**Solution:** 
1. Check that `STATICFILES_DIRS` points to the correct directory
2. Run `python manage.py collectstatic` for production
3. Ensure the CSS file exists at `scan_app/static/css/style.css`

### 4. Server Won't Start

#### Issue: Port already in use
**Solution:** 
```bash
python manage.py runserver 8001
```

#### Issue: Permission denied
**Solution:** Run as administrator or use a different port

### 5. Virtual Environment Issues

#### Issue: `venv\Scripts\activate` not found
**Solution:** Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Issue: Packages not found after activation
**Solution:** Reinstall packages:
```bash
pip install -r requirements.txt
```

### 6. Windows-Specific Issues

#### Issue: PowerShell execution policy
**Solution:** Run PowerShell as administrator and execute:
```powershell
Set-ExecutionPolicy RemoteSigned
```

#### Issue: Batch file not working
**Solution:** Use Command Prompt instead of PowerShell

### 7. Development Setup Issues

#### Issue: Python not found
**Solution:** 
1. Install Python 3.8+ from https://python.org
2. Add Python to PATH during installation
3. Restart command prompt

#### Issue: pip not found
**Solution:** 
```bash
python -m pip install --upgrade pip
```

### 8. Application-Specific Issues

#### Issue: Image upload not working
**Solution:** 
1. Check that `MEDIA_ROOT` directory exists
2. Ensure proper file permissions
3. Check file size limits in settings

#### Issue: Reminders not working
**Solution:** 
1. Check database migrations
2. Verify reminder models are properly configured
3. Check user authentication

### 9. Performance Issues

#### Issue: Slow loading
**Solution:** 
1. Use `DEBUG=False` for production
2. Enable caching
3. Optimize database queries

### 10. Security Issues

#### Issue: SECRET_KEY warning
**Solution:** Generate a new secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Getting Help

If you encounter issues not covered here:

1. **Check the logs** - Look for error messages in the console
2. **Verify setup** - Run `python manage.py check`
3. **Test step by step** - Start with basic Django setup
4. **Check versions** - Ensure compatible versions of Python and Django

## Quick Fix Commands

```bash
# Reset everything and start fresh
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Environment Variables

Create a `.env` file for sensitive settings:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
``` 