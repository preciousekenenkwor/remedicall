import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, List

from fastapi import BackgroundTasks, HTTPException, status
from jinja2 import DictLoader, Environment
from pydantic import EmailStr

from app.config import env
from app.utils.logger import log


class SMTPMailer:
    def __init__(
        self,
        background_tasks: BackgroundTasks,
        receiver_emails: List[EmailStr],
        template_name: str,
        subject: str,
        template_data: dict[str, Any],
        background: bool = False,
    ):
        self.sender_email: EmailStr = env.env["mail"]["mail_sender"]
        self.sender_password = env.env["mail"]["mail_password"]
        self.smtp_server = env.env["mail"]["mail_server"]
        self.smtp_port = env.env["mail"]["mail_port"]

        self.background = background
        self.background_tasks = background_tasks
        self.receiver_emails = receiver_emails
        self.subject = subject
        self.template_name = template_name
        self.template_data = template_data

    def _get_html_content(self) -> str:
        """Render HTML template with provided data"""
        template_env = Environment(loader=DictLoader(EMAIL_TEMPLATES))
        template = template_env.get_template(self.template_name)
        return template.render(**self.template_data)

    def _create_message(self, receiver_email: str) -> MIMEMultipart:
        """Create email message"""
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender_email
        message["To"] = receiver_email

        # Create HTML part
        html_content = self._get_html_content()
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        return message

    def _send_email_sync(self):
        """Send email synchronously"""
        try:
            log.logs.info(
                f"Attempting to send email to: {', '.join(self.receiver_emails)}"
            )
            log.logs.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")

            # Handle different SMTP configurations
            if self.smtp_port == 465:
                # SSL connection (port 465)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    self.smtp_server, self.smtp_port, context=context
                ) as server:
                    log.logs.info("Connected via SSL")
                    server.login(self.sender_email, self.sender_password)
                    log.logs.info("Login successful")

                    for receiver_email in self.receiver_emails:
                        message = self._create_message(receiver_email)
                        server.send_message(message)
                        log.logs.info(f"Email sent to: {receiver_email}")

            elif self.smtp_port == 587:
                # TLS connection (port 587)
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    log.logs.info("Connected via SMTP")
                    server.starttls(context=context)
                    log.logs.info("TLS started")
                    server.login(self.sender_email, self.sender_password)
                    log.logs.info("Login successful")

                    for receiver_email in self.receiver_emails:
                        message = self._create_message(receiver_email)
                        server.send_message(message)
                        log.logs.info(f"Email sent to: {receiver_email}")
            else:
                # Fallback for other ports
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    try:
                        server.starttls(context=context)
                        log.logs.info("TLS started")
                    except Exception as e:
                        log.logs.warning(f"TLS failed, continuing without: {e}")

                    server.login(self.sender_email, self.sender_password)
                    log.logs.info("Login successful")

                    for receiver_email in self.receiver_emails:
                        message = self._create_message(receiver_email)
                        server.send_message(message)
                        log.logs.info(f"Email sent to: {receiver_email}")

            log.logs.info("All emails sent successfully")
            return {"message": "Email sent successfully"}

        except smtplib.SMTPAuthenticationError as e:
            log.logs.error(f"SMTP Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email authentication failed. Check credentials.",
            )
        except smtplib.SMTPConnectError as e:
            log.logs.error(f"SMTP Connection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to email server.",
            )
        except smtplib.SMTPRecipientsRefused as e:
            log.logs.error(f"Recipients refused: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more recipient addresses were refused.",
            )
        except smtplib.SMTPException as e:
            log.logs.error(f"SMTP error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMTP error: {str(e)}",
            )
        except Exception as e:
            log.logs.error(f"Unexpected error sending email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {str(e)}",
            )

    async def send_mail(self):
        """Send email (background or synchronous)"""
        if self.background:
            self.background_tasks.add_task(self._send_email_sync)
            return {"message": "Email queued for sending"}
        else:
            return self._send_email_sync()


