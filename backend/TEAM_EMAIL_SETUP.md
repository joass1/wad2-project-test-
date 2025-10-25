# 📧 WAD2 Project Email Setup Guide for Team Members

## 🎯 Overview
This guide helps team members quickly set up email notifications for the WAD2 Project. The system automatically uses Firebase user emails for sending notifications.

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script
1. Navigate to the `backend/` directory
2. Run the setup script:
   ```bash
   python setup_email.py
   ```
3. Follow the prompts to configure your email service
4. Test the configuration when prompted

### Option 2: Manual Setup
1. Copy `email-config-shared.txt` to `.env` in the `backend/` directory
2. Edit `.env` with your actual email credentials
3. Restart the backend server

## 📧 Email Service Options

### Gmail (Recommended for Development)
- **Pros**: Free, easy setup, reliable
- **Setup**: Requires 2FA + App Password
- **Cost**: Free

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=WAD2 Project Team
```

### SendGrid (Recommended for Production)
- **Pros**: Professional, high deliverability, analytics
- **Setup**: Requires API key
- **Cost**: Free tier available

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=verified-email@your-domain.com
SMTP_FROM_NAME=WAD2 Project Team
```

## 🔧 Gmail Setup Instructions

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Follow the setup process

### Step 2: Generate App Password
1. In Google Account Security, go to "App passwords"
2. Select "Mail" and "Other (custom name)"
3. Enter "WAD2 Project" as the name
4. Copy the 16-character password
5. Use this password in your `.env` file (not your regular password)

### Step 3: Configure Environment
Create `backend/.env` with:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=WAD2 Project Team
```

## 🧪 Testing Email Configuration

### Automated Test
```bash
cd backend
python setup_email.py test
```

### Manual Test
1. Start your backend server
2. Trigger any notification (e.g., claim an achievement)
3. Check console for: `✅ Email sent successfully to [email]`
4. Check your email inbox (and spam folder)

## 🔄 How It Works

### User Email Retrieval
The system automatically gets user emails from:
1. **Firestore User Document** (if email is stored there)
2. **Firebase Auth** (fallback to user's auth email)
3. **Graceful Fallback** (if no email found, skips email, creates in-app notification)

### Notification Flow
```
User Action (e.g., Achievement Unlocked)
    ↓
Check User Notification Settings
    ↓
Create In-App Notification
    ↓
Get User Email from Firebase
    ↓
Send Email Notification (if email found)
    ↓
Log Success/Failure
```

## 🛠️ Troubleshooting

### "Email credentials not configured"
- **Cause**: Missing or empty SMTP credentials
- **Solution**: Check your `.env` file has correct values

### "Authentication failed"
- **Cause**: Wrong username/password
- **Solution**: Verify credentials, use App Password for Gmail

### "No email received"
- **Causes**: 
  - User email not in Firebase
  - Email in spam folder
  - SMTP server issues
- **Solutions**:
  - Check user has email in Firebase Auth
  - Check spam/junk folder
  - Test with different email service

### "User email not found"
- **Cause**: User doesn't have email in Firebase
- **Solution**: System gracefully handles this - in-app notifications still work

## 📋 Team Checklist

- [ ] Email service configured (Gmail/SendGrid/Custom)
- [ ] `.env` file created in `backend/` directory
- [ ] Backend server restarted after configuration
- [ ] Email test completed successfully
- [ ] User can receive achievement notifications
- [ ] User can receive daily check-in reminders

## 🔒 Security Notes

- **Never commit `.env` files** to version control
- **Use App Passwords** for Gmail (not regular passwords)
- **Rotate credentials** periodically
- **Use environment variables** in production

## 📞 Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify your email credentials
3. Test with the setup script
4. Check Firebase user data has email addresses
5. Contact the team lead for shared credentials

## 🎉 Success Indicators

You'll know it's working when you see:
- `✅ Email sent successfully to [email]` in console
- Users receive email notifications
- In-app notifications work regardless of email status
- No "Email credentials not configured" warnings
