"""Email service for sending notifications to users."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in backend directory
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, will use system env vars only
    pass


# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "WAD2 Project")


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.host = SMTP_HOST
        self.port = SMTP_PORT
        self.username = SMTP_USER
        self.password = SMTP_PASSWORD
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email to a recipient.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.username or not self.password:
            print("⚠️  Email credentials not configured. Skipping email send.")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False


# Email templates

def get_achievement_email_template(
    user_name: str, achievement_title: str, achievement_icon: str, achievement_description: str
) -> tuple[str, str]:
    """Generate achievement unlock email template."""
    
    subject = f"🎉 Achievement Unlocked: {achievement_title}!"
    
    text_content = f"""
Hi {user_name},

Congratulations! You've unlocked a new achievement!

{achievement_icon} {achievement_title}
{achievement_description}

Keep up the great work on your wellness journey!

Best regards,
WAD2 Project Team
    """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .achievement-icon {{
            font-size: 80px;
            margin-bottom: 20px;
        }}
        .achievement-title {{
            font-size: 28px;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 10px;
        }}
        .achievement-description {{
            font-size: 16px;
            color: #636e72;
            margin-bottom: 30px;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #95a5a6;
        }}
        .celebration {{
            text-align: center;
            font-size: 48px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="celebration">🎉✨🎊</div>
            <h1 style="color: #667eea; margin-bottom: 10px;">Achievement Unlocked!</h1>
        </div>
        
        <div style="text-align: center;">
            <div class="achievement-icon">{achievement_icon}</div>
            <div class="achievement-title">{achievement_title}</div>
            <div class="achievement-description">{achievement_description}</div>
        </div>
        
        <div style="text-align: center;">
            <p style="font-size: 16px; color: #2d3436;">
                Congratulations, {user_name}! You're making excellent progress on your wellness journey.
            </p>
            <a href="https://your-app-url.com/profile?tab=achievements" class="cta-button">
                View Your Achievements
            </a>
        </div>
        
        <div class="footer">
            <p>Keep up the great work! 💪</p>
            <p>WAD2 Project Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return subject, html_content, text_content


def get_daily_checkin_reminder_template(user_name: str) -> tuple[str, str]:
    """Generate daily check-in reminder email template."""
    
    subject = "🌟 Daily Wellness Check-in Reminder"
    
    text_content = f"""
Hi {user_name},

Don't forget to complete your daily wellness check-in!

Taking a few moments each day to reflect on your wellness helps you:
✓ Track your mood and energy levels
✓ Maintain your check-in streak
✓ Unlock achievements
✓ Stay mindful of your well-being

Complete your check-in now to keep your streak going!

Best regards,
WAD2 Project Team
    """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        .benefits {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
        }}
        .benefit-item {{
            padding: 8px 0;
            display: flex;
            align-items: center;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #95a5a6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">🌟</div>
            <h1 style="color: #667eea; margin-bottom: 10px;">Daily Check-in Time!</h1>
            <p style="color: #636e72;">Hi {user_name},</p>
        </div>
        
        <p style="font-size: 16px; color: #2d3436;">
            Don't forget to complete your daily wellness check-in! Taking a few moments each day helps you stay mindful of your well-being.
        </p>
        
        <div class="benefits">
            <h3 style="margin-top: 0; color: #667eea;">Benefits of Daily Check-ins:</h3>
            <div class="benefit-item">✓ Track your mood and energy levels</div>
            <div class="benefit-item">✓ Maintain your check-in streak</div>
            <div class="benefit-item">✓ Unlock achievements</div>
            <div class="benefit-item">✓ Stay mindful of your well-being</div>
        </div>
        
        <div style="text-align: center;">
            <a href="https://your-app-url.com/checkin" class="cta-button">
                Complete Check-in Now
            </a>
        </div>
        
        <div class="footer">
            <p>Keep your streak going! 🔥</p>
            <p>WAD2 Project Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return subject, html_content, text_content


def get_study_reminder_template(user_name: str) -> tuple[str, str]:
    """Generate study session reminder email template."""
    
    subject = "📚 Time for Your Study Session!"
    
    text_content = f"""
Hi {user_name},

It's time to start your study session!

Remember to:
✓ Find a quiet, comfortable space
✓ Eliminate distractions
✓ Take regular breaks
✓ Stay hydrated

Your focused study time awaits. Let's make it productive!

Best regards,
WAD2 Project Team
    """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        .tips {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
        }}
        .tip-item {{
            padding: 8px 0;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #95a5a6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">📚</div>
            <h1 style="color: #667eea; margin-bottom: 10px;">Study Time!</h1>
            <p style="color: #636e72;">Hi {user_name},</p>
        </div>
        
        <p style="font-size: 16px; color: #2d3436;">
            It's time to start your focused study session. Let's make it productive!
        </p>
        
        <div class="tips">
            <h3 style="margin-top: 0; color: #856404;">Study Tips:</h3>
            <div class="tip-item">✓ Find a quiet, comfortable space</div>
            <div class="tip-item">✓ Eliminate distractions</div>
            <div class="tip-item">✓ Take regular breaks (Pomodoro technique)</div>
            <div class="tip-item">✓ Stay hydrated and take care of yourself</div>
        </div>
        
        <div style="text-align: center;">
            <a href="https://your-app-url.com/timer" class="cta-button">
                Start Study Session
            </a>
        </div>
        
        <div class="footer">
            <p>Focus. Learn. Achieve. 🎯</p>
            <p>WAD2 Project Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    return subject, html_content, text_content


# Initialize email service
email_service = EmailService()

