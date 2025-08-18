from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Review, ReviewCategoryScore, FreightForwarder, User
from email_service import email_service
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class ReviewThankYouRequest:
    def __init__(self, review_id: str):
        self.review_id = review_id

@router.post("/review-thank-you")
async def send_review_thank_you_email(
    request: dict,
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
        review_id = request.get("review_id")
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="review_id is required"
            )
        
        # Get review with related data
        review = db.query(Review).filter(Review.id == review_id).first()
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
        
        # Get category scores for the review
        category_scores = db.query(ReviewCategoryScore).filter(
            ReviewCategoryScore.review_id == review_id
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
