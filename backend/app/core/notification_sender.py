"""Helper functions for sending notifications with email integration."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from google.cloud import firestore

from .firebase import db
from .email import (
    email_service,
    get_achievement_email_template,
    get_daily_checkin_reminder_template,
    get_study_reminder_template,
)


def _user_doc(uid: str):
    """Get user document reference."""
    return db.collection("users").document(uid)


def _notifications_collection(uid: str):
    """Get user's notifications collection reference."""
    return _user_doc(uid).collection("notifications")


def get_user_email(uid: str) -> Optional[str]:
    """Get user's email address from Firebase Auth or user document."""
    try:
        # Try to get from user document first
        user_doc = _user_doc(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict() or {}
            if "email" in user_data and user_data["email"]:
                return user_data["email"]
        
        # If not found in Firestore, get from Firebase Auth
        try:
            import firebase_admin.auth as auth
            user_record = auth.get_user(uid)
            if user_record.email:
                return user_record.email
        except Exception as auth_error:
            print(f"Error getting email from Firebase Auth: {auth_error}")
        
        return None
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None


def get_user_notification_settings(uid: str) -> Dict[str, bool]:
    """Get user's notification settings."""
    try:
        user_doc = _user_doc(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict() or {}
            settings = user_data.get("notification_settings", {})
            return {
                "notifications": settings.get("notifications", True),
                "study_reminders": settings.get("study_reminders", True),
                "daily_checkin": settings.get("daily_checkin", True),
                "achievement_notifications": settings.get("achievement_notifications", False),
                "social_updates": settings.get("social_updates", False),
            }
        return {
            "notifications": True,
            "study_reminders": True,
            "daily_checkin": True,
            "achievement_notifications": False,
            "social_updates": False,
        }
    except Exception as e:
        print(f"Error getting notification settings: {e}")
        return {}


def send_achievement_notification(
    uid: str,
    achievement_title: str,
    achievement_icon: str,
    achievement_description: str,
    achievement_id: str,
) -> bool:
    """
    Send achievement unlock notification (in-app + email).
    
    Args:
        uid: User ID
        achievement_title: Title of the achievement
        achievement_icon: Icon/emoji for the achievement
        achievement_description: Description of what was achieved
        achievement_id: ID of the achievement
    
    Returns:
        True if notification was created successfully
    """
    try:
        # Check if user has achievement notifications enabled
        settings = get_user_notification_settings(uid)
        if not settings.get("achievement_notifications"):
            print(f"Achievement notifications disabled for user {uid}")
            return False
        
        # Create in-app notification
        now = datetime.now(timezone.utc)
        notification_data = {
            "type": "achievement",
            "title": f"Achievement Unlocked: {achievement_title}",
            "message": achievement_description,
            "is_read": False,
            "created_at": now,
            "action_url": "/profile?tab=achievements",
            "metadata": {
                "achievement_id": achievement_id,
                "achievement_icon": achievement_icon,
            },
        }
        
        _notifications_collection(uid).add(notification_data)
        print(f"✅ In-app notification created for user {uid}")
        
        # Send email notification
        user_email = get_user_email(uid)
        if user_email:
            # Get user name (you might want to store this in user document)
            user_doc = _user_doc(uid).get()
            user_name = "there"
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                user_name = user_data.get("displayName") or user_data.get("name") or "there"
            
            subject, html_content, text_content = get_achievement_email_template(
                user_name, achievement_title, achievement_icon, achievement_description
            )
            
            email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        
        return True
        
    except Exception as e:
        print(f"Error sending achievement notification: {e}")
        return False


def send_daily_checkin_reminder(uid: str) -> bool:
    """
    Send daily check-in reminder (in-app + email).
    
    Args:
        uid: User ID
    
    Returns:
        True if notification was created successfully
    """
    try:
        # Check if user has daily check-in reminders enabled
        settings = get_user_notification_settings(uid)
        if not settings.get("daily_checkin"):
            print(f"Daily check-in reminders disabled for user {uid}")
            return False
        
        # Create in-app notification
        now = datetime.now(timezone.utc)
        notification_data = {
            "type": "daily_checkin",
            "title": "Daily Wellness Check-in",
            "message": "Don't forget to complete your daily check-in to maintain your streak!",
            "is_read": False,
            "created_at": now,
            "action_url": "/checkin",
            "metadata": {},
        }
        
        _notifications_collection(uid).add(notification_data)
        print(f"✅ Daily check-in notification created for user {uid}")
        
        # Send email notification
        user_email = get_user_email(uid)
        if user_email:
            user_doc = _user_doc(uid).get()
            user_name = "there"
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                user_name = user_data.get("displayName") or user_data.get("name") or "there"
            
            subject, html_content, text_content = get_daily_checkin_reminder_template(user_name)
            
            email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        
        return True
        
    except Exception as e:
        print(f"Error sending daily check-in reminder: {e}")
        return False


def send_study_reminder(uid: str) -> bool:
    """
    Send study session reminder (in-app + email).
    
    Args:
        uid: User ID
    
    Returns:
        True if notification was created successfully
    """
    try:
        # Check if user has study reminders enabled
        settings = get_user_notification_settings(uid)
        if not settings.get("study_reminders"):
            print(f"Study reminders disabled for user {uid}")
            return False
        
        # Create in-app notification
        now = datetime.now(timezone.utc)
        notification_data = {
            "type": "study_reminder",
            "title": "Study Session Time",
            "message": "It's time to start your focused study session!",
            "is_read": False,
            "created_at": now,
            "action_url": "/timer",
            "metadata": {},
        }
        
        _notifications_collection(uid).add(notification_data)
        print(f"✅ Study reminder notification created for user {uid}")
        
        # Send email notification
        user_email = get_user_email(uid)
        if user_email:
            user_doc = _user_doc(uid).get()
            user_name = "there"
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                user_name = user_data.get("displayName") or user_data.get("name") or "there"
            
            subject, html_content, text_content = get_study_reminder_template(user_name)
            
            email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        
        return True
        
    except Exception as e:
        print(f"Error sending study reminder: {e}")
        return False


def send_social_update(uid: str, friend_name: str = "A friend", action: str = "challenged you") -> bool:
    """
    Send social update notification (in-app + email).
    
    Args:
        uid: User ID
        friend_name: Name of the friend who triggered the update
        action: What action happened (e.g., "challenged you", "commented on your post")
    
    Returns:
        True if notification was created successfully
    """
    try:
        # Check if user has social updates enabled
        settings = get_user_notification_settings(uid)
        if not settings.get("social_updates"):
            print(f"Social updates disabled for user {uid}")
            return False
        
        # Create in-app notification
        now = datetime.now(timezone.utc)
        notification_data = {
            "type": "social_update",
            "title": "New Social Update",
            "message": f"{friend_name} {action}!",
            "is_read": False,
            "created_at": now,
            "action_url": "/socialhub",
            "metadata": {
                "friend_name": friend_name,
                "action": action,
            },
        }
        
        _notifications_collection(uid).add(notification_data)
        print(f"✅ Social update notification created for user {uid}")
        
        # Send email notification
        user_email = get_user_email(uid)
        if user_email:
            user_doc = _user_doc(uid).get()
            user_name = "there"
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                user_name = user_data.get("displayName") or user_data.get("name") or "there"
            
            email_service.send_email(
                to_email=user_email,
                subject=f"🎉 {friend_name} {action}",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f5f7fa;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f7fa; padding: 40px 20px;">
                        <tr>
                            <td align="center">
                                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); overflow: hidden;">
                                    <!-- Header -->
                                    <tr>
                                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                            <div style="font-size: 60px; margin-bottom: 15px;">👥</div>
                                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">New Social Update!</h1>
                                        </td>
                                    </tr>
                                    
                                    <!-- Content -->
                                    <tr>
                                        <td style="padding: 40px 30px;">
                                            <p style="margin: 0 0 20px; font-size: 16px; color: #4a5568; line-height: 1.6;">
                                                Hi {user_name},
                                            </p>
                                            
                                            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; padding: 25px; margin: 25px 0; text-align: center;">
                                                <p style="margin: 0; font-size: 20px; color: #ffffff; font-weight: 600;">
                                                    {friend_name} {action}!
                                                </p>
                                            </div>
                                            
                                            <p style="margin: 20px 0; font-size: 16px; color: #4a5568; line-height: 1.6;">
                                                Check out what's happening in your social hub and stay connected with your friends!
                                            </p>
                                            
                                            <!-- CTA Button -->
                                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                                <tr>
                                                    <td align="center">
                                                        <a href="http://localhost:8080/socialhub" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                                            View Social Hub
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    
                                    <!-- Footer -->
                                    <tr>
                                        <td style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                            <p style="margin: 0 0 10px; font-size: 14px; color: #718096;">
                                                Stay connected with your wellness community! 💙
                                            </p>
                                            <p style="margin: 0; font-size: 12px; color: #a0aec0;">
                                                This is an automated notification from WAD2 Project
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """,
                text_content=f"Hi {user_name},\n\n{friend_name} {action}!\n\nCheck out what's happening in your social hub.\n\nBest regards,\nWAD2 Project Team"
            )
            print(f"✅ Social update email sent to {user_email}")
        
        return True
        
    except Exception as e:
        print(f"Error sending social update: {e}")
        return False

