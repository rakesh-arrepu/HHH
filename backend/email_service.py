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


# ==== BASE TEMPLATE ====

def get_email_base_template(title: str, main_content_html: str) -> str:
    """
    Generate base HTML template for all emails with consistent HHH branding.

    Args:
        title: Email title for the <title> tag and page title
        main_content_html: The email-specific HTML content to insert in the main content area

    Returns:
        Complete HTML email string with HHH branding
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
                            {main_content_html}
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


# ==== HELPER FUNCTIONS ====

def _send_email(to_email: str, subject: str, html: str, text: str) -> tuple[bool, Optional[str]]:
    """
    Centralized email sending function using Resend API.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html: HTML email content
        text: Plain text email content

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not is_email_configured():
        logger.warning("Email service not configured (RESEND_API_KEY not set)")
        return False, "Email service not configured"

    try:
        params = {
            "from": f"HHH Daily Tracker <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html,
            "text": text,
        }

        email_response = resend.Emails.send(params)

        if email_response and email_response.get("id"):
            logger.info(f"Email sent successfully to {to_email}, id: {email_response['id']}, subject: {subject}")
            return True, None
        else:
            logger.error(f"Failed to send email to {to_email}: No email ID returned")
            return False, "Failed to send email"

    except resend.exceptions.ResendError as e:
        logger.error(f"Resend API error sending email to {to_email}: {str(e)}")
        return False, f"Email service error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


# ==== PASSWORD RESET (EXISTING) ====

def get_password_reset_email_html(reset_url: str) -> str:
    """Generate HTML content for password reset email."""
    main_content = f"""
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
"""
    return get_email_base_template("Reset Your Password", main_content)


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
    # Construct reset URL
    # Use hash-based routing for compatibility with HashRouter (used for GitHub Pages)
    reset_url = f"{FRONTEND_URL}/#/reset-password?token={reset_token}"

    return _send_email(
        to_email=to_email,
        subject="Reset your HHH Daily Tracker password",
        html=get_password_reset_email_html(reset_url),
        text=get_password_reset_email_text(reset_url)
    )


# ==== WELCOME EMAIL ====

def get_welcome_email_html(user_name: str, login_url: str) -> str:
    """Generate HTML content for welcome email."""
    main_content = f"""
<h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
    Welcome to HHH Daily Tracker, {user_name}!
</h2>
<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    We're excited to have you on board! HHH Daily Tracker helps you build healthy habits by tracking three essential areas of your life:
</p>

<!-- Features List -->
<div style="margin: 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border-left: 3px solid #8b5cf6;">
    <p style="margin: 0 0 12px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        <strong style="color: #f97316;">🏃 Health</strong> - Track daily activities from 52 different types with calorie tracking
    </p>
    <p style="margin: 0 0 12px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        <strong style="color: #ec4899;">😊 Happiness</strong> - Log moments that bring you joy
    </p>
    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        <strong style="color: #8b5cf6;">💰 Hela (Money)</strong> - Monitor your financial progress
    </p>
</div>

<p style="margin: 20px 0; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    Build streaks, stay accountable, and join groups with friends and family to track progress together!
</p>

<!-- Get Started Button -->
<table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="{login_url}"
               style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                Get Started
            </a>
        </td>
    </tr>
</table>

<p style="margin: 20px 0 0; font-size: 14px; line-height: 1.6; color: rgba(255, 255, 255, 0.5);">
    Start logging your activities today and watch your streaks grow!
</p>
"""
    return get_email_base_template("Welcome to HHH Daily Tracker", main_content)


def get_welcome_email_text(user_name: str, login_url: str) -> str:
    """Generate plain text content for welcome email."""
    return f"""
Welcome to HHH Daily Tracker, {user_name}!

We're excited to have you on board! HHH Daily Tracker helps you build healthy habits by tracking three essential areas of your life:

🏃 HEALTH - Track daily activities from 52 different types with calorie tracking
😊 HAPPINESS - Log moments that bring you joy
💰 HELA (Money) - Monitor your financial progress

Build streaks, stay accountable, and join groups with friends and family to track progress together!

Get started now: {login_url}

Start logging your activities today and watch your streaks grow!

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_welcome_email(to_email: str, user_name: str) -> tuple[bool, Optional[str]]:
    """
    Send a welcome email to a newly registered user.

    Args:
        to_email: Recipient email address
        user_name: The user's name for personalization

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Construct login URL using hash routing for GitHub Pages compatibility
    login_url = f"{FRONTEND_URL}/#/"

    return _send_email(
        to_email=to_email,
        subject="Welcome to HHH Daily Tracker!",
        html=get_welcome_email_html(user_name, login_url),
        text=get_welcome_email_text(user_name, login_url)
    )


# ==== MEMBER ADDED EMAILS ====

