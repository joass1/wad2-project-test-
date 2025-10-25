#!/usr/bin/env python3
"""
Email Configuration Setup Script for WAD2 Project Team
This script helps team members set up email notifications quickly.
"""

import os
import sys
from pathlib import Path

def setup_email_config():
    """Set up email configuration for the team."""
    
    print("🚀 WAD2 Project Email Configuration Setup")
    print("=" * 50)
    
    # Check if we're in the backend directory
    backend_dir = Path(__file__).parent
    if not (backend_dir / "app").exists():
        print("❌ Error: Please run this script from the backend directory")
        return False
    
    # Check if .env already exists
    env_file = backend_dir / ".env"
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    print("\n📧 Email Configuration Options:")
    print("1. Gmail (Recommended for development)")
    print("2. SendGrid (Recommended for production)")
    print("3. Custom SMTP")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        setup_gmail_config(env_file)
    elif choice == "2":
        setup_sendgrid_config(env_file)
    elif choice == "3":
        setup_custom_config(env_file)
    else:
        print("❌ Invalid choice")
        return False
    
    print("\n✅ Email configuration completed!")
    print("🔄 Please restart your backend server to load the new configuration")
    return True

def setup_gmail_config(env_file):
    """Set up Gmail configuration."""
    print("\n📧 Gmail Configuration")
    print("You'll need a Gmail account with 2FA enabled and an App Password")
    
    email = input("Gmail address: ").strip()
    app_password = input("App Password (16 characters): ").strip()
    
    config = f"""# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER={email}
SMTP_PASSWORD={app_password}
SMTP_FROM_EMAIL={email}
SMTP_FROM_NAME=WAD2 Project Team
"""
    
    env_file.write_text(config)
    print("✅ Gmail configuration saved!")

def setup_sendgrid_config(env_file):
    """Set up SendGrid configuration."""
    print("\n📧 SendGrid Configuration")
    print("You'll need a SendGrid account and API key")
    
    api_key = input("SendGrid API Key: ").strip()
    from_email = input("Verified sender email: ").strip()
    
    config = f"""# SendGrid SMTP Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD={api_key}
SMTP_FROM_EMAIL={from_email}
SMTP_FROM_NAME=WAD2 Project Team
"""
    
    env_file.write_text(config)
    print("✅ SendGrid configuration saved!")

def setup_custom_config(env_file):
    """Set up custom SMTP configuration."""
    print("\n📧 Custom SMTP Configuration")
    
    host = input("SMTP Host: ").strip()
    port = input("SMTP Port (default 587): ").strip() or "587"
    username = input("SMTP Username: ").strip()
    password = input("SMTP Password: ").strip()
    from_email = input("From Email: ").strip()
    from_name = input("From Name (default 'WAD2 Project Team'): ").strip() or "WAD2 Project Team"
    
    config = f"""# Custom SMTP Configuration
SMTP_HOST={host}
SMTP_PORT={port}
SMTP_USER={username}
SMTP_PASSWORD={password}
SMTP_FROM_EMAIL={from_email}
SMTP_FROM_NAME={from_name}
"""
    
    env_file.write_text(config)
    print("✅ Custom SMTP configuration saved!")

def test_email_config():
    """Test the email configuration."""
    print("\n🧪 Testing Email Configuration...")
    
    try:
        from app.core.email import email_service
        
        if not email_service.username or not email_service.password:
            print("❌ Email credentials not configured")
            return False
        
        print(f"✅ SMTP Host: {email_service.host}")
        print(f"✅ SMTP Port: {email_service.port}")
        print(f"✅ SMTP User: {email_service.username}")
        print(f"✅ From Email: {email_service.from_email}")
        
        # Test sending a simple email
        test_email = input("\nEnter your email to send a test message: ").strip()
        if test_email:
            success = email_service.send_email(
                to_email=test_email,
                subject="WAD2 Project - Email Test",
                html_content="<h1>Email Test Successful!</h1><p>Your email configuration is working correctly.</p>",
                text_content="Email Test Successful! Your email configuration is working correctly."
            )
            
            if success:
                print("✅ Test email sent successfully!")
                print("📧 Check your inbox (and spam folder)")
            else:
                print("❌ Failed to send test email")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing email configuration: {e}")
        return False

if __name__ == "__main__":
    print("WAD2 Project Email Setup")
    print("=" * 30)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_email_config()
    else:
        setup_email_config()
        
        # Ask if user wants to test
        test = input("\nDo you want to test the email configuration? (y/N): ").lower()
        if test == 'y':
            test_email_config()
