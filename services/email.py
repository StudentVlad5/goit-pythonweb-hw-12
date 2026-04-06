"""
Email Service Module
--------------------
This module handles sending emails for the application using the `fastapi_mail` library.
It supports sending verification emails for new registrations and password reset links.
"""

from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from services.auth import auth_service
from config.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Contacts Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: str, username: str, host: str):
    """
    Sends an email to verify the user's email address during registration.

    Generates a verification token and renders the `email_template.html` template.

    :param email: The recipient's email address.
    :type email: str
    :param username: The username to display in the email body.
    :type username: str
    :param host: The base URL of the application (e.g., http://localhost:8000).
    :type host: str
    :raises Exception: Logs any error that occurs during the email sending process.
    :return: None
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})

        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")

    except Exception as err:
        print("EMAIL ERROR:", err)

async def send_reset_password_email(email: str, username: str, host: str, reset_token: str):
    """
    Sends an email with a password reset link.

    Renders the `password_reset.html` template with a unique reset token.

    :param email: The recipient's email address.
    :type email: str
    :param username: The username of the account owner.
    :type username: str
    :param host: The base URL of the application.
    :type host: str
    :param reset_token: The secure token generated for password recovery.
    :type reset_token: str
    :return: None
    """
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        template_body={
            "host": host,
            "username": username,
            "token": reset_token
        },
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset.html")