"""
Email Service for AUTOOS Authentication and Payment System

Handles sending transactional emails for:
- Email verification
- Password reset
- Welcome emails
- Payment confirmations
- Trial notifications
- Subscription updates
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@autoos.ai")
        self.from_name = os.getenv("FROM_NAME", "AUTOOS")
        self.base_url = os.getenv("BASE_URL", "http://localhost:3000")

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email using SMTP"""
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
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_email(
        self, to_email: str, username: str, verification_token: str
    ) -> bool:
        """Send email verification link"""
        verification_url = f"{self.base_url}/auth/verify?token={verification_token}"

        subject = "Verify Your AUTOOS Account"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to AUTOOS! 🚀</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Thanks for signing up! Please verify your email address to activate your account and start your <strong>30-day free trial</strong>.</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                    <p><strong>Your Free Trial Includes:</strong></p>
                    <ul>
                        <li>30 days of full access</li>
                        <li>10 workflows per month</li>
                        <li>2 concurrent agents</li>
                        <li>No credit card required</li>
                    </ul>
                    <p>This link will expire in 24 hours.</p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to AUTOOS!

        Hi {username},

        Thanks for signing up! Please verify your email address to activate your account.

        Verification link: {verification_url}

        This link will expire in 24 hours.

        Your Free Trial Includes:
        - 30 days of full access
        - 10 workflows per month
        - 2 concurrent agents
        - No credit card required

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(
        self, to_email: str, username: str, reset_token: str
    ) -> bool:
        """Send password reset link"""
        reset_url = f"{self.base_url}/auth/reset-password?token={reset_token}"

        subject = "Reset Your AUTOOS Password"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Your password will remain unchanged</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        Hi {username},

        We received a request to reset your password.

        Reset link: {reset_url}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email. Your password will remain unchanged.

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_welcome_email(self, to_email: str, username: str, trial_end_date: str) -> bool:
        """Send welcome email after successful verification"""
        subject = "Welcome to AUTOOS - Your Free Trial Has Started! 🎉"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .feature-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to AUTOOS! 🎉</h1>
                    <p>Your 30-Day Free Trial Has Started</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your account is now active! Your free trial ends on <strong>{trial_end_date}</strong>.</p>
                    
                    <div class="feature-box">
                        <h3>🚀 What You Can Do:</h3>
                        <ul>
                            <li>Create up to 10 workflows per month</li>
                            <li>Deploy 2 concurrent AI agents</li>
                            <li>Access all core features</li>
                            <li>No credit card required</li>
                        </ul>
                    </div>

                    <div class="feature-box">
                        <h3>📚 Getting Started:</h3>
                        <ol>
                            <li>Submit your first intent</li>
                            <li>Watch AI agents execute your workflow</li>
                            <li>Monitor progress in real-time</li>
                            <li>Review audit trails and metrics</li>
                        </ol>
                    </div>

                    <p style="text-align: center;">
                        <a href="{self.base_url}/dashboard" class="button">Go to Dashboard</a>
                    </p>

                    <p>Need help? Check out our <a href="{self.base_url}/docs">documentation</a> or contact support.</p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to AUTOOS!

        Hi {username},

        Your account is now active! Your free trial ends on {trial_end_date}.

        What You Can Do:
        - Create up to 10 workflows per month
        - Deploy 2 concurrent AI agents
        - Access all core features
        - No credit card required

        Getting Started:
        1. Submit your first intent
        2. Watch AI agents execute your workflow
        3. Monitor progress in real-time
        4. Review audit trails and metrics

        Dashboard: {self.base_url}/dashboard

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_payment_confirmation_email(
        self, to_email: str, username: str, amount: float, currency: str, plan: str
    ) -> bool:
        """Send payment confirmation email"""
        subject = f"Payment Confirmed - {plan.title()} Plan"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .receipt {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .receipt-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .total {{ font-size: 20px; font-weight: bold; color: #10b981; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Thank you for your payment! Your subscription is now active.</p>
                    
                    <div class="receipt">
                        <h3>Payment Receipt</h3>
                        <div class="receipt-row">
                            <span>Plan:</span>
                            <span><strong>{plan.title()}</strong></span>
                        </div>
                        <div class="receipt-row">
                            <span>Amount:</span>
                            <span class="total">{currency} {amount:.2f}</span>
                        </div>
                        <div class="receipt-row">
                            <span>Date:</span>
                            <span>{datetime.now().strftime('%B %d, %Y')}</span>
                        </div>
                    </div>

                    <p>You can view your invoice and manage your subscription in your account settings.</p>
                    <p style="text-align: center;">
                        <a href="{self.base_url}/billing" style="display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">View Invoice</a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Payment Confirmed

        Hi {username},

        Thank you for your payment! Your subscription is now active.

        Payment Receipt:
        - Plan: {plan.title()}
        - Amount: {currency} {amount:.2f}
        - Date: {datetime.now().strftime('%B %d, %Y')}

        View Invoice: {self.base_url}/billing

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_subscription_update_email(
        self, to_email: str, username: str, old_plan: str, new_plan: str, action: str
    ) -> bool:
        """Send subscription update notification"""
        subject = f"Subscription {action.title()} - {new_plan.title()} Plan"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Subscription {action.title()}</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your subscription has been {action}d successfully.</p>
                    
                    <div class="info-box">
                        <p><strong>Previous Plan:</strong> {old_plan.title()}</p>
                        <p><strong>New Plan:</strong> {new_plan.title()}</p>
                        <p><strong>Effective Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    </div>

                    <p>You can manage your subscription anytime in your account settings.</p>
                    <p style="text-align: center;">
                        <a href="{self.base_url}/subscription" style="display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">Manage Subscription</a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Subscription {action.title()}

        Hi {username},

        Your subscription has been {action}d successfully.

        Previous Plan: {old_plan.title()}
        New Plan: {new_plan.title()}
        Effective Date: {datetime.now().strftime('%B %d, %Y')}

        Manage Subscription: {self.base_url}/subscription

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_trial_expiration_warning(
        self, to_email: str, username: str, days_remaining: int, credits_remaining: int
    ) -> bool:
        """Send trial expiration warning email"""
        urgency = "🔴" if days_remaining <= 1 else "⚠️" if days_remaining <= 3 else "📅"
        subject = f"{urgency} Your AUTOOS Trial Expires in {days_remaining} Day{'s' if days_remaining != 1 else ''}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .warning-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{urgency} Trial Ending Soon</h1>
                    <p style="font-size: 24px; margin: 10px 0;">{days_remaining} Day{'s' if days_remaining != 1 else ''} Remaining</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your AUTOOS free trial is ending soon!</p>
                    
                    <div class="warning-box">
                        <h3>Trial Status:</h3>
                        <ul>
                            <li><strong>Days Remaining:</strong> {days_remaining}</li>
                            <li><strong>Credits Remaining:</strong> {credits_remaining}</li>
                        </ul>
                    </div>

                    <p><strong>Don't lose access to:</strong></p>
                    <ul>
                        <li>Your workflow history and data</li>
                        <li>AI agent capabilities</li>
                        <li>Real-time monitoring and analytics</li>
                    </ul>

                    <p style="text-align: center;">
                        <a href="{self.base_url}/pricing" class="button">Upgrade Now</a>
                    </p>

                    <p style="text-align: center; color: #666; font-size: 14px;">
                        Plans start at just $9.99/month
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        {urgency} Trial Ending Soon

        Hi {username},

        Your AUTOOS free trial is ending soon!

        Trial Status:
        - Days Remaining: {days_remaining}
        - Credits Remaining: {credits_remaining}

        Don't lose access to:
        - Your workflow history and data
        - AI agent capabilities
        - Real-time monitoring and analytics

        Upgrade Now: {self.base_url}/pricing

        Plans start at just $9.99/month

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)

    def send_trial_expired_email(self, to_email: str, username: str) -> bool:
        """Send trial expired notification"""
        subject = "Your AUTOOS Trial Has Ended"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Trial Ended</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your 30-day free trial has ended. To continue using AUTOOS, please upgrade to a paid plan.</p>
                    
                    <p><strong>Your data is safe!</strong> All your workflows and settings are preserved and will be available when you upgrade.</p>

                    <p style="text-align: center;">
                        <a href="{self.base_url}/pricing" class="button">View Plans & Upgrade</a>
                    </p>

                    <p>Thank you for trying AUTOOS. We hope to see you back soon!</p>
                </div>
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Trial Ended

        Hi {username},

        Your 30-day free trial has ended. To continue using AUTOOS, please upgrade to a paid plan.

        Your data is safe! All your workflows and settings are preserved and will be available when you upgrade.

        View Plans: {self.base_url}/pricing

        Thank you for trying AUTOOS. We hope to see you back soon!

        © 2024 AUTOOS. All rights reserved.
        """

        return self._send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
