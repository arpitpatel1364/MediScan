// MediScan Pro - Enhanced JavaScript

// Global variables
let currentScanResult = null;
let reminderNotifications = [];
let isOnline = navigator.onLine;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkNotificationPermission();
    setupOfflineHandling();
});

function initializeApp() {
    // Initialize tooltips
    initTooltips();
    
    // Setup image upload handler
    setupImageUpload();
    
    // Initialize reminder system
    initReminderSystem();
    
    // Setup search functionality
    setupSearch();
    
    // Initialize PWA features
    setupPWA();
}

function setupEventListeners() {
    // Image input change handler
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageUpload);
    }
    
    // Search input handlers
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Form submission handlers
    const forms = document.querySelectorAll('form[data-ajax]');
    forms.forEach(form => {
        form.addEventListener('submit', handleAjaxForm);
    });
    
    // Notification click handlers
    document.addEventListener('click', handleNotificationClick);
    
    // Online/offline status
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
}

// Image Upload Functionality
function setupImageUpload() {
    const dropZone = document.getElementById('scanArea');
    if (!dropZone) return;
    
    // Drag and drop handlers
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!isValidImageType(file)) {
        showNotification('Please select a valid image file (JPG, PNG, WEBP)', 'error');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showNotification('Image size should be less than 10MB', 'error');
        return;
    }
    
    previewImage(file);
    enableSubmitButton();
}

function previewImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewDiv = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        
        if (previewDiv && previewImg) {
            previewImg.src = e.target.result;
            previewDiv.classList.remove('hidden');
            previewDiv.classList.add('animate-fade-in');
        }
    };
    reader.readAsDataURL(file);
}

function isValidImageType(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    return validTypes.includes(file.type);
}

function enableSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-50');
    }
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('border-primary-400', 'bg-primary-100');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('border-primary-400', 'bg-primary-100');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('border-primary-400', 'bg-primary-100');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const imageInput = document.getElementById('image');
        if (imageInput) {
            imageInput.files = files;
            handleImageUpload({ target: { files: files } });
        }
    }
}

// Notification System
function checkNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        requestNotificationPermission();
    }
}

function requestNotificationPermission() {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            showNotification('Notifications enabled! You\'ll receive medicine reminders.', 'success');
        }
    });
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm animate-slide-up`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-lg">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('animate-fade-out');
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Reminder System
function initReminderSystem() {
    loadPendingReminders();
    setupReminderNotifications();
}

function loadPendingReminders() {
    fetch('/api/reminder-stats/')
        .then(response => response.json())
        .then(data => {
            updateReminderBadge(data.pending_count);
            reminderNotifications = data.pending_reminders;
        })
        .catch(error => console.error('Error loading reminders:', error));
}

function updateReminderBadge(count) {
    const badge = document.getElementById('reminderBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

function setupReminderNotifications() {
    // Check for due reminders every minute
    setInterval(checkDueReminders, 60000);
}

function checkDueReminders() {
    const now = new Date();
    reminderNotifications.forEach(reminder => {
        const reminderTime = new Date(reminder.next_due);
        if (reminderTime <= now && !reminder.notified) {
            showReminderNotification(reminder);
            reminder.notified = true;
        }
    });
}

function showReminderNotification(reminder) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(`Medicine Reminder: ${reminder.medicine_name}`, {
            body: `Time to take ${reminder.dosage}`,
            icon: '/static/images/icon-192.png',
            badge: '/static/images/badge-72.png',
            tag: `reminder-${reminder.id}`,
            requireInteraction: true,
            actions: [
                { action: 'taken', title: 'Mark as Taken' },
                { action: 'snooze', title: 'Snooze 15 min' }
            ]
        });
        
        notification.onclick = () => {
            window.focus();
            window.location.href = '/reminders/';
            notification.close();
        };
    }
    
    // Also show in-app notification
    showNotification(
        `Reminder: Time to take ${reminder.medicine_name} (${reminder.dosage})`,
        'warning',
        10000
    );
}

// Search Functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
}

function performSearch(event) {
    const query = event.target.value.trim();
    if (query.length < 2) return;
    
    fetch(`/api/search-medicines/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => console.error('Search error:', error));
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-gray-500 text-center py-4">No medicines found</p>';
        return;
    }
    
    resultsContainer.innerHTML = results.map(medicine => `
        <div class="p-3 hover:bg-gray-50 border-b cursor-pointer" onclick="selectMedicine('${medicine.name}')">
            <div class="font-medium">${medicine.name}</div>
            <div class="text-sm text-gray-600">${medicine.generic_name || ''}</div>
        </div>
    `).join('');
}