def get_member_added_email_html_for_member(member_name: str, group_name: str, group_id: int, owner_name: str, group_url: str) -> str:
    """Generate HTML content for member-added email (sent to new member)."""
    main_content = f"""
<h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
    Hi {member_name}, you're now part of '{group_name}'!
</h2>
<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    <strong style="color: #ec4899;">{owner_name}</strong> added you to the group <strong style="color: #8b5cf6;">'{group_name}'</strong>.
</p>

<div style="margin: 20px 0; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border-left: 3px solid #8b5cf6;">
    <p style="margin: 0 0 10px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        You can now track your Health, Happiness, and Hela entries with the group!
    </p>
    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        Start logging your daily activities to build streaks together.
    </p>
</div>

<!-- View Group Button -->
<table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="{group_url}"
               style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                View Group
            </a>
        </td>
    </tr>
</table>
"""
    return get_email_base_template(f"You've been added to '{group_name}'", main_content)


def get_member_added_email_text_for_member(member_name: str, group_name: str, group_id: int, owner_name: str, group_url: str) -> str:
    """Generate plain text content for member-added email (sent to new member)."""
    return f"""
Hi {member_name}, you're now part of '{group_name}'!

{owner_name} added you to the group '{group_name}'.

You can now track your Health, Happiness, and Hela entries with the group! Start logging your daily activities to build streaks together.

View your group: {group_url}

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_member_added_email_to_member(
    to_email: str,
    member_name: str,
    group_name: str,
    group_id: int,
    owner_name: str
) -> tuple[bool, Optional[str]]:
    """
    Send email to a user who was added to a group.

    Args:
        to_email: New member's email address
        member_name: New member's name
        group_name: Name of the group
        group_id: ID of the group
        owner_name: Name of the group owner who added them

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Construct group URL using hash routing
    group_url = f"{FRONTEND_URL}/#/groups/{group_id}"

    # Truncate group name for subject if too long
    subject_group_name = group_name[:40] + "..." if len(group_name) > 40 else group_name

    return _send_email(
        to_email=to_email,
        subject=f"You've been added to '{subject_group_name}'",
        html=get_member_added_email_html_for_member(member_name, group_name, group_id, owner_name, group_url),
        text=get_member_added_email_text_for_member(member_name, group_name, group_id, owner_name, group_url)
    )


def get_member_added_email_html_for_owner(owner_name: str, member_name: str, member_email: str, group_name: str, group_id: int, group_url: str) -> str:
    """Generate HTML content for member-added email (sent to group owner)."""
    main_content = f"""
<h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
    Member Added Successfully
</h2>
<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    You've successfully added <strong style="color: #ec4899;">{member_name}</strong> (<span style="color: rgba(255, 255, 255, 0.6);">{member_email}</span>) to <strong style="color: #8b5cf6;">'{group_name}'</strong>.
</p>

<div style="margin: 20px 0; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border-left: 3px solid #8b5cf6;">
    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        They can now view and contribute to the group's activities. Keep building those streaks together!
    </p>
</div>

<!-- View Group Members Button -->
<table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="{group_url}"
               style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                View Group Members
            </a>
        </td>
    </tr>
</table>
"""
    return get_email_base_template(f"New member added to '{group_name}'", main_content)


def get_member_added_email_text_for_owner(owner_name: str, member_name: str, member_email: str, group_name: str, group_id: int, group_url: str) -> str:
    """Generate plain text content for member-added email (sent to group owner)."""
    return f"""
Member Added Successfully

You've successfully added {member_name} ({member_email}) to '{group_name}'.

They can now view and contribute to the group's activities. Keep building those streaks together!

View group members: {group_url}

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_member_added_email_to_owner(
    to_email: str,
    owner_name: str,
    member_name: str,
    member_email: str,
    group_name: str,
    group_id: int
) -> tuple[bool, Optional[str]]:
    """
    Send confirmation email to group owner after adding a member.

    Args:
        to_email: Owner's email address
        owner_name: Owner's name
        member_name: New member's name
        member_email: New member's email
        group_name: Name of the group
        group_id: ID of the group

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Construct group URL using hash routing
    group_url = f"{FRONTEND_URL}/#/groups/{group_id}"

    # Truncate group name for subject if too long
    subject_group_name = group_name[:40] + "..." if len(group_name) > 40 else group_name

    return _send_email(
        to_email=to_email,
        subject=f"New member added to '{subject_group_name}'",
        html=get_member_added_email_html_for_owner(owner_name, member_name, member_email, group_name, group_id, group_url),
        text=get_member_added_email_text_for_owner(owner_name, member_name, member_email, group_name, group_id, group_url)
    )


# ==== OWNERSHIP TRANSFER EMAILS ====

def get_ownership_transfer_email_html_for_new_owner(new_owner_name: str, group_name: str, group_id: int, previous_owner_name: str, group_url: str) -> str:
    """Generate HTML content for ownership transfer email (sent to new owner)."""
    main_content = f"""
<h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
    Group Ownership Transferred
</h2>
<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    <strong style="color: #ec4899;">{previous_owner_name}</strong> has transferred ownership of <strong style="color: #8b5cf6;">'{group_name}'</strong> to you.
</p>

<div style="margin: 20px 0; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border-left: 3px solid #8b5cf6;">
    <p style="margin: 0 0 15px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        <strong style="color: #ffffff;">As the new owner, you can now:</strong>
    </p>
    <p style="margin: 0 0 8px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.75);">
        ✓ Add or remove members
    </p>
    <p style="margin: 0 0 8px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.75);">
        ✓ Transfer ownership to another member
    </p>
    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.75);">
        ✓ Manage group settings
    </p>
</div>

<!-- Manage Group Button -->
<table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="{group_url}"
               style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                Manage Group
            </a>
        </td>
    </tr>
</table>
"""
    return get_email_base_template(f"You're now the owner of '{group_name}'", main_content)


