import random
import string
import logging
from aiosmtplib import send
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP."""
    digits = string.digits
    return "".join(random.choice(digits) for _ in range(length))

async def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email asynchronously using aiosmtplib."""
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    message["To"] = to_email

    try:
        await send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

async def send_verification_email(email: str, name: str, otp: str):
    """Send OTP for email verification."""
    subject = "Verify Your Account"
    body = f"""Hello {name},

Thank you for registering at POTG. Please use the following OTP to verify your account:

{otp}

This OTP is valid for 10 minutes.

Thank you,
The POTG Team
"""
    await send_email(email, subject, body)

async def send_forget_password_email(email: str, name: str, otp: str):
    """Send OTP for password reset."""
    subject = "Reset Your Password"
    body = f"""Hello {name},

You requested to reset your password. Please use the following OTP to proceed:

{otp}

This OTP is valid for 10 minutes. If you did not request a password reset, please ignore this email.

Thank you,
The POTG Team
"""
    await send_email(email, subject, body)