function selectMedicine(medicineName) {
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('searchResults');
    
    if (searchInput) searchInput.value = medicineName;
    if (resultsContainer) resultsContainer.innerHTML = '';
    
    // Trigger medicine info load
    loadMedicineInfo(medicineName);
}

// Medicine Information
function loadMedicineInfo(medicineName) {
    showLoadingState();
    
    fetch(`/api/medicine-info/?name=${encodeURIComponent(medicineName)}`)
        .then(response => response.json())
        .then(data => {
            displayMedicineInfo(data);
            hideLoadingState();
        })
        .catch(error => {
            console.error('Error loading medicine info:', error);
            showNotification('Error loading medicine information', 'error');
            hideLoadingState();
        });
}

function displayMedicineInfo(medicineData) {
    const infoContainer = document.getElementById('medicineInfo');
    if (!infoContainer) return;
    
    infoContainer.innerHTML = `
        <div class="medicine-info-grid">
            <div class="medicine-info-card">
                <div class="medicine-info-icon bg-gradient-to-r from-blue-500 to-blue-600">
                    <i class="fas fa-info-circle"></i>
                </div>
                <h4 class="font-semibold text-gray-800 mb-2">Uses</h4>
                <p class="text-gray-600 text-sm">${medicineData.uses || 'Not available'}</p>
            </div>
            <div class="medicine-info-card">
                <div class="medicine-info-icon bg-gradient-to-r from-green-500 to-green-600">
                    <i class="fas fa-pills"></i>
                </div>
                <h4 class="font-semibold text-gray-800 mb-2">Dosage</h4>
                <p class="text-gray-600 text-sm">${medicineData.dosage || 'Consult doctor'}</p>
            </div>
            <div class="medicine-info-card">
                <div class="medicine-info-icon bg-gradient-to-r from-red-500 to-red-600">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4 class="font-semibold text-gray-800 mb-2">Side Effects</h4>
                <p class="text-gray-600 text-sm">${medicineData.side_effects || 'Consult doctor'}</p>
            </div>
        </div>
    `;
}

// Loading States
function showLoadingState() {
    const loadingElements = document.querySelectorAll('.loading-spinner');
    loadingElements.forEach(el => el.classList.remove('hidden'));
    
    const buttons = document.querySelectorAll('button[data-loading]');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.classList.add('opacity-50');
    });
}

function hideLoadingState() {
    const loadingElements = document.querySelectorAll('.loading-spinner');
    loadingElements.forEach(el => el.classList.add('hidden'));
    
    const buttons = document.querySelectorAll('button[data-loading]');
    buttons.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('opacity-50');
    });
}

// AJAX Form Handling
function handleAjaxForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const url = form.action || window.location.pathname;
    
    showLoadingState();
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Operation completed successfully', 'success');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showNotification(data.message || 'An error occurred', 'error');
        }
        hideLoadingState();
    })
    .catch(error => {
        console.error('Form submission error:', error);
        showNotification('An error occurred. Please try again.', 'error');
        hideLoadingState();
    });
}

// PWA Features
function setupPWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered:', registration);
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch(error => console.log('SW registration failed:', error));
    }
    
    // Handle install prompt
    setupInstallPrompt();
}

