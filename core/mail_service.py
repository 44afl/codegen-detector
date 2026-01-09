import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")
    
    def send_email(self, to_email, subject, html_body):
        if not self.smtp_user or not self.smtp_password:
            print(f"Email not configured. Would send to {to_email}: {subject}")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_password_reset(self, to_email, token):
        reset_url = f"{self.app_url}/reset-password?token={token}"
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the link below to proceed:</p>
                <p>
                    <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <p style="font-size: 12px; color: #666;">CodeGen Detector Team</p>
            </body>
        </html>
        """
        
        return self.send_email(to_email, "Password Reset Request", html)
    
    def send_welcome_email(self, to_email, full_name):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Welcome to CodeGen Detector!</h2>
                <p>Hi {full_name or 'there'},</p>
                <p>Thank you for signing up. Your account has been created successfully.</p>
                <p>You can now start analyzing code to detect if it's machine-generated or human-written.</p>
                <p>
                    <a href="{self.app_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Get Started
                    </a>
                </p>
                <hr>
                <p style="font-size: 12px; color: #666;">CodeGen Detector Team</p>
            </body>
        </html>
        """
        
        return self.send_email(to_email, "Welcome to CodeGen Detector", html)
    
    def send_subscription_confirmation(self, to_email, plan_type, end_date):
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Subscription Confirmed</h2>
                <p>Your subscription has been activated:</p>
                <ul>
                    <li><strong>Plan:</strong> {plan_type}</li>
                    <li><strong>Valid until:</strong> {end_date}</li>
                </ul>
                <p>Thank you for subscribing!</p>
                <hr>
                <p style="font-size: 12px; color: #666;">CodeGen Detector Team</p>
            </body>
        </html>
        """
        
        return self.send_email(to_email, "Subscription Confirmation", html)
