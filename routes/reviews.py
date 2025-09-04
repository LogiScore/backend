from fastapi import APIRouter, Depends, HTTPException, status, Query
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
from pydantic import BaseModel, field_validator

class QuestionRating(BaseModel):
    question: str
    rating: int
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v < 0 or v > 5:
            raise ValueError(f"Question rating must be between 0 and 5, got {v}")
        return v

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
    shipment_reference: Optional[str] = None  # Added: shipment reference for tracking

class ReviewResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]  # Added user_id field for frontend filtering
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
    shipment_reference: Optional[str] = None  # Added: shipment reference for tracking
    created_at: datetime

    class Config:
        from_attributes = True
        
    @field_validator('shipment_reference', mode='before')
    @classmethod
    def validate_shipment_reference(cls, v):
        """Ensure shipment_reference is always a string or None"""
        if v is None or v == '':
            return None
        return str(v)

class ReviewsListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters: dict

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
        if review_data.aggregate_rating < 0 or review_data.aggregate_rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aggregate rating must be between 0 and 5"
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
                if question.rating < 0 or question.rating > 5:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Question rating must be between 0 and 5, got {question.rating}"
                    )
        
        # Create the main review record
        try:
            logger.info(f"Creating review with data: freight_forwarder_id={review_data.freight_forwarder_id}, city={city}, country={country}")
            logger.info(f"Current user: {current_user}")
            logger.info(f"User ID: {current_user.get('id') if current_user else None}")
            
            # Since we're using locations instead of branches, we need to work around database constraints
            # Create a dummy UUID for branch_id to satisfy any NOT NULL constraints
            # The real location data will be stored in city/country fields
            import uuid
            dummy_branch_id = uuid.uuid4()  # Generate a random UUID for branch_id
            logger.info(f"Using city={city}, country={country} from location, dummy branch_id={dummy_branch_id}")
            
            total_questions = sum(len(cat.questions) for cat in review_data.category_ratings)
            logger.info(f"Total questions to rate: {total_questions}")
            
            review = Review(
                freight_forwarder_id=review_data.freight_forwarder_id,
                branch_id=dummy_branch_id,  # Use dummy UUID to satisfy database constraints
                city=city,
                country=country,
                user_id=current_user.get("id") if current_user else None,
                review_type=review_data.review_type,
                is_anonymous=review_data.is_anonymous,
                review_weight=review_data.review_weight,
                aggregate_rating=review_data.aggregate_rating,
                weighted_rating=review_data.weighted_rating,
                total_questions_rated=total_questions,
                shipment_reference=review_data.shipment_reference,  # Added: shipment reference
                is_active=True,
                is_verified=False
            )
            
            logger.info(f"Review object created successfully: {review}")
            logger.info(f"Review attributes: id={review.id}, user_id={review.user_id}, freight_forwarder_id={review.freight_forwarder_id}")
            logger.info(f"shipment_reference: {review_data.shipment_reference}")
            logger.info(f"Review shipment_reference field: {getattr(review, 'shipment_reference', 'FIELD_NOT_FOUND')}")
            
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
            logger.info(f"Starting to create category scores for {len(review_data.category_ratings)} categories")
            
            for category in review_data.category_ratings:
                logger.info(f"Processing category: {category.category} with {len(category.questions)} questions")
                
                for question in category.questions:
                    logger.info(f"Processing question: {question.question} with rating: {question.rating}")
                    
                    # Get question details from review_questions table
                    question_detail = db.query(ReviewQuestion).filter(
                        ReviewQuestion.question_id == question.question
                    ).first()
                    
                    logger.info(f"Question detail found: {question_detail is not None}")
                    
                    if question_detail:
                        logger.info(f"Question detail: category_name={question_detail.category_name}, question_text={question_detail.question_text}")
                        logger.info(f"Rating definitions type: {type(question_detail.rating_definitions)}")
                        logger.info(f"Rating definitions: {question_detail.rating_definitions}")
                        
                        try:
                            rating_def = question_detail.rating_definitions.get(str(question.rating), "") if question_detail.rating_definitions else ""
                            logger.info(f"Extracted rating definition: {rating_def}")
                        except Exception as e:
                            logger.error(f"Error extracting rating definition: {e}")
                            rating_def = ""
                        
                        category_score = ReviewCategoryScore(
                            review_id=review.id,
                            category_id=category.category,
                            category_name=question_detail.category_name,
                            question_id=question.question,
                            question_text=question_detail.question_text,
                            rating=question.rating,
                            rating_definition=rating_def,
                            weight=review_data.review_weight,
                            category=category.category,  # Set the category field
                            score=0.0  # Set a default score
                        )
                        db.add(category_score)
                        logger.info(f"Category score object created for question {question.question}")
                    else:
                        logger.warning(f"Question detail not found for question_id: {question.question}")
                        # If question not found, create with basic info
                        category_score = ReviewCategoryScore(
                            review_id=review.id,
                            category_id=category.category,
                            category_name=category.category,
                            question_id=question.question,
                            question_text=f"Question {question.question}",
                            rating=question.rating,
                            rating_definition="",
                            weight=review_data.review_weight,
                            category=category.category,  # Set the category field
                            score=0.0  # Set a default score
                        )
                        db.add(category_score)
                        logger.info(f"Fallback category score object created for question {question.question}")
            
            logger.info(f"Category scores created successfully for review {review.id} with category and score fields set")
            
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
            
            # Trigger notification system for new review
            try:
                await trigger_review_notifications(review, freight_forwarder, db)
            except Exception as e:
                # Don't fail the review creation if notifications fail
                logger.error(f"Failed to trigger notifications for review {review.id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error committing review: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database commit error: {str(e)}"
            )
        
        # Return the created review
        try:
            # Convert location_id to UUID if it's a string
            location_uuid = review_data.location_id
            if isinstance(location_uuid, str):
                try:
                    location_uuid = UUID(location_uuid)
                except ValueError:
                    # If conversion fails, use the review's branch_id as fallback
                    location_uuid = review.branch_id
            
            response = ReviewResponse(
                id=review.id,
                user_id=review.user_id,
                freight_forwarder_id=review.freight_forwarder_id,
                location_id=location_uuid,
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
            
            logger.info(f"ReviewResponse created successfully: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating ReviewResponse: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating response: {str(e)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_review: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
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

@router.post("/test/create-simple")
async def test_create_simple_review(db: Session = Depends(get_db)):
    """Test endpoint to create a simple review and see exact database errors"""
    try:
        from sqlalchemy import text
        
        # First, let's check what freight forwarders exist
        ff_query = text("SELECT id FROM freight_forwarders LIMIT 1")
        ff_result = db.execute(ff_query)
        ff_data = ff_result.fetchone()
        
        if not ff_data:
            return {"error": "No freight forwarders found in database"}
        
        freight_forwarder_id = ff_data[0]
        
        # Try to create a minimal review with NULL branch_id
        review_query = text("""
            INSERT INTO reviews (
                freight_forwarder_id, 
                branch_id,
                city,
                country,
                review_type, 
                is_anonymous, 
                review_weight, 
                aggregate_rating, 
                weighted_rating, 
                total_questions_rated,
                is_active,
                is_verified
            ) VALUES (
                :ff_id, NULL, 'Test City', 'Test Country', 'test', true, 1.0, 4.0, 4.0, 1, true, false
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
            "message": "Simple review with NULL branch_id created successfully",
            "test_review_id": str(review_id),
            "freight_forwarder_id": str(freight_forwarder_id)
        }
        
    except Exception as e:
        logger.error(f"Error in test_create_simple_review: {e}")
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

@router.get("/", response_model=ReviewsListResponse)
async def get_reviews(
    country: Optional[str] = Query(None, description="Filter reviews by country"),
    city: Optional[str] = Query(None, description="Filter reviews by city"),
    freight_forwarder_id: Optional[UUID] = Query(None, description="Filter reviews by freight forwarder ID"),
    search: Optional[str] = Query(None, description="Search in review content"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Number of reviews per page"),
    db: Session = Depends(get_db)
):
    """
    Get reviews with filtering and pagination support.
    
    Supports filtering by:
    - country: Filter reviews by country
    - city: Filter reviews by city (optionally with country)
    - freight_forwarder_id: Filter reviews by specific freight forwarder
    - search: Search in review content
    
    Supports pagination with page and page_size parameters.
    """
    try:
        # Build the base query
        query = db.query(Review)  # Temporarily removed is_active filter to fix critical API issue
        
        # DEBUG: Log the initial query
        logger.info(f"Initial query built for reviews endpoint")
        
        # Apply filters
        filters = {}
        
        if country:
            # Case-insensitive country filter
            query = query.filter(Review.country.ilike(f"%{country}%"))
            filters["country"] = country
        
        if city:
            # Case-insensitive city filter
            query = query.filter(Review.city.ilike(f"%{city}%"))
            filters["city"] = city
        
        if freight_forwarder_id:
            query = query.filter(Review.freight_forwarder_id == freight_forwarder_id)
            filters["freight_forwarder_id"] = str(freight_forwarder_id)
            logger.info(f"Applied freight_forwarder_id filter: {freight_forwarder_id}")
        
        if search:
            # Search in review content through category scores
            logger.info(f"Search parameter detected: '{search}' - applying complex join query")
            from sqlalchemy import or_
            query = query.join(ReviewCategoryScore).filter(
                or_(
                    ReviewCategoryScore.question_text.ilike(f"%{search}%"),
                    ReviewCategoryScore.category_name.ilike(f"%{search}%"),
                    ReviewCategoryScore.rating_definition.ilike(f"%{search}%")
                )
            ).distinct()
            filters["search"] = search
        else:
            logger.info("No search parameter - using simple query")
        
        # Get total count before pagination
        total_count = query.count()
        logger.info(f"Total reviews found before pagination: {total_count}")
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(Review.created_at.desc()).offset(offset).limit(page_size)
        
        # Execute query
        reviews = query.all()
        logger.info(f"Reviews returned after pagination: {len(reviews)}")
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Convert to response models
        review_responses = []
        for review in reviews:
            # Create a dummy location_id for response (using branch_id as fallback)
            location_id = review.branch_id if review.branch_id else uuid.uuid4()
            
            review_response = ReviewResponse(
                id=review.id,
                user_id=review.user_id,  # Added user_id field for frontend filtering
                freight_forwarder_id=review.freight_forwarder_id,
                location_id=location_id,
                city=review.city,
                country=review.country,
                review_type=review.review_type,
                is_anonymous=review.is_anonymous,
                review_weight=float(review.review_weight) if review.review_weight else 1.0,
                aggregate_rating=float(review.aggregate_rating) if review.aggregate_rating else 0.0,
                weighted_rating=float(review.weighted_rating) if review.weighted_rating else 0.0,
                total_questions_rated=review.total_questions_rated,
                created_at=review.created_at
            )
            review_responses.append(review_response)
        
        return ReviewsListResponse(
            reviews=review_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            filters=filters
        )
        
    except Exception as e:
        logger.error(f"Error in get_reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reviews: {str(e)}"
        )

@router.get("/countries", response_model=List[str])
async def get_available_countries(db: Session = Depends(get_db)):
    """
    Get list of all available countries that have reviews.
    Useful for frontend filtering dropdowns.
    """
    try:
        # Get distinct countries from reviews table
        countries = db.query(Review.country).filter(
            Review.country.isnot(None),
            Review.country != ""
            # Temporarily removed is_active filter to fix critical API issue
        ).distinct().all()
        
        # Extract country names and filter out None/empty values
        country_list = [country[0] for country in countries if country[0] and country[0].strip()]
        
        # Sort alphabetically
        country_list.sort()
        
        return country_list
        
    except Exception as e:
        logger.error(f"Error in get_available_countries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve countries: {str(e)}"
        )

@router.get("/cities", response_model=List[dict])
async def get_available_cities(
    country: Optional[str] = Query(None, description="Filter cities by country"),
    db: Session = Depends(get_db)
):
    """
    Get list of all available cities that have reviews.
    Optionally filter by country.
    Useful for frontend filtering dropdowns.
    """
    try:
        # Build the base query
        query = db.query(Review.city, Review.country).filter(
            Review.city.isnot(None),
            Review.city != ""
            # Temporarily removed is_active filter to fix critical API issue
        )
        
        # Apply country filter if provided
        if country:
            query = query.filter(Review.country.ilike(f"%{country}%"))
        
        # Get distinct cities
        cities = query.distinct().all()
        
        # Extract city data and filter out None/empty values
        city_list = []
        for city_data in cities:
            if city_data[0] and city_data[0].strip():
                city_list.append({
                    "city": city_data[0],
                    "country": city_data[1] if city_data[1] else "Unknown"
                })
        
        # Sort by city name
        city_list.sort(key=lambda x: x["city"])
        
        return city_list
        
    except Exception as e:
        logger.error(f"Error in get_available_cities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cities: {str(e)}"
        )

@router.get("/statistics/location", response_model=dict)
async def get_review_statistics_by_location(
    country: Optional[str] = Query(None, description="Filter statistics by country"),
    city: Optional[str] = Query(None, description="Filter statistics by city"),
    db: Session = Depends(get_db)
):
    """
    Get review statistics filtered by location.
    Provides counts, average ratings, and other metrics.
    """
    try:
        # Build the base query
        query = db.query(Review)  # Temporarily removed is_active filter to fix critical API issue
        
        # Apply location filters
        if country:
            query = query.filter(Review.country.ilike(f"%{country}%"))
        
        if city:
            query = query.filter(Review.city.ilike(f"%{city}%"))
        
        # Get all reviews for the location
        reviews = query.all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "total_weighted_rating": 0.0,
                "review_types": {},
                "anonymous_count": 0,
                "authenticated_count": 0,
                "location": {
                    "country": country,
                    "city": city
                }
            }
        
        # Calculate statistics
        total_reviews = len(reviews)
        total_rating = sum(review.aggregate_rating or 0 for review in reviews if review.aggregate_rating is not None)
        valid_ratings = sum(1 for review in reviews if review.aggregate_rating is not None)
        average_rating = total_rating / valid_ratings if valid_ratings > 0 else 0.0
        
        total_weighted_rating = sum(review.weighted_rating or 0 for review in reviews if review.weighted_rating is not None)
        
        # Count review types
        review_types = {}
        for review in reviews:
            review_type = review.review_type or "general"
            review_types[review_type] = review_types.get(review_type, 0) + 1
        
        # Count anonymous vs authenticated
        anonymous_count = sum(1 for review in reviews if review.is_anonymous)
        authenticated_count = total_reviews - anonymous_count
        
        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "total_weighted_rating": round(total_weighted_rating, 2),
            "review_types": review_types,
            "anonymous_count": anonymous_count,
            "authenticated_count": authenticated_count,
            "location": {
                "country": country,
                "city": city
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_review_statistics_by_location: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve review statistics: {str(e)}"
        ) 

@router.get("/check-duplicate/{user_id}/{company_id}/{location_id}")
async def check_duplicate_review(
    user_id: UUID,
    company_id: UUID,
    location_id: Union[UUID, str],
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Check if user has already reviewed the same company and location in the last 6 months.
    This prevents duplicate reviews for the same service experience.
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate 6 months ago
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        # Query for existing review with same user, company, and location within 6 months
        # Since location_id is not stored in reviews table, we need to extract city/country from the location_id parameter
        # For now, we'll check by user, company, and time period only
        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.freight_forwarder_id == company_id,
            Review.created_at >= six_months_ago
            # Temporarily removed is_active filter to fix critical API issue
        ).first()
        
        if existing_review:
            return {
                "has_duplicate": True,
                "existing_review_id": str(existing_review.id),
                "created_at": existing_review.created_at.isoformat(),
                "message": "You have already reviewed this company for this location within the last 6 months"
            }
        else:
            return {
                "has_duplicate": False,
                "message": "No duplicate review found, you can proceed"
            }
        
    except Exception as e:
        logger.error(f"Error in check_duplicate_review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check for duplicate review: {str(e)}"
        )

@router.get("/user/{user_id}/company/{company_id}", response_model=List[ReviewResponse])
async def get_user_reviews_for_company(
    user_id: UUID,
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get all reviews submitted by a specific user for a specific company.
    This endpoint allows users to see their own reviews for a company.
    """
    try:
        # Query reviews by user_id and freight_forwarder_id (company_id)
        reviews = db.query(Review).filter(
            Review.user_id == user_id,
            Review.freight_forwarder_id == company_id
            # Temporarily removed is_active filter to fix critical API issue
        ).all()
        
        if not reviews:
            return []
        
        # Convert to response model
        review_responses = []
        for review in reviews:
            try:
                # Get city and country from the review
                city = getattr(review, 'city', None)
                country = getattr(review, 'country', None)
                
                # Count total questions rated for this review
                total_questions = db.query(ReviewCategoryScore).filter(
                    ReviewCategoryScore.review_id == review.id
                ).count()
                
                review_response = ReviewResponse(
                    id=review.id,
                    user_id=review.user_id,  # Added user_id field for frontend filtering
                    freight_forwarder_id=review.freight_forwarder_id,
                    location_id=review.branch_id if review.branch_id else uuid.uuid4(),
                    city=city,
                    country=country,
                    review_type=review.review_type,
                    is_anonymous=review.is_anonymous,
                    review_weight=review.review_weight,
                    aggregate_rating=review.aggregate_rating,
                    weighted_rating=review.weighted_rating,
                    total_questions_rated=total_questions,
                    created_at=review.created_at
                )
                review_responses.append(review_response)
                
            except Exception as e:
                logger.error(f"Error processing review {review.id}: {e}")
                continue
        
        return review_responses
        
    except Exception as e:
        logger.error(f"Error in get_user_reviews_for_company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user reviews for company: {str(e)}"
        )

async def trigger_review_notifications(review: Review, freight_forwarder: FreightForwarder, db: Session):
    """
    Trigger email notifications for a new review submission.
    This function calls the notification service directly instead of making HTTP requests.
    """
    try:
        from routes.notifications import trigger_review_notification
        from routes.notifications import ReviewNotificationTrigger
        from datetime import datetime
        
        # Get category scores for the review (same approach as thank you email)
        from database.models import ReviewCategoryScore
        category_scores_db = db.query(ReviewCategoryScore).filter(
            ReviewCategoryScore.review_id == review.id
        ).all()
        
        # Format category scores for notification (include question text for better email formatting)
        category_scores = []
        for score in category_scores_db:
            category_scores.append({
                'category_name': score.category_name,
                'question_text': score.question_text,
                'rating': score.rating,
                'rating_definition': score.rating_definition
            })
            logger.info(f"Category: {score.category_name}, Question: {score.question_text}, Rating: {score.rating}")
        
        logger.info(f"Found {len(category_scores)} category scores for review {review.id}")
        
        # Prepare notification data
        notification_data = ReviewNotificationTrigger(
            review_id=str(review.id),
            freight_forwarder_id=str(review.freight_forwarder_id),
            freight_forwarder_name=freight_forwarder.name,
            country=review.country or "",
            city=review.city or "",
            reviewer_name="Anonymous User" if review.is_anonymous else (review.user.full_name if review.user else "Anonymous User"),
            rating=float(review.aggregate_rating or 0),
            review_text="Review submitted",  # We don't store full review text in the main review table
            created_at=review.created_at
        )
        
        # Add category scores to the notification data
        notification_data.category_scores = category_scores
        
        # Call the notification function directly
        result = await trigger_review_notification(notification_data, db)
        logger.info(f"Notifications triggered successfully for review {review.id}: {result.notifications_sent} emails sent")
                
    except Exception as e:
        logger.error(f"Error triggering notifications for review {review.id}: {str(e)}")
        # Don't raise the exception - we don't want notification failures to break review creation 