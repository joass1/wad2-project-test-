# Email Notification Setup Guide

This guide will help you configure email notifications for your WAD2 Project application.

## 📧 Email Configuration

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account settings
   - Navigate to Security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "WAD2 Project"
   - Copy the 16-character password

3. **Set Environment Variables**
   ```bash
   export SMTP_HOST=smtp.gmail.com
   export SMTP_PORT=587
   export SMTP_USER=your-email@gmail.com
   export SMTP_PASSWORD=your-16-char-app-password
   export SMTP_FROM_EMAIL=your-email@gmail.com
   export SMTP_FROM_NAME="WAD2 Project"
   ```

### Option 2: SendGrid (Recommended for Production)

1. **Sign up for SendGrid**
   - Visit: https://sendgrid.com/
   - Create a free account (100 emails/day)

2. **Create API Key**
   - Go to Settings > API Keys
   - Create new API Key with "Mail Send" permissions

3. **Set Environment Variables**
   ```bash
   export SMTP_HOST=smtp.sendgrid.net
   export SMTP_PORT=587
   export SMTP_USER=apikey
   export SMTP_PASSWORD=your-sendgrid-api-key
   export SMTP_FROM_EMAIL=verified-email@your-domain.com
   export SMTP_FROM_NAME="WAD2 Project"
   ```

### Option 3: Other SMTP Providers

#### Mailgun
```bash
export SMTP_HOST=smtp.mailgun.org
export SMTP_PORT=587
export SMTP_USER=postmaster@your-domain.mailgun.org
export SMTP_PASSWORD=your-mailgun-password
export SMTP_FROM_EMAIL=noreply@your-domain.com
export SMTP_FROM_NAME="WAD2 Project"
```

#### Outlook/Hotmail
```bash
export SMTP_HOST=smtp-mail.outlook.com
export SMTP_PORT=587
export SMTP_USER=your-email@outlook.com
export SMTP_PASSWORD=your-password
export SMTP_FROM_EMAIL=your-email@outlook.com
export SMTP_FROM_NAME="WAD2 Project"
```

## 🔧 Setting Up on Windows

Create a `.env` file in the `backend/` directory:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=WAD2 Project
```

Then install `python-dotenv` if not already installed:

```bash
uv add python-dotenv
```

Add to `backend/app/core/email.py` at the top:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 📝 User Email Setup

For email notifications to work, users must have their email stored in Firestore. You can:

### Option 1: Store email during registration

In your user registration/profile creation code, save the email:

```python
user_doc.set({
    "email": user_email,
    "displayName": user_name,
    # ... other fields
})
```

### Option 2: Get from Firebase Auth

Modify `get_user_email()` in `backend/app/core/notification_sender.py` to fetch from Firebase Auth:

```python
from firebase_admin import auth

def get_user_email(uid: str) -> Optional[str]:
    try:
        user_record = auth.get_user(uid)
        return user_record.email
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None
```

## 🎯 Notification Types

### 1. Achievement Notifications
Sent when a user claims an achievement:
- **Trigger**: `POST /api/achievements/{achievement_id}/claim`
- **Setting**: `achievement_notifications` must be enabled
- **Email**: Beautiful HTML template with achievement details

### 2. Daily Check-in Reminders
Sent to remind users to complete their daily wellness check-in:
- **Trigger**: Scheduled job (you need to implement)
- **Setting**: `daily_checkin` must be enabled
- **Email**: Wellness check-in reminder with benefits

### 3. Study Session Reminders
Sent to remind users about upcoming study sessions:
- **Trigger**: Scheduled job or timer start
- **Setting**: `study_reminders` must be enabled
- **Email**: Study session reminder with tips

## 🧪 Testing Email Notifications

### Test Achievement Email:

```bash
# Using Python console
from app.core.notification_sender import send_achievement_notification

send_achievement_notification(
    uid="your-firebase-uid",
    achievement_title="First Steps",
    achievement_icon="⭐",
    achievement_description="Complete your first wellness check-in",
    achievement_id="first_checkin"
)
```

### Test via API:

1. Enable achievement notifications in settings:
   ```bash
   curl -X PUT http://localhost:8000/api/notifications/settings \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "notifications": true,
       "achievement_notifications": true
     }'
   ```

2. Claim an achievement:
   ```bash
   curl -X POST http://localhost:8000/api/achievements/first_checkin/claim \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## 🔍 Troubleshooting

### No emails being sent?

1. **Check SMTP credentials**
   ```python
   from app.core.email import email_service
   print(f"SMTP User: {email_service.username}")
   print(f"SMTP Host: {email_service.host}")
   ```

2. **Check user email**
   ```python
   from app.core.notification_sender import get_user_email
   email = get_user_email("your-user-id")
   print(f"User email: {email}")
   ```

3. **Check notification settings**
   ```python
   from app.core.notification_sender import get_user_notification_settings
   settings = get_user_notification_settings("your-user-id")
   print(f"Settings: {settings}")
   ```

4. **Test email directly**
   ```python
   from app.core.email import email_service
   result = email_service.send_email(
       to_email="test@example.com",
       subject="Test Email",
       html_content="<h1>Test</h1>",
       text_content="Test"
   )
   print(f"Email sent: {result}")
   ```

### Gmail "Less secure app" error?

- Make sure you're using an **App Password**, not your regular password
- App Passwords only work with 2-Factor Authentication enabled

### Port issues?

Try alternative ports:
- Gmail: 465 (SSL) or 587 (TLS)
- Update `SMTP_PORT` in your environment variables

## 📚 Next Steps

1. **Implement scheduled reminders** for daily check-ins and study sessions
2. **Customize email templates** in `backend/app/core/email.py`
3. **Add more notification types** (social updates, etc.)
4. **Implement email preferences** in user settings
5. **Add email verification** during registration

## 🔒 Security Best Practices

- ✅ Never commit `.env` files with credentials
- ✅ Use App Passwords instead of real passwords
- ✅ Use environment variables for all sensitive data
- ✅ Consider using a dedicated email service for production
- ✅ Implement rate limiting for email sends
- ✅ Add unsubscribe links in production emails


