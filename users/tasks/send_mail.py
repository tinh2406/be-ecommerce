import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task
from django.conf import settings


@shared_task
def send_email_task(receiver_emails, subject, body, is_html=True):
    try:
        # Create a MIMEMultipart object to represent the email
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = ", ".join(receiver_emails)  # Join multiple emails with comma
        msg["Subject"] = subject

        # Attach the email body (plain text or HTML)
        if is_html:
            msg.attach(MIMEText(body, "html"))  # HTML format
        else:
            msg.attach(MIMEText(body, "plain"))  # Plain text format

        # Set up the server
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()  # Start TLS encryption

        # Login to the SMTP server
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        # Send the email
        server.send_message(msg)

        # Close the connection
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")