function setupInstallPrompt() {
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallButton();
    });
    
    const installButton = document.getElementById('installApp');
    if (installButton) {
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                if (outcome === 'accepted') {
                    showNotification('App installed successfully!', 'success');
                }
                deferredPrompt = null;
                hideInstallButton();
            }
        });
    }
}

function showInstallButton() {
    const installButton = document.getElementById('installApp');
    if (installButton) {
        installButton.classList.remove('hidden');
    }
}

function hideInstallButton() {
    const installButton = document.getElementById('installApp');
    if (installButton) {
        installButton.classList.add('hidden');
    }
}

function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info fixed bottom-4 right-4 z-50 max-w-sm';
    notification.innerHTML = `
        <i class="fas fa-download"></i>
        <span>New version available!</span>
        <button onclick="updateApp()" class="btn-primary ml-2 text-sm">Update</button>
        <button onclick="this.parentElement.remove()" class="ml-2 text-lg">&times;</button>
    `;
    document.body.appendChild(notification);
}

function updateApp() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(registration => {
            registration.waiting?.postMessage({ type: 'SKIP_WAITING' });
        });
    }
    window.location.reload();
}

// Offline Handling
function setupOfflineHandling() {
    updateOnlineStatus();
}

function handleOnlineStatus() {
    isOnline = true;
    updateOnlineStatus();
    showNotification('Connection restored', 'success', 3000);
    syncOfflineData();
}

function handleOfflineStatus() {
    isOnline = false;
    updateOnlineStatus();
    showNotification('You are now offline. Some features may be limited.', 'warning', 5000);
}

function updateOnlineStatus() {
    const statusIndicator = document.getElementById('onlineStatus');
    if (statusIndicator) {
        statusIndicator.className = isOnline ? 'online' : 'offline';
        statusIndicator.textContent = isOnline ? 'Online' : 'Offline';
    }
}

function syncOfflineData() {
    // Sync any offline data when connection is restored
    const offlineData = localStorage.getItem('offlineData');
    if (offlineData) {
        const data = JSON.parse(offlineData);
        // Process offline data
        localStorage.removeItem('offlineData');
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function formatTime(time) {
    return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(`2000-01-01T${time}`));
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success', 2000);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success', 2000);
    }
}

// Analytics and Tracking
function trackEvent(category, action, label = null) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: category,
            event_label: label
        });
    }
}

function trackScanEvent(medicineName) {
    trackEvent('Medicine', 'Scan', medicineName);
}

function trackReminderEvent(action, medicineName) {
    trackEvent('Reminder', action, medicineName);
}

// Image optimization
function compressImage(file, maxWidth = 1200, quality = 0.8) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
            canvas.width = img.width * ratio;
            canvas.height = img.height * ratio;
            
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob(resolve, 'image/jpeg', quality);
        };
        
        img.src = URL.createObjectURL(file);
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Handle notification clicks
function handleNotificationClick(event) {
    if (event.target.matches('[data-notification-action]')) {
        const action = event.target.getAttribute('data-notification-action');
        const id = event.target.getAttribute('data-id');
        
        switch (action) {
            case 'mark-taken':
                markReminderTaken(id);
                break;
            case 'snooze':
                snoozeReminder(id);
                break;
            case 'dismiss':
                dismissNotification(event.target.closest('.alert'));
                break;
        }
    }
}

function markReminderTaken(reminderId) {
    fetch(`/mark-reminder-complete/${reminderId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    }).then(response => {
        if (response.ok) {
            showNotification('Reminder marked as taken', 'success');
            loadPendingReminders(); // Refresh reminder count
        }
    });
}

function dismissNotification(notification) {
    notification.classList.add('animate-fade-out');
    setTimeout(() => notification.remove(), 300);
}

// Export for global access
window.MediScan = {
    showNotification,
    trackEvent,
    copyToClipboard,
    formatDate,
    formatTime,
    compressImage
};

module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};