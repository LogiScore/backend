import os
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

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

# Create singleton instance
email_service = EmailService()
