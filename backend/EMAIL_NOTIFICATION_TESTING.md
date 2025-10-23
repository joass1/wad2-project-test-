# Email Notification Testing Guide

This guide will help you test the email notification system.

## 🔧 Prerequisites

1. **Configure Email Settings** (see EMAIL_SETUP_GUIDE.md)
2. **Ensure user has email stored** in Firestore
3. **Enable notifications** in user settings

## 📧 Testing Email Configuration

### Step 1: Set Environment Variables

```bash
# Windows (PowerShell)
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
$env:SMTP_FROM_EMAIL="your-email@gmail.com"
$env:SMTP_FROM_NAME="WAD2 Project"

# Linux/Mac
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SMTP_FROM_EMAIL=your-email@gmail.com
export SMTP_FROM_NAME="WAD2 Project"
```

### Step 2: Add User Email to Firestore

Using Firebase Console:
1. Go to Firestore Database
2. Navigate to `users/{your-uid}`
3. Add field: `email` = "your-test-email@gmail.com"

Or via API/Code:
```python
from app.core.firebase import db

db.collection("users").document("your-uid").set({
    "email": "your-test-email@gmail.com",
    "displayName": "Test User"
}, merge=True)
```

## 🧪 Test Notification Types

### 1. Achievement Notification

#### Via Postman/API:

```bash
# Step 1: Enable achievement notifications
POST http://localhost:8000/api/notifications/settings
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
  Content-Type: application/json
Body:
{
  "notifications": true,
  "achievement_notifications": true,
  "study_reminders": true,
  "daily_checkin": true,
  "social_updates": false
}

# Step 2: Unlock an achievement (if not already unlocked)
# Submit enough check-ins to meet criteria, or manually set in Firestore

# Step 3: Claim the achievement (this triggers the email)
POST http://localhost:8000/api/achievements/first_checkin/claim
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
```

**Expected Result:**
- ✅ In-app notification created
- ✅ Email sent with achievement details
- ✅ Beautiful HTML email in inbox with:
  - 🎉 Celebration header
  - Achievement icon and title
  - Description
  - "View Your Achievements" button

### 2. Daily Check-in Reminder

#### Via Postman/API:

```bash
# Step 1: Enable daily check-in notifications
POST http://localhost:8000/api/notifications/settings
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
  Content-Type: application/json
Body:
{
  "notifications": true,
  "daily_checkin": true
}

# Step 2: Trigger reminder (testing endpoint)
POST http://localhost:8000/api/notifications/send-checkin-reminder
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
```

**Expected Result:**
- ✅ In-app notification created
- ✅ Email sent with reminder
- ✅ Email includes:
  - 🌟 Wellness icon
  - Benefits of daily check-ins
  - "Complete Check-in Now" button

### 3. Study Session Reminder

#### Via Postman/API:

```bash
# Step 1: Enable study reminders
POST http://localhost:8000/api/notifications/settings
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
  Content-Type: application/json
Body:
{
  "notifications": true,
  "study_reminders": true
}

# Step 2: Trigger reminder (testing endpoint)
POST http://localhost:8000/api/notifications/send-study-reminder
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
```

**Expected Result:**
- ✅ In-app notification created
- ✅ Email sent with reminder
- ✅ Email includes:
  - 📚 Study icon
  - Study tips
  - "Start Study Session" button

## 🔍 Debugging

### Check if emails are being sent

Look for console output:
```
✅ Email sent successfully to user@example.com
```

Or error messages:
```
❌ Failed to send email to user@example.com: [error details]
⚠️  Email credentials not configured. Skipping email send.
```

### Verify notification was created

```bash
GET http://localhost:8000/api/notifications/
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
```

Check that new notifications appear with correct `type` field.

### Check notification settings

```bash
GET http://localhost:8000/api/notifications/settings
Headers:
  Authorization: Bearer YOUR_FIREBASE_TOKEN
```

Verify that the appropriate notification types are enabled.

### Test email service directly

Create a test script `test_email.py` in `backend/`:

```python
import os
os.environ["SMTP_HOST"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_USER"] = "your-email@gmail.com"
os.environ["SMTP_PASSWORD"] = "your-app-password"
os.environ["SMTP_FROM_EMAIL"] = "your-email@gmail.com"

from app.core.email import email_service

result = email_service.send_email(
    to_email="test-recipient@gmail.com",
    subject="Test Email from WAD2 Project",
    html_content="<h1>Hello!</h1><p>This is a test email.</p>",
    text_content="Hello! This is a test email."
)

print(f"Email sent: {result}")
```

Run:
```bash
cd backend
python test_email.py
```

## 📊 Testing Checklist

- [ ] Email credentials configured
- [ ] User email stored in Firestore
- [ ] Backend server running
- [ ] Notification settings enabled
- [ ] Achievement notification works
- [ ] Check-in reminder works
- [ ] Study reminder works
- [ ] Emails arrive in inbox (check spam folder!)
- [ ] HTML templates display correctly
- [ ] In-app notifications created
- [ ] Notification preferences respected

## 🐛 Common Issues

### Issue: No email received

**Possible causes:**
1. Email credentials not set or incorrect
2. User email not in Firestore
3. Notification type disabled in settings
4. Email in spam folder
5. SMTP port blocked by firewall

**Solutions:**
- Check all console logs
- Verify SMTP credentials
- Check spam/junk folder
- Try different SMTP port (465 instead of 587)
- Verify user email with `get_user_email(uid)`

### Issue: "Authentication failed"

**Solution:**
- For Gmail, ensure you're using an **App Password**, not your regular password
- Enable 2-Factor Authentication first
- Generate new App Password

### Issue: Emails sent but notification settings don't persist

**Solution:**
- Check that settings are being saved to Firestore
- Verify the API endpoint response
- Check Firestore console to see if `notification_settings` field exists

### Issue: In-app notification created but no email

**Solution:**
- Check console for email sending errors
- Verify email service has credentials
- Test email service directly (see debugging section)

## 🎯 Production Recommendations

1. **Use a dedicated email service** (SendGrid, Mailgun)
2. **Implement rate limiting** to prevent spam
3. **Add unsubscribe links** to all emails
4. **Track email delivery** status
5. **Implement email verification** during registration
6. **Add retry logic** for failed email sends
7. **Use email templates** stored in database
8. **Log all email activities** for debugging
9. **Implement scheduled jobs** for automatic reminders
10. **Add email bounce handling**

## 📅 Scheduled Reminders (Future Implementation)

To implement automatic daily reminders, you can use:

1. **Cron jobs** with Python APScheduler
2. **Cloud Functions** (Firebase, AWS Lambda)
3. **Background tasks** with Celery
4. **Cloud Scheduler** (Google Cloud Platform)

Example with APScheduler:

```python
from apscheduler.schedulers.background import BackgroundScheduler

def send_daily_reminders():
    # Get all users who need reminders
    users = db.collection("users").where("notification_settings.daily_checkin", "==", True).stream()
    
    for user in users:
        send_daily_checkin_reminder(user.id)

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_reminders, 'cron', hour=9, minute=0)
scheduler.start()
```


