from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Review, ReviewCategoryScore, FreightForwarder, User
from email_service import email_service
from typing import List
import logging
from pydantic import BaseModel, EmailStr, validator
import re
import uuid
from auth.auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class ReviewThankYouRequest(BaseModel):
    review_id: str
    
    @validator('review_id')
    def validate_review_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('review_id cannot be empty')
        # Validate that it's a valid UUID format
        try:
            uuid.UUID(v.strip())
        except ValueError:
            raise ValueError('review_id must be a valid UUID')
        return v.strip()

class ContactFormData(BaseModel):
    name: str
    email: EmailStr
    contact_reason: str
    subject: str
    message: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Name must be less than 100 characters')
        return v.strip()
    
    @validator('contact_reason')
    def validate_contact_reason(cls, v):
        valid_reasons = ['feedback', 'support', 'billing', 'reviews', 'privacy', 'general']
        if v.lower() not in valid_reasons:
            raise ValueError(f'Contact reason must be one of: {", ".join(valid_reasons)}')
        return v.lower()
    
    @validator('subject')
    def validate_subject(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Subject must be at least 5 characters long')
        if len(v.strip()) > 200:
            raise ValueError('Subject must be less than 200 characters')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        if len(v.strip()) > 2000:
            raise ValueError('Message must be less than 2000 characters')
        # Basic XSS protection - remove script tags
        v = re.sub(r'<script[^>]*>.*?</script>', '', v, flags=re.IGNORECASE | re.DOTALL)
        return v.strip()

@router.post("/contact-form")
async def send_contact_form(contact_data: ContactFormData):
    """
    Handle contact form submissions with intelligent email routing and acknowledgment sending.
    
    Routes messages to appropriate teams based on contact_reason:
    - feedback -> feedback@logiscore.net
    - support -> support@logiscore.net
    - billing -> accounts@logiscore.net
    - reviews -> dispute@logiscore.net
    - privacy -> dpo@logiscore.net
    - general -> support@logiscore.net (default)
    """
    try:
        logger.info(f"Contact form submission received from {contact_data.email} - Reason: {contact_data.contact_reason}")
        
        # Convert to dict for email service
        contact_dict = contact_data.dict()
        
        # 1. Determine routing email based on contact_reason
        routing_email = email_service.get_routing_email(contact_data.contact_reason)
        logger.info(f"Routing contact form to: {routing_email}")
        
        # 2. Send email to appropriate team
        team_email_sent = await email_service.send_contact_form_team_email(contact_dict, routing_email)
        
        # 3. Send acknowledgment to user
        ack_email_sent = await email_service.send_contact_form_acknowledgment(contact_dict)
        
        # Log success
        logger.info(f"Contact form processed successfully for {contact_data.email}. Team email: {team_email_sent}, Acknowledgment: {ack_email_sent}")
        
        return {
            "message": "Contact form submitted successfully",
            "email_sent": team_email_sent,
            "acknowledgment_sent": ack_email_sent,
            "routed_to": routing_email
        }
        
    except Exception as e:
        logger.error(f"Error processing contact form from {contact_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process contact form. Please try again later."
        )

@router.post("/review-thank-you")
async def send_review_thank_you_email(
    request: ReviewThankYouRequest,
    db: Session = Depends(get_db)
):
    """
    Send thank you email after review submission
    
    Expected request format:
    {
        "review_id": "uuid-string"
    }
    """
    try:
        review_id = request.review_id
        
        # Convert string to UUID object for database query
        try:
            review_uuid = uuid.UUID(review_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid review_id format - must be a valid UUID"
            )
        
        # Get review with related data using UUID object
        review = db.query(Review).filter(Review.id == review_uuid).first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        # Get freight forwarder name
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == review.freight_forwarder_id
        ).first()
        if not freight_forwarder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freight forwarder not found"
            )
        
        # Get user information (if not anonymous)
        user_name = "Anonymous User"
        user_email = None
        
        if review.user_id and not review.is_anonymous:
            user = db.query(User).filter(User.id == review.user_id).first()
            if user:
                user_name = user.full_name or user.username or user.email
                user_email = user.email
        
        # If anonymous review or no user email, we can't send email
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send email for anonymous reviews or users without email"
            )
        
        # Get category scores for the review using UUID object
        category_scores = db.query(ReviewCategoryScore).filter(
            ReviewCategoryScore.review_id == review_uuid
        ).all()
        
        # Format category scores for email
        formatted_scores = []
        for score in category_scores:
            formatted_scores.append({
                "category_name": score.category_name,
                "question_text": score.question_text,
                "rating": score.rating,
                "rating_definition": score.rating_definition
            })
        
        # Get location information
        city = review.city or "Not specified"
        country = review.country or "Not specified"
        
        # Send thank you email
        email_sent = await email_service.send_review_thank_you_email(
            to_email=user_email,
            user_name=user_name,
            freight_forwarder_name=freight_forwarder.name,
            city=city,
            country=country,
            category_scores=formatted_scores
        )
        
        if email_sent:
            logger.info(f"Review thank you email sent successfully for review {review_id}")
            return {
                "success": True,
                "message": "Thank you email sent successfully",
                "email_sent_to": user_email
            }
        else:
            logger.error(f"Failed to send review thank you email for review {review_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send thank you email"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in send_review_thank_you_email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while sending thank you email"
        )

class AdminNewForwarderRequest(BaseModel):
    forwarder_data: dict
    creator_data: dict

@router.post("/admin-new-forwarder")
async def send_admin_new_forwarder_notification(
    request: AdminNewForwarderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send notification email to admin when a new freight forwarder is added
    
    Expected request format:
    {
        "forwarder_data": {
            "name": "Company Name",
            "website": "https://example.com",
            "description": "Company description",
            "headquarters_country": "Country",
            "logo_url": "https://example.com/logo.png"
        },
        "creator_data": {
            "id": "user_id",
            "full_name": "User Full Name",
            "email": "user@example.com",
            "username": "username",
            "user_type": "shipper"
        }
    }
    """
    try:
        # Check if user has permission to send admin notifications
        if current_user.user_type not in ["admin", "shipper"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to send admin notifications"
            )
        
        logger.info(f"Admin new forwarder notification requested by {current_user.email}")
        logger.info(f"Company: {request.forwarder_data.get('name')}")
        logger.info(f"Creator: {request.creator_data.get('full_name')}")
        
        # Send admin notification email
        email_sent = await email_service.send_admin_new_forwarder_notification(
            forwarder_data=request.forwarder_data,
            creator_data=request.creator_data
        )
        
        if email_sent:
            logger.info(f"Admin new forwarder notification sent successfully to admin@logiscore.net")
            return {
                "success": True,
                "message": "Admin notification sent successfully",
                "email_sent_to": "admin@logiscore.net"
            }
        else:
            logger.error(f"Failed to send admin new forwarder notification")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send admin notification"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in send_admin_new_forwarder_notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while sending admin notification"
        )
