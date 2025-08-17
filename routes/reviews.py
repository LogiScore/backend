from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from uuid import UUID
import uuid
import logging
from datetime import datetime

from database.database import get_db
from database.models import Review, ReviewCategoryScore, ReviewQuestion, FreightForwarder
from auth.auth import get_current_user_optional

router = APIRouter(tags=["reviews"])
logger = logging.getLogger(__name__)

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
    location_id: Union[UUID, str]  # Required: location UUID or location name from locations table
    review_type: str = "general"
    is_anonymous: bool = False
    review_weight: float = 1.0
    category_ratings: List[CategoryRating]
    aggregate_rating: float
    weighted_rating: float

class ReviewResponse(BaseModel):
    id: UUID
    freight_forwarder_id: UUID
    location_id: UUID
    city: Optional[str]
    country: Optional[str]
    review_type: str
    is_anonymous: bool
    review_weight: float
    aggregate_rating: float
    weighted_rating: float
    total_questions_rated: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Create a new review"""
    try:
        # Validate freight forwarder exists
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == review_data.freight_forwarder_id
        ).first()
        
        if not freight_forwarder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freight forwarder not found"
            )
        
                # Validate location and extract city/country
        city = None
        country = None
        
        logger.info(f"Validating location_id: {review_data.location_id} (type: {type(review_data.location_id)})")
        
        try:
            # Query the locations table to get city and country
            from sqlalchemy import text
            
            # Try to find location by UUID first, then by name if that fails
            location_query = text("""
                SELECT "UUID", "Location", "City", "Country", "Region"
                FROM locations 
                WHERE "UUID" = :location_id OR "Location" = :location_name
            """)
            
            result = db.execute(location_query, {
                "location_id": review_data.location_id,
                "location_name": review_data.location_id
            })
            location_data = result.fetchone()
            
            if not location_data:
                # Let's also check what locations are available for debugging
                sample_query = text("""
                    SELECT "UUID", "Location", "City", "Country" 
                    FROM locations 
                    LIMIT 5
                """)
                sample_result = db.execute(sample_query)
                sample_locations = sample_result.fetchall()
                
                logger.error(f"Location not found. Sample locations in DB: {sample_locations}")
                logger.error(f"Looking for: {review_data.location_id}")
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Location not found: {review_data.location_id}. Please use a valid location name or UUID."
                )
            
            # Extract city and country from location data
            city = location_data[2] if location_data[2] else None  # City is at index 2
            country = location_data[3] if location_data[3] else None  # Country is at index 3
            
            logger.info(f"Location found: UUID={location_data[0]}, Location={location_data[1]}, City={city}, Country={country}")
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error querying location: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location format. Must be a valid UUID or location name"
            )
        
        # Validate ratings
        if review_data.aggregate_rating < 0 or review_data.aggregate_rating > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aggregate rating must be between 0 and 4"
            )
        
        # Validate category ratings
        if not review_data.category_ratings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one category rating is required"
            )
        
        for category in review_data.category_ratings:
            if not category.questions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category '{category.category}' must have at least one question"
                )
            
            for question in category.questions:
                if question.rating < 0 or question.rating > 4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Question rating must be between 0 and 4, got {question.rating}"
                    )
        
        # Create the main review record
        try:
            logger.info(f"Creating review with data: freight_forwarder_id={review_data.freight_forwarder_id}, city={city}, country={country}")
            
            # Use the location UUID as branch_id to maintain database compatibility
            location_uuid = None
            if location_data and location_data[0]:  # location_data[0] is the UUID
                # Convert the location string to a proper UUID format
                location_string = str(location_data[0])
                try:
                    # If it's already a valid UUID, use it
                    if len(location_string) == 36 and '-' in location_string:
                        location_uuid = UUID(location_string)
                    else:
                        # Convert alphanumeric string to UUID format
                        # Pad with zeros and add hyphens to make it UUID-compliant
                        padded_string = location_string.ljust(32, '0')
                        uuid_string = f"{padded_string[:8]}-{padded_string[8:12]}-{padded_string[12:16]}-{padded_string[16:20]}-{padded_string[20:32]}"
                        location_uuid = UUID(uuid_string)
                        logger.info(f"Converted location string '{location_string}' to UUID: {location_uuid}")
                except ValueError as e:
                    logger.error(f"Error converting location string to UUID: {e}")
                    # Fallback: generate a new UUID based on the location string
                    import hashlib
                    hash_object = hashlib.md5(location_string.encode())
                    hash_hex = hash_object.hexdigest()
                    uuid_string = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
                    location_uuid = UUID(uuid_string)
                    logger.info(f"Generated UUID from hash for location '{location_string}': {location_uuid}")
            
            review = Review(
                freight_forwarder_id=review_data.freight_forwarder_id,
                branch_id=location_uuid,  # Use location UUID as branch_id
                city=city,
                country=country,
                user_id=current_user.get("id") if current_user else None,
                review_type=review_data.review_type,
                is_anonymous=review_data.is_anonymous,
                review_weight=review_data.review_weight,
                aggregate_rating=review_data.aggregate_rating,
                weighted_rating=review_data.weighted_rating,
                total_questions_rated=sum(len(cat.questions) for cat in review_data.category_ratings),
                is_active=True,
                is_verified=False
            )
            
            logger.info(f"Review object created successfully: {review}")
            
        except Exception as e:
            logger.error(f"Error creating Review object: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating review object: {str(e)}"
            )
        
        try:
            db.add(review)
            db.flush()  # Get the review ID
            logger.info(f"Review added to session and flushed, ID: {review.id}")
            
        except Exception as e:
            logger.error(f"Error adding review to database session: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error adding review: {str(e)}"
            )
        
        # Create category scores for each question
        try:
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
                    else:
                        # If question not found, create with basic info
                        category_score = ReviewCategoryScore(
                            review_id=review.id,
                            category_id=category.category,
                            category_name=category.category,
                            question_id=question.question,
                            question_text=f"Question {question.question}",
                            rating=question.rating,
                            rating_definition="",
                            weight=review_data.review_weight
                        )
                        db.add(category_score)
            
            logger.info(f"Category scores created successfully for review {review.id}")
            
        except Exception as e:
            logger.error(f"Error creating category scores: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating category scores: {str(e)}"
            )
        
        try:
            db.commit()
            db.refresh(review)
            logger.info(f"Review committed successfully: {review.id}")
        except Exception as e:
            logger.error(f"Error committing review: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database commit error: {str(e)}"
            )
        
        # Return the created review
        return ReviewResponse(
            id=review.id,
            freight_forwarder_id=review.freight_forwarder_id,
            location_id=review.branch_id,  # Now branch_id contains the location UUID
            city=city,
            country=country,
            review_type=review.review_type,
            is_anonymous=review.is_anonymous,
            review_weight=float(review.review_weight) if review.review_weight else 1.0,
            aggregate_rating=float(review.aggregate_rating) if review.aggregate_rating else 0.0,
            weighted_rating=float(review.weighted_rating) if review.weighted_rating else 0.0,
            total_questions_rated=review.total_questions_rated,
            created_at=review.created_at
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )

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

@router.get("/test/locations")
async def test_locations(db: Session = Depends(get_db)):
    """Test endpoint to check locations table"""
    try:
        from sqlalchemy import text
        
        # Get sample locations
        query = text("""
            SELECT "UUID", "Location", "City", "Country", "Region"
            FROM locations 
            LIMIT 10
        """)
        
        result = db.execute(query)
        locations = result.fetchall()
        
        # Get total count
        count_query = text("SELECT COUNT(*) FROM locations")
        count_result = db.execute(count_query)
        total_count = count_result.scalar()
        
        return {
            "total_locations": total_count,
            "sample_locations": [
                {
                    "uuid": str(loc[0]),
                    "location": str(loc[1]) if loc[1] else "",
                    "city": str(loc[2]) if loc[2] else "",
                    "country": str(loc[3]) if loc[3] else "",
                    "region": str(loc[4]) if loc[4] else ""
                }
                for loc in locations
            ]
        }
    except Exception as e:
        logger.error(f"Error in test_locations: {e}")
        return {"error": str(e)}

@router.post("/test/create-minimal")
async def test_create_minimal_review(db: Session = Depends(get_db)):
    """Test endpoint to create a minimal review and identify database issues"""
    try:
        from sqlalchemy import text
        
        # First, let's check what freight forwarders exist
        ff_query = text("SELECT id FROM freight_forwarders LIMIT 1")
        ff_result = db.execute(ff_query)
        ff_data = ff_result.fetchone()
        
        if not ff_data:
            return {"error": "No freight forwarders found in database"}
        
        freight_forwarder_id = ff_data[0]
        
        # Try to create a minimal review
        review_query = text("""
            INSERT INTO reviews (
                freight_forwarder_id, 
                review_type, 
                is_anonymous, 
                review_weight, 
                aggregate_rating, 
                weighted_rating, 
                total_questions_rated,
                is_active,
                is_verified
            ) VALUES (
                :ff_id, 'test', true, 1.0, 4.0, 4.0, 1, true, false
            ) RETURNING id
        """)
        
        result = db.execute(review_query, {"ff_id": freight_forwarder_id})
        review_id = result.scalar()
        
        # Clean up the test review
        cleanup_query = text("DELETE FROM reviews WHERE id = :review_id")
        db.execute(cleanup_query, {"review_id": review_id})
        db.commit()
        
        return {
            "success": True,
            "message": "Minimal review created and cleaned up successfully",
            "test_review_id": str(review_id),
            "freight_forwarder_id": str(freight_forwarder_id)
        }
        
    except Exception as e:
        logger.error(f"Error in test_create_minimal_review: {e}")
        db.rollback()
        return {"error": str(e), "type": type(e).__name__}

@router.get("/ping")
async def ping():
    """Simple ping endpoint to test if reviews router is working"""
    return {"message": "Reviews router is working", "status": "ok"}

@router.get("/debug/schema")
async def debug_schema(db: Session = Depends(get_db)):
    """Debug endpoint to check database schema for reviews table"""
    try:
        from sqlalchemy import text
        
        # Check reviews table structure
        schema_query = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'reviews'
            ORDER BY ordinal_position
        """)
        
        result = db.execute(schema_query)
        columns = result.fetchall()
        
        # Check constraints
        constraint_query = text("""
            SELECT constraint_name, constraint_type, column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'reviews'
        """)
        
        constraint_result = db.execute(constraint_query)
        constraints = constraint_result.fetchall()
        
        return {
            "table": "reviews",
            "columns": [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2],
                    "default": col[3]
                }
                for col in columns
            ],
            "constraints": [
                {
                    "name": const[0],
                    "type": const[1],
                    "column": const[2]
                }
                for const in constraints
            ]
        }
    except Exception as e:
        logger.error(f"Error in debug_schema: {e}")
        return {"error": str(e)} 