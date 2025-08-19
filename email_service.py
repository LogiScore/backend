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
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@logiscore.com')
        self.from_name = os.getenv('FROM_NAME', 'LogiScore')
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not found in environment variables. Email sending will be disabled.")
    
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
                <div class="header">
                    <h1>🔐 LogiScore Verification</h1>
                    <p>Your secure access code</p>
                </div>
                
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
                    
                    <p>With your new account, you can:</p>
                    <ul>
                        <li>📝 Write and read authentic reviews</li>
                        <li>⭐ Rate freight forwarders across multiple categories</li>
                        <li>🔍 Search and compare logistics providers</li>
                        <li>💼 Access premium features and insights</li>
                    </ul>
                    
                    <a href="https://logiscore.net" class="cta-button">Get Started Now</a>
                    
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
            if not self.api_key:
                logger.info(f"FALLBACK: Review thank you email would be sent to {to_email}")
                return True
            
            subject = f"Thank you for your review of {freight_forwarder_name}! 🚢"
            
            # Build category scores HTML
            category_scores_html = ""
            for score in category_scores:
                stars = "⭐" * score['rating']
                category_scores_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                        <strong>{score['category_name']}</strong><br>
                        <span style="color: #6c757d; font-size: 14px;">{score['question_text']}</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6; text-align: center;">
                        <span style="font-size: 18px;">{stars}</span><br>
                        <span style="color: #6c757d; font-size: 12px;">{score['rating_definition']}</span>
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
                logger.info(f"Review thank you email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send review thank you email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending review thank you email to {to_email}: {str(e)}")
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

# Create singleton instance
email_service = EmailService()
