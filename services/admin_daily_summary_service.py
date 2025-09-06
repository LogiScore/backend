import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, distinct
from datetime import datetime, timedelta
from database.models import User, FreightForwarder, Review, ReviewCategoryScore
from email_service import email_service

logger = logging.getLogger(__name__)

class AdminDailySummaryService:
    """Service for generating and sending daily admin summary emails"""
    
    def __init__(self):
        self.email_service = email_service
    
    async def generate_daily_summary(self, db: Session, target_date: datetime = None) -> Dict[str, Any]:
        """Generate daily summary data for admin email"""
        try:
            # Use provided date or yesterday
            if target_date is None:
                target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            
            # Calculate date range for the previous day
            start_of_day = target_date
            end_of_day = target_date + timedelta(days=1)
            
            logger.info(f"Generating daily summary for {start_of_day.date()}")
            
            # Get new reviews from the previous day
            new_reviews = db.query(Review).filter(
                Review.created_at >= start_of_day,
                Review.created_at < end_of_day,
                Review.is_active == True
            ).all()
            
            # Get total reviews count
            total_reviews = db.query(Review).filter(Review.is_active == True).count()
            
            # Get new freight forwarders from the previous day
            new_forwarders = db.query(FreightForwarder).filter(
                FreightForwarder.created_at >= start_of_day,
                FreightForwarder.created_at < end_of_day
            ).all()
            
            # Get total freight forwarders count
            total_forwarders = db.query(FreightForwarder).count()
            
            # Get new review locations (unique city, country combinations) from the previous day
            new_locations = db.query(
                Review.city, 
                Review.country
            ).filter(
                Review.created_at >= start_of_day,
                Review.created_at < end_of_day,
                Review.is_active == True,
                Review.city.isnot(None),
                Review.country.isnot(None)
            ).distinct().all()
            
            # Get total unique review locations
            total_locations = db.query(
                Review.city, 
                Review.country
            ).filter(
                Review.is_active == True,
                Review.city.isnot(None),
                Review.country.isnot(None)
            ).distinct().count()
            
            # Get new users from the previous day
            new_users = db.query(User).filter(
                User.created_at >= start_of_day,
                User.created_at < end_of_day,
                User.is_active == True
            ).all()
            
            # Get total users count
            total_users = db.query(User).filter(User.is_active == True).count()
            
            # Get new locations added to existing forwarders (locations that appeared in reviews for existing forwarders)
            existing_forwarder_ids = db.query(FreightForwarder.id).filter(
                FreightForwarder.created_at < start_of_day
            ).subquery()
            
            new_forwarder_locations = db.query(
                Review.city,
                Review.country,
                FreightForwarder.name
            ).join(
                FreightForwarder, Review.freight_forwarder_id == FreightForwarder.id
            ).filter(
                Review.created_at >= start_of_day,
                Review.created_at < end_of_day,
                Review.is_active == True,
                Review.city.isnot(None),
                Review.country.isnot(None),
                FreightForwarder.id.in_(db.query(FreightForwarder.id).filter(FreightForwarder.created_at < start_of_day))
            ).distinct().all()
            
            # Format the summary data
            summary_data = {
                'date': start_of_day.strftime('%Y-%m-%d'),
                'new_reviews': {
                    'count': len(new_reviews),
                    'total': total_reviews,
                    'reviews': self._format_reviews_for_email(new_reviews, db)
                },
                'new_forwarders': {
                    'count': len(new_forwarders),
                    'total': total_forwarders,
                    'forwarders': self._format_forwarders_for_email(new_forwarders)
                },
                'new_review_locations': {
                    'count': len(new_locations),
                    'total': total_locations,
                    'locations': self._format_locations_for_email(new_locations)
                },
                'new_users': {
                    'count': len(new_users),
                    'total': total_users,
                    'users': self._format_users_for_email(new_users)
                },
                'new_forwarder_locations': {
                    'count': len(new_forwarder_locations),
                    'locations': self._format_forwarder_locations_for_email(new_forwarder_locations)
                }
            }
            
            logger.info(f"Daily summary generated: {len(new_reviews)} new reviews, {len(new_forwarders)} new forwarders, {len(new_locations)} new locations, {len(new_users)} new users")
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {str(e)}")
            raise
    
    def _format_reviews_for_email(self, reviews: List[Review], db: Session) -> List[Dict[str, Any]]:
        """Format reviews for email display"""
        formatted_reviews = []
        
        for review in reviews[:10]:  # Limit to 10 most recent reviews
            # Get freight forwarder name
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == review.freight_forwarder_id
            ).first()
            
            # Get user name
            user_name = "Anonymous"
            if review.user:
                user_name = review.user.full_name or review.user.username or review.user.email.split('@')[0]
            
            formatted_reviews.append({
                'id': str(review.id),
                'freight_forwarder_name': freight_forwarder.name if freight_forwarder else 'Unknown',
                'user_name': user_name,
                'rating': float(review.aggregate_rating) if review.aggregate_rating else 0,
                'city': review.city or 'N/A',
                'country': review.country or 'N/A',
                'review_type': review.review_type or 'general',
                'shipment_reference': review.shipment_reference or 'N/A',
                'created_at': review.created_at.strftime('%H:%M UTC') if review.created_at else 'N/A'
            })
        
        return formatted_reviews
    
    def _format_forwarders_for_email(self, forwarders: List[FreightForwarder]) -> List[Dict[str, Any]]:
        """Format freight forwarders for email display"""
        formatted_forwarders = []
        
        for forwarder in forwarders:
            formatted_forwarders.append({
                'id': str(forwarder.id),
                'name': forwarder.name,
                'website': forwarder.website or 'N/A',
                'headquarters_country': forwarder.headquarters_country or 'N/A',
                'created_at': forwarder.created_at.strftime('%H:%M UTC') if forwarder.created_at else 'N/A'
            })
        
        return formatted_forwarders
    
    def _format_locations_for_email(self, locations: List[tuple]) -> List[Dict[str, str]]:
        """Format locations for email display"""
        formatted_locations = []
        
        for city, country in locations:
            formatted_locations.append({
                'city': city or 'N/A',
                'country': country or 'N/A'
            })
        
        return formatted_locations
    
    def _format_users_for_email(self, users: List[User]) -> List[Dict[str, Any]]:
        """Format users for email display"""
        formatted_users = []
        
        for user in users:
            formatted_users.append({
                'id': str(user.id),
                'email': user.email,
                'username': user.username or 'N/A',
                'full_name': user.full_name or 'N/A',
                'user_type': user.user_type or 'N/A',
                'subscription_tier': user.subscription_tier or 'free',
                'created_at': user.created_at.strftime('%H:%M UTC') if user.created_at else 'N/A'
            })
        
        return formatted_users
    
    def _format_forwarder_locations_for_email(self, forwarder_locations: List[tuple]) -> List[Dict[str, str]]:
        """Format forwarder locations for email display"""
        formatted_locations = []
        
        for city, country, forwarder_name in forwarder_locations:
            formatted_locations.append({
                'city': city or 'N/A',
                'country': country or 'N/A',
                'forwarder_name': forwarder_name or 'Unknown'
            })
        
        return formatted_locations
    
    async def send_daily_summary_email(self, summary_data: Dict[str, Any]) -> bool:
        """Send daily summary email to admin"""
        try:
            admin_email = "admin@logiscore.net"
            
            # Create email subject
            subject = f"LogiScore Daily Summary - {summary_data['date']}"
            
            # Generate HTML content
            html_content = self._generate_summary_html(summary_data)
            
            # Create SendGrid message
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, HtmlContent
            
            message = Mail(
                from_email=Email(self.email_service.from_email, self.email_service.from_name),
                to_emails=To(admin_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            # Send email
            sg = SendGridAPIClient(self.email_service.api_key)
            
            # Set EU data residency if needed
            import os
            if os.getenv('SENDGRID_EU_RESIDENCY', 'false').lower() == 'true':
                sg.set_sendgrid_data_residency("eu")
            
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Daily summary email sent successfully to {admin_email}")
                return True
            else:
                logger.error(f"Failed to send daily summary email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending daily summary email: {str(e)}")
            return False
    
    def _generate_summary_html(self, summary_data: Dict[str, Any]) -> str:
        """Generate HTML content for the daily summary email"""
        
        # Format review data
        reviews_html = ""
        for review in summary_data['new_reviews']['reviews']:
            rating_stars = "⭐" * int(review['rating']) + "☆" * (5 - int(review['rating']))
            reviews_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{review['freight_forwarder_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{review['user_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6; text-align: center;">{rating_stars} ({review['rating']}/5)</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{review['city']}, {review['country']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{review['created_at']}</td>
            </tr>
            """
        
        # Format forwarder data
        forwarders_html = ""
        for forwarder in summary_data['new_forwarders']['forwarders']:
            forwarders_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{forwarder['name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{forwarder['website']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{forwarder['headquarters_country']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{forwarder['created_at']}</td>
            </tr>
            """
        
        # Format location data
        locations_html = ""
        for location in summary_data['new_review_locations']['locations']:
            locations_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location['city']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location['country']}</td>
            </tr>
            """
        
        # Format user data
        users_html = ""
        for user in summary_data['new_users']['users']:
            users_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{user['email']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{user['full_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{user['user_type']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{user['subscription_tier']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{user['created_at']}</td>
            </tr>
            """
        
        # Format forwarder location data
        forwarder_locations_html = ""
        for location in summary_data['new_forwarder_locations']['locations']:
            forwarder_locations_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location['forwarder_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location['city']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location['country']}</td>
            </tr>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LogiScore Daily Summary - {summary_data['date']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
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
                .summary-stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 5px;
                }}
                .stat-label {{
                    color: #6c757d;
                    font-size: 14px;
                }}
                .section {{
                    background: white;
                    margin: 20px 0;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .section-header {{
                    background: #f8f9fa;
                    padding: 15px 20px;
                    border-bottom: 1px solid #dee2e6;
                    font-weight: bold;
                    color: #495057;
                }}
                .section-content {{
                    padding: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background: #f8f9fa;
                    padding: 12px 8px;
                    text-align: left;
                    font-weight: bold;
                    border-bottom: 2px solid #dee2e6;
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
                .no-data {{
                    text-align: center;
                    color: #6c757d;
                    font-style: italic;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 LogiScore Daily Summary</h1>
                <p>Activity Report for {summary_data['date']}</p>
            </div>
            
            <div class="content">
                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-number">{summary_data['new_reviews']['count']}</div>
                        <div class="stat-label">New Reviews</div>
                        <div style="font-size: 12px; color: #6c757d;">Total: {summary_data['new_reviews']['total']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{summary_data['new_forwarders']['count']}</div>
                        <div class="stat-label">New Forwarders</div>
                        <div style="font-size: 12px; color: #6c757d;">Total: {summary_data['new_forwarders']['total']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{summary_data['new_review_locations']['count']}</div>
                        <div class="stat-label">New Review Locations</div>
                        <div style="font-size: 12px; color: #6c757d;">Total: {summary_data['new_review_locations']['total']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{summary_data['new_users']['count']}</div>
                        <div class="stat-label">New Users</div>
                        <div style="font-size: 12px; color: #6c757d;">Total: {summary_data['new_users']['total']}</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">📝 New Reviews ({summary_data['new_reviews']['count']})</div>
                    <div class="section-content">
                        {f'''
                        <table>
                            <thead>
                                <tr>
                                    <th>Company</th>
                                    <th>Reviewer</th>
                                    <th>Rating</th>
                                    <th>Location</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {reviews_html}
                            </tbody>
                        </table>
                        ''' if summary_data['new_reviews']['reviews'] else '<div class="no-data">No new reviews today</div>'}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">🚢 New Freight Forwarders ({summary_data['new_forwarders']['count']})</div>
                    <div class="section-content">
                        {f'''
                        <table>
                            <thead>
                                <tr>
                                    <th>Company Name</th>
                                    <th>Website</th>
                                    <th>Headquarters</th>
                                    <th>Added</th>
                                </tr>
                            </thead>
                            <tbody>
                                {forwarders_html}
                            </tbody>
                        </table>
                        ''' if summary_data['new_forwarders']['forwarders'] else '<div class="no-data">No new freight forwarders today</div>'}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">📍 New Review Locations ({summary_data['new_review_locations']['count']})</div>
                    <div class="section-content">
                        {f'''
                        <table>
                            <thead>
                                <tr>
                                    <th>City</th>
                                    <th>Country</th>
                                </tr>
                            </thead>
                            <tbody>
                                {locations_html}
                            </tbody>
                        </table>
                        ''' if summary_data['new_review_locations']['locations'] else '<div class="no-data">No new review locations today</div>'}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">👥 New Users ({summary_data['new_users']['count']})</div>
                    <div class="section-content">
                        {f'''
                        <table>
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Subscription</th>
                                    <th>Joined</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users_html}
                            </tbody>
                        </table>
                        ''' if summary_data['new_users']['users'] else '<div class="no-data">No new users today</div>'}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">🏢 New Locations for Existing Forwarders ({summary_data['new_forwarder_locations']['count']})</div>
                    <div class="section-content">
                        {f'''
                        <table>
                            <thead>
                                <tr>
                                    <th>Company</th>
                                    <th>City</th>
                                    <th>Country</th>
                                </tr>
                            </thead>
                            <tbody>
                                {forwarder_locations_html}
                            </tbody>
                        </table>
                        ''' if summary_data['new_forwarder_locations']['locations'] else '<div class="no-data">No new locations for existing forwarders today</div>'}
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated daily summary from the LogiScore platform.</p>
                    <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <p>&copy; 2025 LogiScore. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    async def run_daily_summary(self, db: Session) -> Dict[str, Any]:
        """Run the complete daily summary process"""
        try:
            logger.info("Starting daily admin summary process")
            
            # Generate summary data
            summary_data = await self.generate_daily_summary(db)
            
            # Send email
            email_sent = await self.send_daily_summary_email(summary_data)
            
            result = {
                'success': True,
                'email_sent': email_sent,
                'summary_data': summary_data,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Daily admin summary completed. Email sent: {email_sent}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run daily summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }

# Create singleton instance
admin_daily_summary_service = AdminDailySummaryService()
