# MediScan Pro - Medicine Scanner Application

A Django-based web application for scanning and managing medicines using AI-powered image recognition.

## Features

- **Medicine Scanning**: Upload medicine images for AI-powered identification
- **Reminder Management**: Set up medication reminders with customizable schedules
- **Medicine History**: Track all scanned medicines with detailed information
- **Health Insights**: Analytics and reports on medication usage
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTML, CSS, JavaScript with Tailwind CSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Image Processing**: Pillow
- **AI/ML**: Mock implementation (ready for integration with real AI services)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medicine_scanner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## Project Structure

```
medicine_scanner/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── medicine_scanner/        # Project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── scan_app/               # Main application
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # App URL patterns
│   ├── forms.py            # Form definitions
│   ├── utils.py            # Utility functions
│   ├── templates/          # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── results.html
│   │   ├── history.html
│   │   ├── reminders.html
│   │   └── scanner/
│   │       ├── dashboard.html
│   │       ├── favorites.html
│   │       ├── calendar.html
│   │       ├── reports.html
│   │       └── medicine_detail.html
│   ├── static/             # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── migrations/         # Database migrations
└── media/                  # User-uploaded files
```

## Usage

### For Users

1. **Registration/Login**: Create an account or log in to access features
2. **Scan Medicine**: Upload an image of a medicine for identification
3. **View Results**: Get detailed information about the scanned medicine
4. **Set Reminders**: Create medication reminders with custom schedules
5. **Track History**: View all previously scanned medicines
6. **Manage Favorites**: Save frequently used medicines for quick access

### For Administrators

1. **Admin Panel**: Access `http://127.0.0.1:8000/admin/` with superuser credentials
2. **User Management**: View and manage user accounts
3. **Medicine Data**: Monitor scanned medicines and user activity
4. **System Statistics**: View analytics and reports

## Configuration

### Environment Variables

Create a `.env` file in the project root for environment-specific settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration

The application uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Integration

The application is designed to integrate with AI/ML services for medicine recognition. Currently, it uses a mock implementation in `utils.py`. To integrate with real AI services:

1. **Google Cloud Vision API**
2. **Azure Computer Vision**
3. **Custom ML models**

Update the `process_medicine_image()` function in `utils.py` to use your preferred AI service.

## Testing

Run tests using pytest:

```bash
pytest
```

## Deployment

### Production Setup

1. **Set DEBUG=False** in settings.py
2. **Configure a production database** (PostgreSQL recommended)
3. **Set up static file serving** with whitenoise or nginx
4. **Use a production WSGI server** like gunicorn
5. **Configure environment variables** for security

### Docker Deployment

```bash
# Build the image
docker build -t medicinescanner .

# Run the container
docker run -p 8000:8000 medicinescanner
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team

## Roadmap

- [ ] Real AI integration for medicine recognition
- [ ] Mobile app development
- [ ] Advanced analytics and reporting
- [ ] Integration with healthcare providers
- [ ] Multi-language support
- [ ] Offline functionality 