def get_ownership_transfer_email_text_for_new_owner(new_owner_name: str, group_name: str, group_id: int, previous_owner_name: str, group_url: str) -> str:
    """Generate plain text content for ownership transfer email (sent to new owner)."""
    return f"""
Group Ownership Transferred

{previous_owner_name} has transferred ownership of '{group_name}' to you.

As the new owner, you can now:
✓ Add or remove members
✓ Transfer ownership to another member
✓ Manage group settings

Manage your group: {group_url}

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_ownership_transfer_email_to_new_owner(
    to_email: str,
    new_owner_name: str,
    group_name: str,
    group_id: int,
    previous_owner_name: str
) -> tuple[bool, Optional[str]]:
    """
    Send email to the new owner after ownership transfer.

    Args:
        to_email: New owner's email address
        new_owner_name: New owner's name
        group_name: Name of the group
        group_id: ID of the group
        previous_owner_name: Name of the previous owner

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Construct group URL using hash routing
    group_url = f"{FRONTEND_URL}/#/groups/{group_id}"

    # Truncate group name for subject if too long
    subject_group_name = group_name[:40] + "..." if len(group_name) > 40 else group_name

    return _send_email(
        to_email=to_email,
        subject=f"You're now the owner of '{subject_group_name}'",
        html=get_ownership_transfer_email_html_for_new_owner(new_owner_name, group_name, group_id, previous_owner_name, group_url),
        text=get_ownership_transfer_email_text_for_new_owner(new_owner_name, group_name, group_id, previous_owner_name, group_url)
    )


def get_ownership_transfer_email_html_for_previous_owner(previous_owner_name: str, group_name: str, group_id: int, new_owner_name: str, group_url: str) -> str:
    """Generate HTML content for ownership transfer email (sent to previous owner)."""
    main_content = f"""
<h2 style="margin: 0 0 20px; font-size: 20px; font-weight: 600; color: #ffffff;">
    Ownership Transfer Confirmed
</h2>
<p style="margin: 0 0 20px; font-size: 16px; line-height: 1.6; color: rgba(255, 255, 255, 0.7);">
    You've successfully transferred ownership of <strong style="color: #8b5cf6;">'{group_name}'</strong> to <strong style="color: #ec4899;">{new_owner_name}</strong>.
</p>

<div style="margin: 20px 0; padding: 20px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border-left: 3px solid #8b5cf6;">
    <p style="margin: 0 0 10px; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        You remain a member and can continue tracking your activities with the group.
    </p>
    <p style="margin: 0; font-size: 15px; line-height: 1.6; color: rgba(255, 255, 255, 0.85);">
        {new_owner_name} can now manage the group and its members.
    </p>
</div>

<!-- View Group Button -->
<table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
        <td align="center" style="padding: 20px 0;">
            <a href="{group_url}"
               style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 12px; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
                View Group
            </a>
        </td>
    </tr>
</table>
"""
    return get_email_base_template(f"You've transferred ownership of '{group_name}'", main_content)


def get_ownership_transfer_email_text_for_previous_owner(previous_owner_name: str, group_name: str, group_id: int, new_owner_name: str, group_url: str) -> str:
    """Generate plain text content for ownership transfer email (sent to previous owner)."""
    return f"""
Ownership Transfer Confirmed

You've successfully transferred ownership of '{group_name}' to {new_owner_name}.

You remain a member and can continue tracking your activities with the group. {new_owner_name} can now manage the group and its members.

View your group: {group_url}

---
Track your Health, Happiness & Hela daily
HHH Daily Tracker
"""


def send_ownership_transfer_email_to_previous_owner(
    to_email: str,
    previous_owner_name: str,
    group_name: str,
    group_id: int,
    new_owner_name: str
) -> tuple[bool, Optional[str]]:
    """
    Send confirmation email to the previous owner after ownership transfer.

    Args:
        to_email: Previous owner's email address
        previous_owner_name: Previous owner's name
        group_name: Name of the group
        group_id: ID of the group
        new_owner_name: Name of the new owner

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Construct group URL using hash routing
    group_url = f"{FRONTEND_URL}/#/groups/{group_id}"

    # Truncate group name for subject if too long
    subject_group_name = group_name[:40] + "..." if len(group_name) > 40 else group_name

    return _send_email(
        to_email=to_email,
        subject=f"You've transferred ownership of '{subject_group_name}'",
        html=get_ownership_transfer_email_html_for_previous_owner(previous_owner_name, group_name, group_id, new_owner_name, group_url),
        text=get_ownership_transfer_email_text_for_previous_owner(previous_owner_name, group_name, group_id, new_owner_name, group_url)
    )
