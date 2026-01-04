"""
Email service module for sending transactional emails via Resend.

Environment variables required:
- RESEND_API_KEY: API key from Resend dashboard
- FROM_EMAIL: Sender email address (default: onboarding@resend.dev for testing)
- FRONTEND_URL: Base URL for links in emails (default: http://localhost:5173)
"""

import os
import logging
from typing import Optional

from dotenv import load_dotenv
import resend

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Email configuration from environment
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Initialize Resend API key
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def is_email_configured() -> bool:
    """Check if email service is properly configured."""
    return bool(RESEND_API_KEY)


def get_password_reset_email_html(reset_url: str) -> str:
    """Generate HTML content for password reset email."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #0f0f23; color: #ffffff;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 500px; width: 100%; border-collapse: collapse;">
                    <!-- Logo/Header -->
                    <tr>
                        <td align="center" style="padding-bottom: 30px;">
                            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #8b5cf6, #ec4899, #f97316); border-radius: 16px; display: inline-block; line-height: 60px; font-size: 24px;">
                                &#10024;
                            </div>
                            <h1 style="margin: 20px 0 0; font-size: 24px; font-weight: 600; color: #ffffff;">
                                HHH Daily Tracker
                            </h1>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="background: rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
                                Reset Your Password
                            </h2>
                            <p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
                                You requested to reset your password for your HHH Daily Tracker account. Click the button below to set a new password.
                            </p>

                            <!-- Reset Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{reset_url}"
                                           style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                                            Reset Password
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 20px 0 0; font-size: 14px; line-height: 1.6; color: rgba(255, 255, 255, 0.5);">
                                This link will expire in <strong style="color: #f59e0b;">15 minutes</strong> for security reasons.
                            </p>

                            <p style="margin: 20px 0 0; font-size: 14px; line-height: 1.6; color: rgba(255, 255, 255, 0.5);">
                                If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.
                            </p>

                            <!-- Fallback Link -->
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                <p style="margin: 0; font-size: 12px; color: rgba(255, 255, 255, 0.4);">
                                    If the button doesn't work, copy and paste this link into your browser:
                                </p>
                                <p style="margin: 10px 0 0; font-size: 12px; word-break: break-all; color: #8b5cf6;">
                                    {reset_url}
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="padding-top: 30px;">
                            <p style="margin: 0; font-size: 12px; color: rgba(255, 255, 255, 0.4);">
                                Track your Health, Happiness & Hela daily
                            </p>
                            <p style="margin: 10px 0 0; font-size: 12px; color: rgba(255, 255, 255, 0.3);">
                                &copy; 2024 HHH Daily Tracker
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def get_password_reset_email_text(reset_url: str) -> str:
    """Generate plain text content for password reset email."""
    return f"""
Reset Your Password - HHH Daily Tracker

You requested to reset your password for your HHH Daily Tracker account.

Click the link below to set a new password (valid for 15 minutes):
{reset_url}

If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_password_reset_email(to_email: str, reset_token: str) -> tuple[bool, Optional[str]]:
    """
    Send a password reset email to the user.

    Args:
        to_email: Recipient email address
        reset_token: The password reset token

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not is_email_configured():
        logger.warning("Email service not configured (RESEND_API_KEY not set)")
        return False, "Email service not configured"

    # Construct reset URL
    # Use hash-based routing for compatibility with HashRouter (used for GitHub Pages)
    reset_url = f"{FRONTEND_URL}/#/reset-password?token={reset_token}"

    try:
        params = {
            "from": f"HHH Daily Tracker <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": "Reset your HHH Daily Tracker password",
            "html": get_password_reset_email_html(reset_url),
            "text": get_password_reset_email_text(reset_url),
        }

        email_response = resend.Emails.send(params)

        if email_response and email_response.get("id"):
            logger.info(f"Password reset email sent successfully to {to_email}, id: {email_response['id']}")
            return True, None
        else:
            logger.error(f"Failed to send password reset email to {to_email}: No email ID returned")
            return False, "Failed to send email"

    except resend.exceptions.ResendError as e:
        logger.error(f"Resend API error sending email to {to_email}: {str(e)}")
        return False, f"Email service error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
