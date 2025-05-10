"""Email sending functionality for the email assistant."""

import re
import smtplib
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, credentials):
        """Initialize the email sender.
        
        Args:
            credentials: Dict containing email credentials
        """
        self.credentials = credentials
    
    def is_valid_email(self, email):
        """Check if string looks like a valid email address.
        
        Args:
            email: Email address to check
            
        Returns:
            Boolean indicating if the email looks valid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def send_email(self, to_email, subject, body):
        """Send an email via Gmail SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            
        Returns:
            Tuple (success, message)
        """
        # Create the email
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = self.credentials['gmail_user']
        msg['To'] = to_email

        # Try to send it
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.credentials['gmail_user'], self.credentials['gmail_pass'])
            server.sendmail(self.credentials['gmail_user'], to_email, msg.as_string())
            server.quit()
            return True, "Email sent successfully!"
        except smtplib.SMTPAuthenticationError:
            return False, "Gmail login failed. Check your app password."
        except Exception as e:
            return False, f"Sending failed: {e}"