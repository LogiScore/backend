from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime

from ..database.database import get_db
from ..database.models import Review, ReviewCategoryScore, ReviewQuestion, FreightForwarder
from ..auth.auth import get_current_user_optional

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

# Pydantic models for request/response
from pydantic import BaseModel

class QuestionRating(BaseModel):
    question: str
    rating: int

class CategoryRating(BaseModel):
    category: str
    questions: List[QuestionRating]

class ReviewCreate(BaseModel):
    freight_forwarder_id: UUID
    branch_id: Optional[UUID] = None
    review_type: str = "general"
    is_anonymous: bool = False
    review_weight: float = 1.0
    category_ratings: List[CategoryRating]
    aggregate_rating: float
    weighted_rating: float

class ReviewResponse(BaseModel):
    id: UUID
    freight_forwarder_id: UUID
    branch_id: Optional[UUID]
    review_type: str
    is_anonymous: bool
    review_weight: float
    aggregate_rating: float
    weighted_rating: float
    total_questions_rated: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Create a new review"""
    
    # Validate freight forwarder exists
    freight_forwarder = db.query(FreightForwarder).filter(
        FreightForwarder.id == review_data.freight_forwarder_id
    ).first()
    
    if not freight_forwarder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Freight forwarder not found"
        )
    
    # Create the main review record
    review = Review(
        freight_forwarder_id=review_data.freight_forwarder_id,
        branch_id=review_data.branch_id,
        user_id=current_user.get("id") if current_user else None,
        review_type=review_data.review_type,
        is_anonymous=review_data.is_anonymous,
        review_weight=review_data.review_weight,
        aggregate_rating=review_data.aggregate_rating,
        weighted_rating=review_data.weighted_rating,
        total_questions_rated=sum(len(cat.questions) for cat in review_data.category_ratings)
    )
    
    db.add(review)
    db.flush()  # Get the review ID
    
    # Create category scores for each question
    for category in review_data.category_ratings:
        for question in category.questions:
            # Get question details from review_questions table
            question_detail = db.query(ReviewQuestion).filter(
                ReviewQuestion.question_id == question.question
            ).first()
            
            if question_detail:
                category_score = ReviewCategoryScore(
                    review_id=review.id,
                    category_id=category.category,
                    category_name=question_detail.category_name,
                    question_id=question.question,
                    question_text=question_detail.question_text,
                    rating=question.rating,
                    rating_definition=question_detail.rating_definitions.get(str(question.rating), ""),
                    weight=review_data.review_weight
                )
                db.add(category_score)
    
    db.commit()
    db.refresh(review)
    
    return review

@router.get("/questions", response_model=List[dict])
async def get_review_questions(db: Session = Depends(get_db)):
    """Get all review questions for the frontend form"""
    
    questions = db.query(ReviewQuestion).filter(
        ReviewQuestion.is_active == True
    ).all()
    
    # Group questions by category
    categories = {}
    for question in questions:
        if question.category_id not in categories:
            categories[question.category_id] = {
                "id": question.category_id,
                "name": question.category_name,
                "questions": []
            }
        
        categories[question.category_id]["questions"].append({
            "id": question.question_id,
            "text": question.question_text,
            "ratingDefinitions": question.rating_definitions
        })
    
    return list(categories.values())

@router.get("/freight-forwarder/{freight_forwarder_id}", response_model=List[ReviewResponse])
async def get_reviews_by_freight_forwarder(
    freight_forwarder_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific freight forwarder"""
    
    reviews = db.query(Review).filter(
        Review.freight_forwarder_id == freight_forwarder_id
    ).order_by(Review.created_at.desc()).all()
    
    return reviews

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review 