# Email Templates (keeping your existing templates)
EMAIL_TEMPLATES = {
    # Authentication Templates
   "verify_email.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: rgba(255, 255, 255, 0.95); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .header { 
            text-align: center; 
            color: #2c5aa0; 
            margin-bottom: 30px; 
            font-size: 28px;
            font-weight: 700;
        }
        .token-container {
            background: linear-gradient(135deg, #2c5aa0, #3b82f6);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(44, 90, 160, 0.3);
        }
        .token {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .token-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .instructions {
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #2c5aa0;
            margin: 20px 0;
        }
        .footer { 
            margin-top: 30px; 
            font-size: 12px; 
            color: #666; 
            text-align: center; 
            opacity: 0.8;
        }
        .warning {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            margin: 20px 0;
            font-size: 14px;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .token { font-size: 28px; letter-spacing: 4px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">✉️ Email Verification</h1>
        <p>Hello <strong>{{ name }}</strong>,</p>
        <p>To complete your account verification, please use the verification code below:</p>
        
        <div class="token-container">
            <div class="token-label">Your Verification Code</div>
            <div class="token">{{ otp }}</div>
        </div>
        
        <div class="instructions">
            <p><strong>How to verify:</strong></p>
            <p>1. Go to the verification page on our website</p>
            <p>2. Enter the 6-digit code above</p>
            <p>3. Click "Verify" to activate your account</p>
        </div>
        
        <div class="warning">
            ⚠️ This code will expire in <strong>{{ expiry_hours }} hours</strong>. Please verify your email before it expires.
        </div>
        
        <div class="footer">
            <p>If you didn't request this verification, please ignore this email.</p>
            <p>For security reasons, never share this code with anyone.</p>
            <>p>Thanks for using {{website_name}} service!</p>
        </div>
    </div>
</body>
</html>
""",

# Reset Password

"reset_password.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
            min-height: 100vh;
        }
        .container { 
            background: rgba(255, 255, 255, 0.95); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .header { 
            text-align: center; 
            color: #e74c3c; 
            margin-bottom: 30px; 
            font-size: 28px;
            font-weight: 700;
        }
        .token-container {
            background: linear-gradient(135deg, #e74c3c, #ff6b6b);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(231, 76, 60, 0.3);
        }
        .token {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .token-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .instructions {
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #e74c3c;
            margin: 20px 0;
        }
        .footer { 
            margin-top: 30px; 
            font-size: 12px; 
            color: #666; 
            text-align: center; 
            opacity: 0.8;
        }
        .warning {
            background: #fef2f2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #fecaca;
            margin: 20px 0;
            font-size: 14px;
        }
        .security-notice {
            background: #fffbeb;
            color: #d97706;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #fed7aa;
            margin: 20px 0;
            font-size: 14px;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .token { font-size: 28px; letter-spacing: 4px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🔐 Password Reset</h1>
        <p>Hello <strong>{{ name }}</strong>,</p>
        <p>You requested to reset your password. Use the verification code below to proceed:</p>
        
        <div class="token-container">
            <div class="token-label">Password Reset Code</div>
            <div class="token">{{ otp }}</div>
        </div>
        
        <div class="instructions">
            <p><strong>How to reset your password:</strong></p>
            <p>1. Go to the password reset page</p>
            <p>2. Enter the 6-digit code above</p>
            <p>3. Create your new secure password</p>
            <p>4. Confirm and save your changes</p>
        </div>
        
        <div class="warning">
            ⏰ This code will expire in <strong>{{ expiry_hours }} hours</strong>. Please reset your password before it expires.
        </div>
        
        <div class="security-notice">
            🛡️ <strong>Security Notice:</strong> If you didn't request this password reset, please secure your account immediately and contact our support team.
        </div>
        
        <div class="footer">
            <p>Never share this code with anyone. We will never ask for your code via phone or email.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
""",


# Welcome email

"welcome.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to {{ app_name }}</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            min-height: 100vh;
        }
        .container { 
            background: rgba(255, 255, 255, 0.95); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .header { 
            text-align: center; 
            color: #27ae60; 
            margin-bottom: 30px; 
            font-size: 28px;
            font-weight: 700;
        }
        .welcome-message {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 10px 25px rgba(39, 174, 96, 0.3);
        }
        .button { 
            display: inline-block; 
            background: linear-gradient(135deg, #27ae60, #2ecc71); 
            color: white; 
            padding: 15px 35px; 
            text-decoration: none; 
            border-radius: 50px; 
            margin: 20px 0; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(39, 174, 96, 0.4);
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(39, 174, 96, 0.6);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature {
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .feature-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .footer { 
            margin-top: 30px; 
            font-size: 12px; 
            color: #666; 
            text-align: center; 
            opacity: 0.8;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .features { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🎉 Welcome to {{ app_name }}!</h1>
        <p>Hello <strong>{{ name }}</strong>,</p>
        
        <div class="welcome-message">
            <h2 style="margin-top: 0; font-size: 24px;">Your Account is Ready!</h2>
            <p style="margin-bottom: 0; font-size: 16px; opacity: 0.9;">Welcome aboard! Your account has been successfully created and verified.</p>
        </div>
        
        <p>You now have access to all our features and services. Here's what you can do:</p>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🏥</div>
                <h3>Book Appointments</h3>
                <p>Schedule appointments with your preferred healthcare providers</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h3>View Records</h3>
                <p>Access your medical records and test results securely</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💊</div>
                <h3>Manage Prescriptions</h3>
                <p>Track and manage your medications and prescriptions</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔔</div>
                <h3>Get Notifications</h3>
                <p>Receive important updates and appointment reminders</p>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ login_link }}" class="button">Get Started Now</a>
        </div>
        
        <div class="footer">
            <p>Thank you for choosing {{ app_name }}! We're excited to serve you.</p>
            <p>If you have any questions, our support team is here to help.</p>
        </div>
    </div>
</body>
</html>
""",
    
    
    # Notification Templates
    "appointment_reminder.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Appointment Reminder</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #3498db; margin-bottom: 30px; }
            .appointment-details { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Appointment Reminder</h1>
            <p>Hello {{ patient_name }},</p>
            <p>This is a reminder for your upcoming appointment:</p>
            <div class="appointment-details">
                <p><strong>Doctor:</strong> {{ doctor_name }}</p>
                <p><strong>Date:</strong> {{ appointment_date }}</p>
                <p><strong>Time:</strong> {{ appointment_time }}</p>
                <p><strong>Location:</strong> {{ location }}</p>
            </div>
            <div class="footer">
                <p>Please arrive 15 minutes early. Contact us if you need to reschedule.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    "prescription_ready.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Prescription Ready</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #16a085; margin-bottom: 30px; }
            .prescription-details { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Prescription Ready</h1>
            <p>Hello {{ patient_name }},</p>
            <p>Your prescription is ready for pickup:</p>
            <div class="prescription-details">
                <p><strong>Prescription ID:</strong> {{ prescription_id }}</p>
                <p><strong>Medications:</strong> {{ medications }}</p>
                <p><strong>Pharmacy:</strong> {{ pharmacy_name }}</p>
                <p><strong>Address:</strong> {{ pharmacy_address }}</p>
            </div>
            <div class="footer">
                <p>Please bring a valid ID when picking up your prescription.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    "test_results.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Results Available</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #8e44ad; margin-bottom: 30px; }
            .button { display: inline-block; background: #8e44ad; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Test Results Available</h1>
            <p>Hello {{ patient_name }},</p>
            <p>Your {{ test_type }} results are now available.</p>
            <p>Please log in to your patient portal to view your results or schedule a follow-up appointment.</p>
            <div style="text-align: center;">
                <a href="{{ portal_link }}" class="button">View Results</a>
            </div>
            <div class="footer">
                <p>For questions about your results, please contact your healthcare provider.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    "payment_confirmation.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Payment Confirmation</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #27ae60; margin-bottom: 30px; }
            .payment-details { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">Payment Confirmation</h1>
            <p>Hello {{ patient_name }},</p>
            <p>Your payment has been successfully processed:</p>
            <div class="payment-details">
                <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                <p><strong>Amount:</strong> ${{ amount }}</p>
                <p><strong>Service:</strong> {{ service_description }}</p>
                <p><strong>Date:</strong> {{ payment_date }}</p>
            </div>
            <div class="footer">
                <p>Keep this email for your records. Contact us if you have any questions.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    "general_notification.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #34495e; margin-bottom: 30px; }
            .content { background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">{{ title }}</h1>
            <p>Hello {{ name }},</p>
            <div class="content">
                {{ message }}
            </div>
            <div class="footer">
                <p>{{ footer_message | default("Thank you for using our service.") }}</p>
            </div>
        </div>
    </body>
    </html>
    """,
}


# Usage Examples
def send_verification_email(
    background_tasks: BackgroundTasks, email: str, name: str, verification_link: str
):
    """Send email verification"""
    mailer = SMTPMailer(
        background_tasks=background_tasks,
        receiver_emails=[email],
        template_name="verify_email.html",
        subject="Verify Your Email Address",
        template_data={
            "name": name,
            "verification_link": verification_link,
            "expiry_hours": 24,
        },
        background=True,
    )
    return mailer.send_mail()


def send_appointment_reminder(
    background_tasks: BackgroundTasks,
    email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    location: str,
):
    """Send appointment reminder"""
    mailer = SMTPMailer(
        background_tasks=background_tasks,
        receiver_emails=[email],
        template_name="appointment_reminder.html",
        subject="Appointment Reminder",
        template_data={
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "location": location,
        },
        background=True,
    )
    return mailer.send_mail()


def send_general_notification(
    background_tasks: BackgroundTasks,
    email: str,
    name: str,
    title: str,
    message: str,
    footer_message: str | None = None,
):
    """Send general notification"""
    mailer = SMTPMailer(
        background_tasks=background_tasks,
        receiver_emails=[email],
        template_name="general_notification.html",
        subject=title,
        template_data={
            "name": name,
            "title": title,
            "message": message,
            "footer_message": footer_message,
        },
        background=True,
    )
    return mailer.send_mail()


# Test function to help debug connection
def test_smtp_connection(smtp_server: str, smtp_port: int, email: str, password: str):
    """Test SMTP connection without sending email"""
    try:
        if smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(email, password)
                print("✅ SSL connection successful")
        elif smtp_port == 587:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(email, password)
                print("✅ TLS connection successful")
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.login(email, password)
                print("✅ Basic connection successful")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
