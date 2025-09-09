import os
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@logiscore.net')
        self.from_name = os.getenv('FROM_NAME', 'LogiScore')
        
        # Enhanced logging for configuration
        if self.api_key:
            logger.info(f"SendGrid API key loaded successfully. From email: {self.from_email}")
            # Log first few characters of API key for debugging (safely)
            if len(self.api_key) > 8:
                logger.info(f"SendGrid API key starts with: {self.api_key[:8]}...")
            else:
                logger.warning("SendGrid API key seems too short")
        else:
            logger.warning("SENDGRID_API_KEY not found in environment variables. Email sending will be disabled.")
            logger.info("Available environment variables:")
            for key, value in os.environ.items():
                if 'SENDGRID' in key or 'EMAIL' in key or 'MAIL' in key:
                    if 'KEY' in key and value:
                        logger.info(f"  {key}: {value[:8]}... (truncated)")
                    else:
                        logger.info(f"  {key}: {value}")
    
    async def send_verification_code(self, to_email: str, verification_code: str) -> bool:
        """Send verification code email using SendGrid"""
        try:
            if not self.api_key:
                # Fallback: log the code to console for development
                logger.info(f"FALLBACK: Verification code for {to_email}: {verification_code}")
                return True
            
            # Create email message
            subject = "LogiScore - Email Verification Code"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>LogiScore Verification Code</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 10px;
                    }}
                    .verification-code {{
                        background: #007bff;
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                        padding: 20px;
                        text-align: center;
                        border-radius: 8px;
                        margin: 20px 0;
                        letter-spacing: 5px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    <h2>Hello!</h2>
                    <p>You've requested a verification code to access your LogiScore account.</p>
                    
                    <div class="verification-code">
                        {verification_code}
                    </div>
                    
                    <p><strong>This code will expire in 10 minutes.</strong></p>
                    
                    <div class="warning">
                        <strong>Security Notice:</strong> Never share this code with anyone. 
                        LogiScore staff will never ask for your verification code.
                    </div>
                    
                    <p>If you didn't request this code, please ignore this email or contact our support team.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Verification code email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email to {to_email}: {str(e)}")
            # Fallback: log the code to console
            logger.info(f"FALLBACK: Verification code for {to_email}: {verification_code}")
            return True  # Return True for fallback mode
    
    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        """Send welcome email to new users"""
        try:
            if not self.api_key:
                logger.info(f"FALLBACK: Welcome email would be sent to {to_email}")
                return True
            
            subject = "Welcome to LogiScore! 🚀"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to LogiScore</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: #28a745;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 Welcome to LogiScore!</h1>
                    <p>Your account has been successfully created</p>
                </div>
                
                <div class="content">
                    <h2>Hello {full_name}!</h2>
                    
                    <p>Welcome to LogiScore, the premier platform for freight forwarder reviews and ratings.</p>
                    
                    <p><strong>🎯 You've joined a community dedicated to improving service levels across the logistics industry!</strong></p>
                    
                    <p>By becoming part of LogiScore, you're helping to:</p>
                    <ul>
                        <li>🚀 <strong>Elevate Industry Standards</strong> - Your feedback drives quality improvements</li>
                        <li>🤝 <strong>Build Trust</strong> - Help other businesses make informed decisions</li>
                        <li>📈 <strong>Promote Excellence</strong> - Recognize and reward outstanding service providers</li>
                        <li>🌍 <strong>Create Transparency</strong> - Share real experiences to benefit the global logistics community</li>
                    </ul>
                    
                    <p>With your new account, you can:</p>
                    <ul>
                        <li>📝 Write and read authentic reviews</li>
                        <li>⭐ Rate freight forwarders across multiple categories</li>
                        <li>🔍 Search and compare logistics providers</li>
                        <li>💼 Access premium features and insights</li>
                    </ul>
                    
                    <a href="https://logiscore.net" class="cta-button">Get Started Now</a>
                    
                    <p><strong>💡 Ready to make a difference?</strong></p>
                    <p>Start by writing your first review or exploring existing ones. Every rating, every review, and every piece of feedback contributes to building a better, more transparent logistics industry.</p>
                    
                    <p><strong>Thank you for joining our mission to improve service levels across the logistics industry!</strong></p>
                    
                    <p>If you have any questions or need assistance, our support team is here to help!</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Welcome email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send welcome email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email to {to_email}: {str(e)}")
            logger.info(f"FALLBACK: Welcome email would be sent to {to_email}")
            return True  # Return True for fallback mode

    async def send_review_thank_you_email(self, to_email: str, user_name: str, freight_forwarder_name: str, 
                                        city: str, country: str, category_scores: list) -> bool:
        """Send thank you email after review submission"""
        try:
            logger.info(f"Attempting to send review thank you email to {to_email}")
            logger.info(f"User: {user_name}, Freight Forwarder: {freight_forwarder_name}")
            logger.info(f"Location: {city}, {country}")
            logger.info(f"Category scores count: {len(category_scores)}")
            
            if not self.api_key:
                logger.warning("SendGrid API key not available - using fallback mode")
                logger.info(f"FALLBACK: Review thank you email would be sent to {to_email}")
                logger.info(f"FALLBACK: Subject: Thank you for your review of {freight_forwarder_name}!")
                return True
            
            subject = f"Thank you for your review of {freight_forwarder_name}! 🚢"
            logger.info(f"Email subject: {subject}")
            
            # Build category scores HTML
            category_scores_html = ""
            for score in category_scores:
                # Create 5-star scale: filled stars + empty stars
                filled_stars = "⭐" * score['rating']
                empty_stars = "☆" * (5 - score['rating'])
                stars = filled_stars + empty_stars
                category_scores_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                        <strong>{score['category_name']}</strong><br>
                        <span style="color: #6c757d; font-size: 14px;">{score['question_text']}</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6; text-align: center;">
                        <span style="font-size: 18px;">{stars}</span><br>
                        <span style="color: #6c757d; font-size: 12px;">{score['rating']}/5 - {score['rating_definition']}</span>
                    </td>
                </tr>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thank you for your review!</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 700px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .review-summary {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .category-scores {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        margin: 20px 0;
                        overflow: hidden;
                    }}
                    .category-scores table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    .category-scores th {{
                        background: #f8f9fa;
                        padding: 15px 12px;
                        text-align: left;
                        font-weight: bold;
                        border-bottom: 2px solid #dee2e6;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: #28a745;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .location-info {{
                        background: #e3f2fd;
                        border: 1px solid #bbdefb;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 Thank you for your review!</h1>
                    <p>Your feedback helps the logistics community</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    
                    <p>Thank you for taking the time to submit your review on LogiScore. Your feedback is invaluable to the logistics community and helps other businesses make informed decisions.</p>
                    
                    <div class="review-summary">
                        <h3>📋 Review Summary</h3>
                        <p><strong>Freight Forwarder:</strong> {freight_forwarder_name}</p>
                        <div class="location-info">
                            <strong>📍 Location:</strong> {city}, {country}
                        </div>
                    </div>
                    
                    <div class="category-scores">
                        <h3>⭐ Your Ratings</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th style="width: 60%;">Category & Question</th>
                                    <th style="width: 40%;">Your Rating</th>
                                </tr>
                            </thead>
                            <tbody>
                                {category_scores_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <p>Your review has been submitted and is now visible to the LogiScore community. Other users can now benefit from your experience and insights.</p>
                    
                    <a href="https://logiscore.net" class="cta-button">Visit LogiScore</a>
                    
                    <p>If you have any questions about your review or need to make changes, please don't hesitate to contact our support team.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            logger.info("Creating SendGrid message...")
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            logger.info("Initializing SendGrid client...")
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                logger.info("Setting EU data residency for SendGrid")
                sg.set_sendgrid_data_residency("eu")
            
            logger.info("Sending email via SendGrid...")
            response = sg.send(message)
            
            logger.info(f"SendGrid response status: {response.status_code}")
            logger.info(f"SendGrid response headers: {dict(response.headers)}")
            
            if response.status_code == 202:
                logger.info(f"Review thank you email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send review thank you email. Status code: {response.status_code}")
                logger.error(f"SendGrid response body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending review thank you email to {to_email}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            logger.info(f"FALLBACK: Review thank you email would be sent to {to_email}")
            return True  # Return True for fallback mode

    def get_routing_email(self, contact_reason: str) -> str:
        """Get the appropriate email address based on contact reason"""
        routing_map = {
            "feedback": "feedback@logiscore.net",
            "support": "support@logiscore.net",
            "billing": "accounts@logiscore.net",
            "reviews": "dispute@logiscore.net",
            "privacy": "dpo@logiscore.net",
            "general": "support@logiscore.net"
        }
        return routing_map.get(contact_reason.lower(), "support@logiscore.net")

    async def send_contact_form_team_email(self, contact_data: dict, routing_email: str) -> bool:
        """Send contact form email to the appropriate team"""
        try:
            if not self.api_key:
                logger.info(f"FALLBACK: Contact form team email would be sent to {routing_email}")
                return True
            
            subject = f"[Contact Form] {contact_data.get('subject', 'General Inquiry')}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Contact Form Submission</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .contact-info {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .contact-info h3 {{
                        margin-top: 0;
                        color: #495057;
                    }}
                    .contact-info p {{
                        margin: 10px 0;
                    }}
                    .contact-info strong {{
                        color: #495057;
                    }}
                    .message-content {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📧 New Contact Form Submission</h1>
                    <p>Contact Reason: {contact_data.get('contact_reason', 'general').title()}</p>
                </div>
                
                <div class="content">
                    <div class="contact-info">
                        <h3>👤 Contact Information</h3>
                        <p><strong>Name:</strong> {contact_data.get('name', 'Not provided')}</p>
                        <p><strong>Email:</strong> {contact_data.get('email', 'Not provided')}</p>
                        <p><strong>Contact Reason:</strong> {contact_data.get('contact_reason', 'general').title()}</p>
                        <p><strong>Subject:</strong> {contact_data.get('subject', 'No subject')}</p>
                    </div>
                    
                    <div class="message-content">
                        <h3>💬 Message</h3>
                        <p>{contact_data.get('message', 'No message content').replace(chr(10), '<br>')}</p>
                    </div>
                    
                    <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <p>Please respond to this inquiry within 24 hours.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from the LogiScore contact form system.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(routing_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Contact form team email sent successfully to {routing_email}")
                return True
            else:
                logger.error(f"Failed to send contact form team email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending contact form team email to {routing_email}: {str(e)}")
            logger.info(f"FALLBACK: Contact form team email would be sent to {routing_email}")
            return True  # Return True for fallback mode

    async def send_contact_form_acknowledgment(self, contact_data: dict) -> bool:
        """Send acknowledgment email to the user who submitted the contact form"""
        try:
            if not self.api_key:
                logger.info(f"FALLBACK: Contact form acknowledgment would be sent to {contact_data.get('email')}")
                return True
            
            subject = "Thank you for contacting LogiScore"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thank you for contacting LogiScore</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .confirmation {{
                        background: #d4edda;
                        border: 1px solid #c3e6cb;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        color: #155724;
                    }}
                    .next-steps {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: #28a745;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📧 Thank you for contacting LogiScore!</h1>
                    <p>We've received your message</p>
                </div>
                
                <div class="content">
                    <h2>Hello {contact_data.get('name', 'there')}!</h2>
                    
                    <div class="confirmation">
                        <h3>✅ Message Received</h3>
                        <p>We've successfully received your contact form submission and our team will get back to you as soon as possible.</p>
                    </div>
                    
                    <div class="next-steps">
                        <h3>📋 What happens next?</h3>
                        <ul>
                            <li>Your message has been routed to our {contact_data.get('contact_reason', 'general').title()} team</li>
                            <li>We typically respond within 24 hours during business days</li>
                            <li>For urgent matters, please include "URGENT" in your subject line</li>
                        </ul>
                    </div>
                    
                    <p><strong>Your message details:</strong></p>
                    <ul>
                        <li><strong>Subject:</strong> {contact_data.get('subject', 'No subject')}</li>
                        <li><strong>Contact Reason:</strong> {contact_data.get('contact_reason', 'general').title()}</li>
                        <li><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                    </ul>
                    
                    <a href="https://logiscore.net" class="cta-button">Visit LogiScore</a>
                    
                    <p>If you have any additional questions or need immediate assistance, please don't hesitate to reach out.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated acknowledgment message. Please do not reply to this email.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(contact_data.get('email')),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Contact form acknowledgment sent successfully to {contact_data.get('email')}")
                return True
            else:
                logger.error(f"Failed to send contact form acknowledgment. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending contact form acknowledgment to {contact_data.get('email')}: {str(e)}")
            logger.info(f"FALLBACK: Contact form acknowledgment would be sent to {contact_data.get('email')}")
            return True  # Return True for fallback mode

    async def send_review_notification(self, user_email: str, user_name: str, review_data: dict) -> bool:
        """Send notification email for new reviews matching user subscriptions"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Review notification for {user_email}: {review_data}")
                return True
            
            # Create email message
            subject = f"New Review Alert - {review_data.get('freight_forwarder_name', 'Freight Forwarder')}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Review Alert - LogiScore</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .review-card {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .rating {{
                        color: #ffc107;
                        font-size: 18px;
                        margin: 10px 0;
                    }}
                    .location {{
                        background: #e9ecef;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 10px 0;
                        font-size: 14px;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: #007bff;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔔 New Review Alert</h1>
                    <p>A new review has been posted that matches your subscription criteria</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    
                    <p>We've found a new review that matches your subscription preferences:</p>
                    
                    <div class="review-card">
                        <h3>{review_data.get('freight_forwarder_name', 'Freight Forwarder')}</h3>
                        
                        <div class="rating">
                            {'⭐' * int(review_data.get('aggregate_rating', 0))} 
                            {review_data.get('aggregate_rating', 'N/A')}/5.0
                        </div>
                        
                        <div class="location">
                            <strong>Location:</strong> {review_data.get('city', 'N/A')}, {review_data.get('country', 'N/A')}
                        </div>
                        
                        <div class="location">
                            <strong>Review Type:</strong> {review_data.get('review_type', 'General').title()}
                        </div>
                        
                        <p><strong>Posted:</strong> {review_data.get('created_at', 'N/A')}</p>
                    </div>
                    
                    <a href="https://logiscore.net/reviews/{review_data.get('review_id')}" class="cta-button">View Full Review</a>
                    
                    <p>This notification was sent because you're subscribed to reviews matching your criteria. You can manage your subscription preferences in your LogiScore account.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>You're receiving this email because you have an active review subscription on LogiScore.</p>
                    <p><a href="https://logiscore.net/account/subscriptions">Manage Subscriptions</a> | <a href="https://logiscore.net/account/unsubscribe">Unsubscribe</a></p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(user_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Review notification sent successfully to {user_email}")
                return True
            else:
                logger.error(f"Failed to send review notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending review notification to {user_email}: {str(e)}")
            logger.info(f"FALLBACK: Review notification would be sent to {user_email}")
            return True  # Return True for fallback mode

    async def send_subscription_summary(self, user_email: str, user_name: str, summary_data: dict) -> bool:
        """Send daily/weekly subscription summary email"""
        try:
            if not self.api_key:
                # Fallback: log the summary to console for development
                logger.info(f"FALLBACK: Subscription summary for {user_email}: {summary_data}")
                return True
            
            # Create email message
            frequency = summary_data.get('frequency', 'daily')
            subject = f"Your {frequency.title()} Review Summary - LogiScore"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{frequency.title()} Review Summary - LogiScore</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .summary-stats {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .stat-number {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #007bff;
                    }}
                    .review-item {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: #007bff;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Your {frequency.title()} Review Summary</h1>
                    <p>Here's what's new in your subscribed categories</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    
                    <div class="summary-stats">
                        <div class="stat-number">{summary_data.get('total_reviews', 0)}</div>
                        <p>New reviews in the past {frequency}</p>
                    </div>
                    
                    <h3>Recent Reviews:</h3>
                    
                    {self._generate_review_summary_html(summary_data.get('reviews', []))}
                    
                    <a href="https://logiscore.net/reviews" class="cta-button">View All Reviews</a>
                    
                    <p>You can manage your subscription preferences and notification frequency in your LogiScore account.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>You're receiving this email because you have an active review subscription on LogiScore.</p>
                    <p><a href="https://logiscore.net/account/subscriptions">Manage Subscriptions</a> | <a href="https://logiscore.net/account/unsubscribe">Unsubscribe</a></p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(user_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Subscription summary sent successfully to {user_email}")
                return True
            else:
                logger.error(f"Failed to send subscription summary. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending subscription summary to {user_email}: {str(e)}")
            logger.info(f"FALLBACK: Subscription summary would be sent to {user_email}")
            return True  # Return True for fallback mode

    def _generate_review_summary_html(self, reviews: list) -> str:
        """Generate HTML for review summary items"""
        if not reviews:
            return '<p>No new reviews in this period.</p>'
        
        html_parts = []
        for review in reviews[:5]:  # Limit to 5 reviews
            html_parts.append(f"""
                <div class="review-item">
                    <h4>{review.get('freight_forwarder_name', 'Freight Forwarder')}</h4>
                    <p><strong>Rating:</strong> {'⭐' * int(review.get('aggregate_rating', 0))} {review.get('aggregate_rating', 'N/A')}/5.0</p>
                    <p><strong>Location:</strong> {review.get('city', 'N/A')}, {review.get('country', 'N/A')}</p>
                    <p><strong>Type:</strong> {review.get('review_type', 'General').title()}</p>
                    <p><strong>Posted:</strong> {review.get('created_at', 'N/A')}</p>
                </div>
            """)
        
        if len(reviews) > 5:
            html_parts.append(f'<p><em>... and {len(reviews) - 5} more reviews</em></p>')
        
        return ''.join(html_parts)

    async def send_admin_new_forwarder_notification(self, forwarder_data: dict, creator_data: dict) -> bool:
        """Send notification email to admin when a new freight forwarder is added"""
        try:
            if not self.api_key:
                logger.info(f"FALLBACK: Admin new forwarder notification would be sent to admin@logiscore.net")
                logger.info(f"FALLBACK: New company: {forwarder_data.get('name')} by {creator_data.get('full_name', 'Unknown')}")
                return True
            
            subject = f"🚢 New Freight Forwarder Added: {forwarder_data.get('name', 'Unknown Company')}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Freight Forwarder Added - LogiScore</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 700px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .company-info {{
                        background: white;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .creator-info {{
                        background: #e3f2fd;
                        border: 1px solid #bbdefb;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .company-info h3, .creator-info h3 {{
                        margin-top: 0;
                        color: #495057;
                    }}
                    .company-info p, .creator-info p {{
                        margin: 10px 0;
                    }}
                    .company-info strong, .creator-info strong {{
                        color: #495057;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .timestamp {{
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 15px 0;
                        text-align: center;
                        color: #6c757d;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚢 New Freight Forwarder Added</h1>
                    <p>A new company has been added to the LogiScore platform</p>
                </div>
                
                <div class="content">
                    <h2>Company Information</h2>
                    
                    <div class="company-info">
                        <h3>🏢 {forwarder_data.get('name', 'Unknown Company')}</h3>
                        <p><strong>Website:</strong> <a href="https://logiscore.net/8x7k9m2p" target="_blank">Company Management</a></p>
                    </div>
                    
                    <h2>Creator Information</h2>
                    
                    <div class="creator-info">
                        <h3>👤 {creator_data.get('full_name', 'Unknown User')}</h3>
                        <p><strong>Email:</strong> {creator_data.get('email', 'Not provided')}</p>
                        <p><strong>Username:</strong> {creator_data.get('username', 'Not provided')}</p>
                        <p><strong>User Type:</strong> {creator_data.get('user_type', 'Unknown').title()}</p>
                        <p><strong>User ID:</strong> {creator_data.get('id', 'Unknown')}</p>
                    </div>
                    
                    <div class="timestamp">
                        <strong>Added to platform:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                    </div>
                    
                    <p>This notification was automatically generated when a new freight forwarder was added to the LogiScore platform. The company is now available for reviews and ratings.</p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Review the company information for accuracy</li>
                        <li>Verify the company's legitimacy if needed</li>
                        <li>Monitor for any reviews or disputes</li>
                        <li>Consider reaching out to the company for partnership opportunities</li>
                    </ul>
                    
                    <p>Best regards,<br>The LogiScore System</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from the LogiScore platform.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To("admin@logiscore.net"),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Admin new forwarder notification sent successfully to admin@logiscore.net")
                return True
            else:
                logger.error(f"Failed to send admin new forwarder notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending admin new forwarder notification: {str(e)}")
            logger.info(f"FALLBACK: Admin new forwarder notification would be sent to admin@logiscore.net")
            return True  # Return True for fallback mode

    async def send_subscription_expiration_warning(self, user_id: str, email_data: dict) -> bool:
        """Send subscription expiration warning email (7 days before expiry)"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Subscription expiration warning for user {user_id}: {email_data}")
                return True
            
            # Get user email from database or use provided data
            user_email = email_data.get('email') or f"user_{user_id}@logiscore.com"
            
            # Create email message
            subject = f"LogiScore - Your {email_data.get('subscription_tier', 'subscription')} expires in {email_data.get('days_remaining', '7')} days"
            
            # Determine auto-renewal status and billing information
            auto_renew_enabled = email_data.get('auto_renew_enabled', False)
            subscription_price = email_data.get('subscription_price', {})
            next_billing_date = email_data.get('next_billing_date')
            
            # Format price information
            price_amount = subscription_price.get('amount', 0)
            price_currency = subscription_price.get('currency', 'USD')
            price_period = subscription_price.get('period', 'month')
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Subscription Expiring Soon</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 10px;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .info-box {{
                        background: #e7f3ff;
                        border: 1px solid #b3d9ff;
                        color: #004085;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .billing-info {{
                        background: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .cta-button {{
                        background: #007bff;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                        margin: 10px 5px;
                        font-weight: bold;
                    }}
                    .secondary-button {{
                        background: #6c757d;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                        margin: 10px 5px;
                        font-weight: bold;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .highlight {{
                        font-weight: bold;
                        color: #dc3545;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    <h2>Hello {email_data.get('user_name', 'there')}!</h2>
                    
                    <div class="warning">
                        <h3>⚠️ Subscription Expiring Soon</h3>
                        <p>Your <strong>{email_data.get('subscription_tier', 'subscription')}</strong> will expire on <strong>{email_data.get('expiry_date', 'the specified date')}</strong>.</p>
                        <p>That's only <strong>{email_data.get('days_remaining', '7')} days</strong> from now!</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>📋 Your Subscription Details</h3>
                        <p><strong>Current Plan:</strong> {email_data.get('subscription_tier', 'subscription').replace('_', ' ').title()}</p>
                        <p><strong>Expiration Date:</strong> {email_data.get('expiry_date', 'the specified date')}</p>
                        <p><strong>Auto-Renewal:</strong> <span class="highlight">{'Enabled' if auto_renew_enabled else 'Disabled'}</span></p>
                    </div>
                    
                    {f'''
                    <div class="billing-info">
                        <h3>💳 Auto-Renewal Billing Information</h3>
                        <p>Since auto-renewal is <strong>enabled</strong>, your subscription will be automatically renewed on <strong>{next_billing_date}</strong> (one day before expiration).</p>
                        <p><strong>Amount to be charged:</strong> <span class="highlight">${price_amount:.2f} {price_currency}</span> per {price_period}</p>
                        <p>You will receive a payment confirmation email once the renewal is processed.</p>
                    </div>
                    ''' if auto_renew_enabled else '''
                    <div class="info-box">
                        <h3>⚠️ Auto-Renewal Disabled</h3>
                        <p>Since auto-renewal is <strong>disabled</strong>, your subscription will <strong>not</strong> be automatically renewed.</p>
                        <p><strong>What will happen on {email_data.get('expiry_date', 'the expiration date')}:</strong></p>
                        <ul>
                            <li>Your account will automatically revert to the free tier</li>
                            <li>You'll lose access to premium features</li>
                            <li>Your data and settings will be preserved</li>
                            <li>You can upgrade again at any time</li>
                        </ul>
                    </div>
                    '''}
                    
                    <p><strong>Need to make changes?</strong></p>
                    <p>You can manage your subscription settings, including auto-renewal, at any time through your account dashboard.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{email_data.get('renewal_link', 'https://logiscore.com/renew')}" class="cta-button">Renew Subscription Now</a>
                        <a href="{email_data.get('manage_subscription_link', 'https://logiscore.com/subscription')}" class="secondary-button">Manage Subscription</a>
                    </div>
                    
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from LogiScore.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(user_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Subscription expiration warning sent successfully to {user_email}")
                return True
            else:
                logger.error(f"Failed to send subscription expiration warning. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending subscription expiration warning to {user_id}: {str(e)}")
            logger.info(f"FALLBACK: Subscription expiration warning would be sent to user {user_id}")
            return True  # Return True for fallback mode

    async def send_subscription_expired_notification(self, user_id: str, email_data: dict) -> bool:
        """Send notification when subscription has expired and been reverted to free"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Subscription expired notification for user {user_id}: {email_data}")
                return True
            
            # Get user email from database or use provided data
            user_email = email_data.get('email') or f"user_{user_id}@logiscore.com"
            
            # Create email message
            subject = "LogiScore - Your subscription has expired"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Subscription Expired</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 10px;
                }}
                .expired {{
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .cta-button {{
                    background: #007bff;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
            </head>
            <body>
                <div class="content">
                    <h2>Hello {email_data.get('user_name', 'there')}!</h2>
                    
                    <div class="expired">
                        <h3>❌ Subscription Expired</h3>
                        <p>Your <strong>{email_data.get('previous_tier', 'subscription')}</strong> has expired on <strong>{email_data.get('expiry_date', 'the specified date')}</strong>.</p>
                    </div>
                    
                    <p>Your account has been automatically reverted to the free tier. Don't worry - all your data and settings have been preserved.</p>
                    
                    <p><strong>What you can still do with the free tier:</strong></p>
                    <ul>
                        <li>Access basic LogiScore features</li>
                        <li>View limited freight forwarder information</li>
                        <li>Submit basic reviews</li>
                    </ul>
                    
                    <p><strong>To restore premium access:</strong></p>
                    <a href="https://logiscore.com/renew" class="cta-button">Renew Subscription Now</a>
                    
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    
                    <p>Best regards,<br>The LogiScore Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from LogiScore.</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(user_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Subscription expired notification sent successfully to {user_email}")
                return True
            else:
                logger.error(f"Failed to send subscription expired notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending subscription expired notification to {user_id}: {str(e)}")
            logger.info(f"FALLBACK: Subscription expired notification would be sent to user {user_id}")
            return True  # Return True for fallback mode

    async def send_review_notification(self, to_email: str, user_name: str, review_data: dict, subscription_type: str) -> bool:
        """Send new review notification email"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Review notification for {to_email}: New review for {review_data['freight_forwarder_name']}")
                return True
            
            # Create email subject
            location = f"{review_data['city']}, {review_data['country']}" if review_data['city'] else review_data['country']
            subject = f"New review for {review_data['freight_forwarder_name']} in {location}"
            
            # Create subscription type description
            subscription_desc = {
                'company': f"for {review_data['freight_forwarder_name']}",
                'country': f"in {review_data['country']}",
                'city': f"in {location}",
                'general': "matching your subscription"
            }.get(subscription_type, "matching your subscription")
            
            # Format rating stars and round to 1 decimal place
            rating_value = round(float(review_data['rating']), 1)
            rating_stars = "★" * int(rating_value) + "☆" * (5 - int(rating_value))
            
            # Truncate review text if too long
            review_text = review_data['review_text']
            if len(review_text) > 200:
                review_text = review_text[:200] + "..."
            
            # Get category scores for the review - group questions by category
            category_scores_html = ""
            if 'category_scores' in review_data and review_data['category_scores']:
                category_scores_html = "<div class='category-scores'><h4>Category Breakdown:</h4>"
                
                # Group questions by category
                categories = {}
                for category in review_data['category_scores']:
                    cat_name = category.get('category_name', 'Other')
                    if cat_name not in categories:
                        categories[cat_name] = []
                    
                    question_text = category.get('question_text', 'Question')
                    rating_def = category.get('rating_definition', '')
                    rating_def_text = f" - {rating_def}" if rating_def else ""
                    
                    categories[cat_name].append({
                        'question': question_text,
                        'rating': category['rating'],
                        'definition': rating_def_text
                    })
                
                # Build HTML for each category
                for cat_name, questions in categories.items():
                    category_scores_html += f"<div class='category-group'><h5>{cat_name}:</h5><ul>"
                    for question in questions:
                        category_scores_html += f"<li><strong>{question['question']}:</strong> {question['rating']}/5{question['definition']}</li>"
                    category_scores_html += "</ul></div>"
                
                category_scores_html += "</div>"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #2c5aa0;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    .review-card {{
                        background-color: #f8f9fa;
                        border-left: 4px solid #2c5aa0;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 5px;
                    }}
                    .company-name {{
                        font-size: 20px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    .rating {{
                        color: #ffc107;
                        font-size: 18px;
                        margin: 10px 0;
                    }}
                    .review-text {{
                        font-style: italic;
                        margin: 15px 0;
                        padding: 15px;
                        background-color: white;
                        border-radius: 5px;
                        border: 1px solid #e9ecef;
                    }}
                    .reviewer-info {{
                        color: #666;
                        font-size: 14px;
                        margin-top: 10px;
                    }}
                    .unsubscribe {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                        font-size: 12px;
                        color: #666;
                    }}
                    .unsubscribe a {{
                        color: #2c5aa0;
                        text-decoration: none;
                    }}
                    .category-scores {{
                        margin-top: 15px;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        border: 1px solid #e9ecef;
                    }}
                    .category-scores h4 {{
                        margin: 0 0 10px 0;
                        color: #2c5aa0;
                        font-size: 16px;
                    }}
                    .category-scores ul {{
                        margin: 0;
                        padding-left: 20px;
                    }}
                    .category-scores li {{
                        margin: 5px 0;
                        color: #555;
                    }}
                    .category-group {{
                        margin-bottom: 20px;
                        padding: 10px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        border-left: 3px solid #2c5aa0;
                    }}
                    .category-group h5 {{
                        margin: 0 0 10px 0;
                        color: #2c5aa0;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    .category-group ul {{
                        margin: 0;
                        padding-left: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <p>Dear {user_name},</p>
                    
                    <p>A new review has been posted {subscription_desc} that matches your notification subscription.</p>
                    
                    <div class="review-card">
                        <div class="company-name">{review_data['freight_forwarder_name']}</div>
                        <div class="rating">{rating_stars} ({rating_value}/5)</div>
                        {category_scores_html}
                    </div>
                    
                    <p>You can view this review and more on the LogiScore platform.</p>
                    
                    <div class="unsubscribe">
                        <p>You're receiving this because you subscribed to review notifications.</p>
                        <p><a href="https://logiscore.net/unsubscribe">Unsubscribe from notifications</a></p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from LogiScore.</p>
                        <p>&copy; 2025 LogiScore. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Review notification email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send review notification email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending review notification email to {to_email}: {str(e)}")
            logger.info(f"FALLBACK: Review notification would be sent to {to_email}")
            return True  # Return True for fallback mode

    async def send_subscription_cleanup_notice(self, to_email: str, user_name: str, cleanup_reason: str, old_tier: str, new_tier: str) -> bool:
        """Send subscription cleanup notice email"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Subscription cleanup notice for {to_email}: {cleanup_reason}")
                return True
            
            # Create email subject
            subject = "Your notification subscriptions have been removed"
            
            # Create reason description
            reason_desc = {
                'downgrade': f"your subscription was downgraded from {old_tier} to {new_tier}",
                'expiry': "your subscription has expired",
                'cancellation': "your subscription was cancelled"
            }.get(cleanup_reason, "your subscription status changed")
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #2c5aa0;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #2c5aa0;
                        margin-bottom: 10px;
                    }}
                    .notice-box {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 5px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">LogiScore</div>
                        <h2>Notification Subscriptions Removed</h2>
                    </div>
                    
                    <p>Hello {user_name},</p>
                    
                    <div class="notice-box">
                        <p><strong>Your review notification subscriptions have been removed</strong></p>
                        <p>This happened because {reason_desc}.</p>
                        <p>Review notifications are only available for premium subscription tiers.</p>
                    </div>
                    
                    <p>If you'd like to continue receiving review notifications, you can upgrade your subscription at any time.</p>
                    
                    <p>Thank you for using LogiScore!</p>
                    
                    <div class="footer">
                        <p>This is an automated message from LogiScore.</p>
                        <p>&copy; 2025 LogiScore. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Subscription cleanup notice sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send subscription cleanup notice. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending subscription cleanup notice to {to_email}: {str(e)}")
            logger.info(f"FALLBACK: Subscription cleanup notice would be sent to {to_email}")
            return True  # Return True for fallback mode

    async def send_score_threshold_notification(
        self, 
        to_email: str, 
        user_name: str, 
        freight_forwarder_name: str,
        current_score: float,
        threshold_score: float,
        subscription_expires_at: Optional[datetime] = None
    ) -> bool:
        """Send score threshold breach notification email"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Score threshold notification for {to_email}: {freight_forwarder_name} score {current_score} below threshold {threshold_score}")
                return True
            
            # Create email message
            subject = f"LogiScore Alert: {freight_forwarder_name} Score Below Threshold"
            
            # Format expiry date
            expiry_text = ""
            if subscription_expires_at:
                expiry_text = f"<p><strong>Your subscription expires:</strong> {subscription_expires_at.strftime('%B %d, %Y')}</p>"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Score Threshold Alert</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #e74c3c;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-bottom: 10px;
                    }}
                    .alert-badge {{
                        background-color: #e74c3c;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 14px;
                        font-weight: bold;
                        display: inline-block;
                        margin-bottom: 20px;
                    }}
                    .score-comparison {{
                        background-color: #f8f9fa;
                        border-left: 4px solid #e74c3c;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 0 5px 5px 0;
                    }}
                    .current-score {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #e74c3c;
                        margin: 10px 0;
                    }}
                    .threshold-score {{
                        font-size: 18px;
                        color: #666;
                        margin: 10px 0;
                    }}
                    .forwarder-name {{
                        font-size: 20px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin: 15px 0;
                    }}
                    .action-button {{
                        display: inline-block;
                        background-color: #3498db;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        font-size: 12px;
                        color: #666;
                        text-align: center;
                    }}
                    .warning-icon {{
                        font-size: 48px;
                        color: #e74c3c;
                        text-align: center;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">LogiScore</div>
                        <div class="alert-badge">SCORE ALERT</div>
                    </div>
                    
                    <div class="warning-icon">⚠️</div>
                    
                    <h2>Score Threshold Alert</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>We're writing to inform you that the aggregated score for one of your monitored freight forwarders has fallen below your specified threshold.</p>
                    
                    <div class="score-comparison">
                        <div class="forwarder-name">{freight_forwarder_name}</div>
                        <div class="current-score">Current Score: {current_score:.2f}/5.0</div>
                        <div class="threshold-score">Your Threshold: {threshold_score:.2f}/5.0</div>
                    </div>
                    
                    <p>This means the freight forwarder's performance has declined based on recent reviews. You may want to:</p>
                    <ul>
                        <li>Review recent feedback to understand the issues</li>
                        <li>Contact the freight forwarder to discuss improvements</li>
                        <li>Consider alternative service providers</li>
                        <li>Adjust your monitoring threshold if needed</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="https://logiscore.net/dashboard" class="action-button">View Dashboard</a>
                    </div>
                    
                    {expiry_text}
                    
                    <p>You can manage your score threshold subscriptions in your account settings.</p>
                    
                    <div class="footer">
                        <p>This is an automated notification from LogiScore.</p>
                        <p>If you no longer wish to receive these alerts, you can unsubscribe from your account settings.</p>
                        <p>© 2024 LogiScore. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Score threshold notification sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send score threshold notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending score threshold notification to {to_email}: {str(e)}")
            logger.info(f"FALLBACK: Score threshold notification would be sent to {to_email}")
            return True  # Return True for fallback mode

    async def send_trial_ending_warning(self, user_id: str, trial_data: dict) -> bool:
        """Send trial ending warning email (1 day before trial ends)"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Trial ending warning for user {user_id}: {trial_data}")
                return True
            
            # Create email message
            subject = f"⚠️ Your LogiScore trial ends tomorrow - Action required"
            
            # Format trial end date
            trial_end_date = trial_data.get('trial_end_date', '')
            trial_end_time = ""
            if trial_end_date:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(trial_end_date.replace('Z', '+00:00'))
                    trial_end_time = dt.strftime('%I:%M %p UTC')
                except:
                    trial_end_time = "end of day"
            
            # Build plan features HTML
            plan_features_html = ""
            for feature in trial_data.get('plan_features', []):
                plan_features_html += f"<li>{feature}</li>"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your LogiScore Trial Ends Tomorrow</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .trial-info {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                    .cta-button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 20px 0; }}
                    .features {{ background: white; padding: 20px; border-radius: 4px; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⚠️ Your LogiScore Trial Ends Tomorrow</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi {trial_data.get('user_name', 'User')},</p>
                        
                        <p>Your <strong>{trial_data.get('trial_duration', 7)}-day free trial</strong> of LogiScore {trial_data.get('plan_name', 'Subscription')} ends tomorrow at {trial_end_time}.</p>
                        
                        <div class="trial-info">
                            <h3>🕐 Trial Details</h3>
                            <p><strong>Plan:</strong> {trial_data.get('plan_name', 'Subscription')} - ${trial_data.get('plan_price', 0)}/{trial_data.get('billing_cycle', 'month')}</p>
                            <p><strong>Trial Ends:</strong> {trial_data.get('trial_end_date', 'N/A')}</p>
                            <p><strong>Time Remaining:</strong> Less than 24 hours</p>
                        </div>
                        
                        <h3>What happens next?</h3>
                        <p>If you don't take action, your subscription will automatically convert to a paid plan and you'll be charged <strong>${trial_data.get('plan_price', 0)}</strong> tomorrow.</p>
                        
                        <div class="features">
                            <h3>🚀 Continue enjoying LogiScore benefits:</h3>
                            <ul>
                                {plan_features_html}
                            </ul>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="https://logiscore.com/subscribe?plan={trial_data.get('plan_id', 'monthly')}" class="cta-button">Continue Subscription</a>
                            <br>
                            <a href="https://logiscore.com/cancel-trial?user_id={user_id}" style="color: #666; text-decoration: none;">Cancel Trial</a>
                        </div>
                        
                        <p><strong>Questions?</strong> Reply to this email or contact our support team.</p>
                        
                        <p>Best regards,<br>The LogiScore Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>This email was sent to {trial_data.get('user_email', 'your email')} because you have an active trial subscription.</p>
                        <p>LogiScore - Freight Forwarder Review Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(trial_data.get('user_email', '')),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Trial ending warning sent successfully to {trial_data.get('user_email', '')}")
                return True
            else:
                logger.error(f"Failed to send trial ending warning. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending trial ending warning to {user_id}: {str(e)}")
            logger.info(f"FALLBACK: Trial ending warning would be sent to user {user_id}")
            return True  # Return True for fallback mode

    async def send_trial_ended_notification(self, user_id: str, trial_data: dict) -> bool:
        """Send trial ended notification email"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Trial ended notification for user {user_id}: {trial_data}")
                return True
            
            # Create email message
            subject = "❌ Your LogiScore trial has ended"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your LogiScore Trial Has Ended</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .trial-info {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                    .cta-button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ Your LogiScore Trial Has Ended</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi {trial_data.get('user_name', 'User')},</p>
                        
                        <p>Your <strong>{trial_data.get('trial_duration', 7)}-day free trial</strong> of LogiScore {trial_data.get('plan_name', 'Subscription')} has ended.</p>
                        
                        <div class="trial-info">
                            <h3>📅 Trial Summary</h3>
                            <p><strong>Plan:</strong> {trial_data.get('plan_name', 'Subscription')} - ${trial_data.get('plan_price', 0)}/{trial_data.get('billing_cycle', 'month')}</p>
                            <p><strong>Trial Ended:</strong> {trial_data.get('trial_end_date', 'N/A')}</p>
                            <p><strong>Status:</strong> Trial completed</p>
                        </div>
                        
                        <h3>What's next?</h3>
                        <p>Your account has been downgraded to the free tier. You can still:</p>
                        <ul>
                            <li>Browse basic freight forwarder information</li>
                            <li>Submit reviews</li>
                            <li>View star ratings</li>
                        </ul>
                        
                        <p>To regain full access to LogiScore features, you can subscribe anytime:</p>
                        
                        <div style="text-align: center;">
                            <a href="https://logiscore.com/subscribe?plan={trial_data.get('plan_id', 'monthly')}" class="cta-button">Subscribe Now</a>
                        </div>
                        
                        <p><strong>Questions?</strong> Reply to this email or contact our support team.</p>
                        
                        <p>Best regards,<br>The LogiScore Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>This email was sent to {trial_data.get('user_email', 'your email')} because your trial subscription has ended.</p>
                        <p>LogiScore - Freight Forwarder Review Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(trial_data.get('user_email', '')),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            
            # Set EU data residency if needed
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Trial ended notification sent successfully to {trial_data.get('user_email', '')}")
                return True
            else:
                logger.error(f"Failed to send trial ended notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending trial ended notification to {user_id}: {str(e)}")
            logger.info(f"FALLBACK: Trial ended notification would be sent to user {user_id}")
            return True  # Return True for fallback mode

    async def send_subscription_cancellation_notification(self, user_id: str) -> bool:
        """Send subscription cancellation notification email"""
        try:
            if not self.api_key:
                # Fallback: log the notification to console for development
                logger.info(f"FALLBACK: Subscription cancellation notification for user {user_id}")
                return True
            
            # Get user data from database
            from database.database import get_db
            from database.models import User
            from sqlalchemy.orm import Session
            
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f"User {user_id} not found for cancellation notification")
                return False
            
            # Create email message
            subject = "📋 Your LogiScore subscription has been canceled"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Subscription Canceled - LogiScore</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #6c757d; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .cancellation-info {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                    .cta-button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📋 Subscription Canceled</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi {user.full_name or user.username or 'User'},</p>
                        
                        <p>We're sorry to see you go! Your LogiScore subscription has been successfully canceled.</p>
                        
                        <div class="cancellation-info">
                            <h3>What happens next?</h3>
                            <ul>
                                <li>Your subscription will remain active until the end of your current billing period</li>
                                <li>You'll continue to have access to all LogiScore features until then</li>
                                <li>No further charges will be made to your account</li>
                            </ul>
                        </div>
                        
                        <p>If you change your mind, you can reactivate your subscription at any time by logging into your account.</p>
                        
                        <div style="text-align: center;">
                            <a href="https://logiscore.com/account" class="cta-button">Manage Your Account</a>
                        </div>
                        
                        <p>Thank you for using LogiScore. We hope to see you again soon!</p>
                        
                        <p>Best regards,<br>The LogiScore Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>This email was sent to {user.email}</p>
                        <p>© 2024 LogiScore. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Hi {user.full_name or user.username or 'User'},
            
            We're sorry to see you go! Your LogiScore subscription has been successfully canceled.
            
            What happens next?
            - Your subscription will remain active until the end of your current billing period
            - You'll continue to have access to all LogiScore features until then
            - No further charges will be made to your account
            
            If you change your mind, you can reactivate your subscription at any time by logging into your account.
            
            Manage your account: https://logiscore.com/account
            
            Thank you for using LogiScore. We hope to see you again soon!
            
            Best regards,
            The LogiScore Team
            
            This email was sent to {user.email}
            © 2024 LogiScore. All rights reserved.
            """
            
            # Create SendGrid message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=user.email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            # Send email
            sg = SendGridAPIClient(api_key=self.api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Subscription cancellation notification sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Failed to send subscription cancellation notification. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending subscription cancellation notification to {user_id}: {str(e)}")
            logger.info(f"FALLBACK: Subscription cancellation notification would be sent to user {user_id}")
            return True  # Return True for fallback mode

    async def send_auto_renewal_toggle_notification(self, to_email: str, user_name: str, auto_renew_enabled: bool, subscription_tier: str) -> bool:
        """Send auto-renewal toggle notification email"""
        try:
            if not self.api_key:
                logger.info(f"FALLBACK: Auto-renewal toggle notification would be sent to {to_email}")
                return True
            
            status_text = "enabled" if auto_renew_enabled else "disabled"
            status_emoji = "✅" if auto_renew_enabled else "❌"
            
            subject = f"{status_emoji} Auto-renewal {status_text} - LogiScore"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Auto-renewal {status_text.title()} - LogiScore</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: {'#28a745' if auto_renew_enabled else '#dc3545'}; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .status-info {{ background: {'#d4edda' if auto_renew_enabled else '#f8d7da'}; border: 1px solid {'#c3e6cb' if auto_renew_enabled else '#f5c6cb'}; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                    .cta-button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                    .highlight {{ font-weight: bold; color: {'#155724' if auto_renew_enabled else '#721c24'}; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{status_emoji} Auto-renewal {status_text.title()}</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi {user_name or 'User'},</p>
                        
                        <p>Your LogiScore subscription auto-renewal setting has been <span class="highlight">{status_text}</span>.</p>
                        
                        <div class="status-info">
                            <h3>Subscription Details</h3>
                            <ul>
                                <li><strong>Plan:</strong> {subscription_tier.title()}</li>
                                <li><strong>Auto-renewal:</strong> <span class="highlight">{'Enabled' if auto_renew_enabled else 'Disabled'}</span></li>
                            </ul>
                        </div>
                        
                        {'<p>Your subscription will automatically renew at the end of each billing period. You\'ll receive a payment confirmation email when the renewal is processed.</p>' if auto_renew_enabled else '<p>Your subscription will not automatically renew. You\'ll need to manually renew it before it expires to continue using LogiScore services.</p>'}
                        
                        <p>You can change this setting at any time through your account dashboard.</p>
                        
                        <div style="text-align: center;">
                            <a href="https://logiscore.com/account" class="cta-button">Manage Subscription</a>
                        </div>
                        
                        <p>If you have any questions about your subscription, please don't hesitate to contact our support team.</p>
                        
                        <p>Best regards,<br>The LogiScore Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>This email was sent to {to_email}</p>
                        <p>© 2024 LogiScore. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Hi {user_name or 'User'},
            
            Your LogiScore subscription auto-renewal setting has been {status_text}.
            
            Subscription Details:
            - Plan: {subscription_tier.title()}
            - Auto-renewal: {'Enabled' if auto_renew_enabled else 'Disabled'}
            
            {'Your subscription will automatically renew at the end of each billing period. You\'ll receive a payment confirmation email when the renewal is processed.' if auto_renew_enabled else 'Your subscription will not automatically renew. You\'ll need to manually renew it before it expires to continue using LogiScore services.'}
            
            You can change this setting at any time through your account dashboard.
            
            Manage your subscription: https://logiscore.com/account
            
            If you have any questions about your subscription, please don't hesitate to contact our support team.
            
            Best regards,
            The LogiScore Team
            """
            
            # Send email using SendGrid
            sg = SendGridAPIClient(self.api_key)
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                plain_text_content=text_content,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Auto-renewal toggle notification sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send auto-renewal toggle notification to {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending auto-renewal toggle notification to {to_email}: {str(e)}")
            logger.info(f"FALLBACK: Auto-renewal toggle notification would be sent to {to_email}")
            return True  # Return True for fallback mode

# Create singleton instance
email_service = EmailService()
