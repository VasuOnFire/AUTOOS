"""
Email Templates for AUTOOS

Centralized email template definitions for easy customization and maintenance.
All templates support both HTML and plain text formats.
"""

from typing import Dict, Any


class EmailTemplates:
    """Email template definitions"""

    # Base styles used across all templates
    BASE_STYLES = """
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
        .feature-box { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
        .receipt { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .receipt-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
    """

    @staticmethod
    def get_base_template(title: str, content: str) -> str:
        """Get base HTML template with content"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>{EmailTemplates.BASE_STYLES}</style>
        </head>
        <body>
            <div class="container">
                {content}
                <div class="footer">
                    <p>© 2024 AUTOOS. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def verification_email(username: str, verification_url: str) -> Dict[str, str]:
        """Email verification template"""
        html = EmailTemplates.get_base_template(
            "Verify Email",
            f"""
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
            """,
        )

        text = f"""
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

        return {"html": html, "text": text, "subject": "Verify Your AUTOOS Account"}

    @staticmethod
    def password_reset(username: str, reset_url: str) -> Dict[str, str]:
        """Password reset template"""
        html = EmailTemplates.get_base_template(
            "Password Reset",
            f"""
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
            """,
        )

        text = f"""
        Password Reset Request

        Hi {username},

        We received a request to reset your password.

        Reset link: {reset_url}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email. Your password will remain unchanged.

        © 2024 AUTOOS. All rights reserved.
        """

        return {"html": html, "text": text, "subject": "Reset Your AUTOOS Password"}

    @staticmethod
    def welcome_email(username: str, trial_end_date: str, dashboard_url: str) -> Dict[str, str]:
        """Welcome email template"""
        html = EmailTemplates.get_base_template(
            "Welcome",
            f"""
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
                    <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                </p>
            </div>
            """,
        )

        text = f"""
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

        Dashboard: {dashboard_url}

        © 2024 AUTOOS. All rights reserved.
        """

        return {
            "html": html,
            "text": text,
            "subject": "Welcome to AUTOOS - Your Free Trial Has Started! 🎉",
        }

    @staticmethod
    def trial_activation(username: str, trial_end_date: str) -> Dict[str, str]:
        """Trial activation confirmation template"""
        return EmailTemplates.welcome_email(username, trial_end_date, "")

    @staticmethod
    def trial_warning(username: str, days_remaining: int, credits_remaining: int, pricing_url: str) -> Dict[str, str]:
        """Trial expiration warning template"""
        urgency = "🔴" if days_remaining <= 1 else "⚠️" if days_remaining <= 3 else "📅"
        
        html = EmailTemplates.get_base_template(
            "Trial Warning",
            f"""
            <div class="header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <h1>{urgency} Trial Ending Soon</h1>
                <p style="font-size: 24px; margin: 10px 0;">{days_remaining} Day{'s' if days_remaining != 1 else ''} Remaining</p>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>Your AUTOOS free trial is ending soon!</p>
                
                <div class="warning">
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
                    <a href="{pricing_url}" class="button" style="background: #f59e0b;">Upgrade Now</a>
                </p>

                <p style="text-align: center; color: #666; font-size: 14px;">
                    Plans start at just $9.99/month
                </p>
            </div>
            """,
        )

        text = f"""
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

        Upgrade Now: {pricing_url}

        Plans start at just $9.99/month

        © 2024 AUTOOS. All rights reserved.
        """

        return {
            "html": html,
            "text": text,
            "subject": f"{urgency} Your AUTOOS Trial Expires in {days_remaining} Day{'s' if days_remaining != 1 else ''}",
        }

    @staticmethod
    def trial_expired(username: str, pricing_url: str) -> Dict[str, str]:
        """Trial expired notification template"""
        html = EmailTemplates.get_base_template(
            "Trial Expired",
            f"""
            <div class="header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                <h1>Trial Ended</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>Your 30-day free trial has ended. To continue using AUTOOS, please upgrade to a paid plan.</p>
                
                <p><strong>Your data is safe!</strong> All your workflows and settings are preserved and will be available when you upgrade.</p>

                <p style="text-align: center;">
                    <a href="{pricing_url}" class="button" style="background: #ef4444;">View Plans & Upgrade</a>
                </p>

                <p>Thank you for trying AUTOOS. We hope to see you back soon!</p>
            </div>
            """,
        )

        text = f"""
        Trial Ended

        Hi {username},

        Your 30-day free trial has ended. To continue using AUTOOS, please upgrade to a paid plan.

        Your data is safe! All your workflows and settings are preserved and will be available when you upgrade.

        View Plans: {pricing_url}

        Thank you for trying AUTOOS. We hope to see you back soon!

        © 2024 AUTOOS. All rights reserved.
        """

        return {"html": html, "text": text, "subject": "Your AUTOOS Trial Has Ended"}

    @staticmethod
    def payment_confirmation(username: str, amount: float, currency: str, plan: str, date: str, invoice_url: str) -> Dict[str, str]:
        """Payment confirmation template"""
        html = EmailTemplates.get_base_template(
            "Payment Confirmed",
            f"""
            <div class="header" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
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
                        <span style="font-size: 20px; font-weight: bold; color: #10b981;">{currency} {amount:.2f}</span>
                    </div>
                    <div class="receipt-row">
                        <span>Date:</span>
                        <span>{date}</span>
                    </div>
                </div>

                <p>You can view your invoice and manage your subscription in your account settings.</p>
                <p style="text-align: center;">
                    <a href="{invoice_url}" class="button" style="background: #10b981;">View Invoice</a>
                </p>
            </div>
            """,
        )

        text = f"""
        Payment Confirmed

        Hi {username},

        Thank you for your payment! Your subscription is now active.

        Payment Receipt:
        - Plan: {plan.title()}
        - Amount: {currency} {amount:.2f}
        - Date: {date}

        View Invoice: {invoice_url}

        © 2024 AUTOOS. All rights reserved.
        """

        return {"html": html, "text": text, "subject": f"Payment Confirmed - {plan.title()} Plan"}

    @staticmethod
    def subscription_update(username: str, old_plan: str, new_plan: str, action: str, date: str, manage_url: str) -> Dict[str, str]:
        """Subscription update template"""
        html = EmailTemplates.get_base_template(
            "Subscription Update",
            f"""
            <div class="header">
                <h1>Subscription {action.title()}</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>Your subscription has been {action}d successfully.</p>
                
                <div class="feature-box">
                    <p><strong>Previous Plan:</strong> {old_plan.title()}</p>
                    <p><strong>New Plan:</strong> {new_plan.title()}</p>
                    <p><strong>Effective Date:</strong> {date}</p>
                </div>

                <p>You can manage your subscription anytime in your account settings.</p>
                <p style="text-align: center;">
                    <a href="{manage_url}" class="button">Manage Subscription</a>
                </p>
            </div>
            """,
        )

        text = f"""
        Subscription {action.title()}

        Hi {username},

        Your subscription has been {action}d successfully.

        Previous Plan: {old_plan.title()}
        New Plan: {new_plan.title()}
        Effective Date: {date}

        Manage Subscription: {manage_url}

        © 2024 AUTOOS. All rights reserved.
        """

        return {
            "html": html,
            "text": text,
            "subject": f"Subscription {action.title()} - {new_plan.title()} Plan",
        }

    @staticmethod
    def qr_payment_confirmation(username: str, amount: float, currency: str, plan: str, payment_method: str) -> Dict[str, str]:
        """QR code payment confirmation template"""
        html = EmailTemplates.get_base_template(
            "QR Payment Confirmed",
            f"""
            <div class="header" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <h1>✅ Payment Received</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>We've received your payment via {payment_method}. Your subscription is now active!</p>
                
                <div class="receipt">
                    <h3>Payment Details</h3>
                    <div class="receipt-row">
                        <span>Plan:</span>
                        <span><strong>{plan.title()}</strong></span>
                    </div>
                    <div class="receipt-row">
                        <span>Amount:</span>
                        <span style="font-size: 20px; font-weight: bold; color: #10b981;">{currency} {amount:.2f}</span>
                    </div>
                    <div class="receipt-row">
                        <span>Payment Method:</span>
                        <span>{payment_method}</span>
                    </div>
                </div>

                <p>Thank you for choosing AUTOOS!</p>
            </div>
            """,
        )

        text = f"""
        Payment Received

        Hi {username},

        We've received your payment via {payment_method}. Your subscription is now active!

        Payment Details:
        - Plan: {plan.title()}
        - Amount: {currency} {amount:.2f}
        - Payment Method: {payment_method}

        Thank you for choosing AUTOOS!

        © 2024 AUTOOS. All rights reserved.
        """

        return {"html": html, "text": text, "subject": f"Payment Received - {plan.title()} Plan"}

    @staticmethod
    def invoice_email(username: str, invoice_number: str, amount: float, currency: str, download_url: str) -> Dict[str, str]:
        """Invoice email template"""
        html = EmailTemplates.get_base_template(
            "Invoice",
            f"""
            <div class="header">
                <h1>Invoice #{invoice_number}</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                <p>Your invoice is ready for download.</p>
                
                <div class="receipt">
                    <div class="receipt-row">
                        <span>Invoice Number:</span>
                        <span><strong>#{invoice_number}</strong></span>
                    </div>
                    <div class="receipt-row">
                        <span>Amount:</span>
                        <span style="font-size: 20px; font-weight: bold;">{currency} {amount:.2f}</span>
                    </div>
                </div>

                <p style="text-align: center;">
                    <a href="{download_url}" class="button">Download Invoice</a>
                </p>
            </div>
            """,
        )

        text = f"""
        Invoice #{invoice_number}

        Hi {username},

        Your invoice is ready for download.

        Invoice Number: #{invoice_number}
        Amount: {currency} {amount:.2f}

        Download: {download_url}

        © 2024 AUTOOS. All rights reserved.
        """

        return {"html": html, "text": text, "subject": f"Invoice #{invoice_number} - AUTOOS"}


# Export singleton
email_templates = EmailTemplates()
