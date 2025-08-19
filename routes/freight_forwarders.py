from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from database.database import get_db
from database.models import FreightForwarder, Branch, Review, ReviewCategoryScore
from auth.auth import get_current_user
from database.models import User

router = APIRouter()

from datetime import datetime
from uuid import UUID

class FreightForwarderCreate(BaseModel):
    name: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    headquarters_country: Optional[str] = None

class FreightForwarderResponse(BaseModel):
    id: UUID
    name: str
    website: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]  # Keep this field
    headquarters_country: Optional[str]  # Keep this field
    average_rating: Optional[float] = 0.0  # Average rating per review
    review_count: Optional[int] = 0  # Total number of review submissions (raw count)
    weighted_review_count: Optional[float] = 0.0  # PRIMARY: Weighted count for frontend (anonymous=0.5, authenticated=1.0)
    total_aggregated_score: Optional[float] = 0.0  # Sum of all review ratings
    category_scores_summary: Optional[dict] = {}  # Aggregated category scores
    created_at: datetime

    class Config:
        from_attributes = True

class BranchResponse(BaseModel):
    id: str
    name: str
    city: Optional[str]
    country: Optional[str]
    address: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[FreightForwarderResponse])
async def get_freight_forwarders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    random_select: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """Get list of freight forwarders with optional search and random selection"""
    try:
        query = db.query(FreightForwarder)
        
        if search:
            query = query.filter(FreightForwarder.name.ilike(f"%{search}%"))
        
        # Handle random selection
        if random_select:
            from sqlalchemy import func
            query = query.order_by(func.random())
        
        freight_forwarders = query.offset(skip).limit(limit).all()
        
        # Convert to response model with safe attribute access
        result = []
        for ff in freight_forwarders:
            try:
                # Calculate company rating from reviews.aggregate_rating
                try:
                    avg_rating = ff.average_rating if hasattr(ff, 'average_rating') else 0.0
                except Exception:
                    avg_rating = 0.0
                
                # Count total reviews for each company
                try:
                    review_count = ff.review_count if hasattr(ff, 'review_count') else 0
                except Exception:
                    review_count = 0
                
                # Aggregate category scores from review_category_scores
                try:
                    category_scores = ff.category_scores_summary if hasattr(ff, 'category_scores_summary') else {}
                except Exception:
                    category_scores = {}
                
                # Create response manually to avoid SQL generation issues
                response = FreightForwarderResponse(
                    id=ff.id,
                    name=ff.name,
                    website=ff.website,
                    logo_url=ff.logo_url,
                    description=ff.description,
                    headquarters_country=ff.headquarters_country,
                    average_rating=avg_rating,
                    review_count=review_count,
                    category_scores_summary=category_scores,
                    created_at=ff.created_at
                )
                result.append(response)
            except Exception as e:
                # Log the error but continue with other records
                print(f"Error converting freight forwarder {ff.id}: {e}")
                continue
        
        return result
        
    except Exception as e:
        print(f"Error in get_freight_forwarders: {e}")
        # Return empty list instead of crashing
        return []

@router.get("/aggregated/", response_model=List[FreightForwarderResponse])
async def get_freight_forwarders_aggregated(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get freight forwarders with efficiently calculated aggregated data using SQL"""
    try:
        from sqlalchemy import func, case, text
        
        # Build the base query with aggregations
        query = db.query(
            FreightForwarder.id,
            FreightForwarder.name,
            FreightForwarder.website,
            FreightForwarder.logo_url,
            FreightForwarder.description,
            FreightForwarder.headquarters_country,
            FreightForwarder.created_at,
            # Calculate average rating from reviews.aggregate_rating
            func.avg(Review.aggregate_rating).label('calculated_average_rating'),
            # Count total reviews (raw count)
            func.count(Review.id).label('calculated_review_count'),
            # Calculate total aggregated score (sum of all ratings)
            func.sum(Review.aggregate_rating).label('calculated_total_score'),
            # PRIMARY: Calculate weighted review count for frontend (anonymous=0.5, authenticated=1.0)
            func.sum(Review.review_weight).label('calculated_weighted_count')
        ).outerjoin(Review, FreightForwarder.id == Review.freight_forwarder_id)
        
        if search:
            query = query.filter(FreightForwarder.name.ilike(f"%{search}%"))
        
        # Group by freight forwarder and apply pagination
        query = query.group_by(
            FreightForwarder.id,
            FreightForwarder.name,
            FreightForwarder.website,
            FreightForwarder.logo_url,
            FreightForwarder.description,
            FreightForwarder.headquarters_country,
            FreightForwarder.created_at
        ).offset(skip).limit(limit)
        
        results = query.all()
        
        # Convert to response model
        freight_forwarders = []
        for result in results:
            # Get category scores summary for this freight forwarder
            category_scores = {}
            try:
                # Query category scores for this specific freight forwarder
                category_query = db.query(
                    ReviewCategoryScore.category_id,
                    ReviewCategoryScore.category_name,
                    func.avg(ReviewCategoryScore.rating * ReviewCategoryScore.weight).label('avg_weighted_rating'),
                    func.count(ReviewCategoryScore.id).label('total_questions')
                ).join(Review, ReviewCategoryScore.review_id == Review.id).filter(
                    Review.freight_forwarder_id == result.id
                ).group_by(
                    ReviewCategoryScore.category_id,
                    ReviewCategoryScore.category_name
                )
                
                category_results = category_query.all()
                for cat_result in category_results:
                    category_scores[cat_result.category_id] = {
                        "average_rating": float(cat_result.avg_weighted_rating or 0),
                        "total_reviews": int(cat_result.total_questions or 0),
                        "category_name": cat_result.category_name
                    }
            except Exception as e:
                print(f"Error calculating category scores for freight forwarder {result.id}: {e}")
                category_scores = {}
            
            response = FreightForwarderResponse(
                id=result.id,
                name=result.name,
                website=result.website,
                logo_url=result.logo_url,
                description=result.description,
                headquarters_country=result.headquarters_country,
                average_rating=float(result.calculated_average_rating or 0),
                review_count=int(result.calculated_review_count or 0),
                total_aggregated_score=float(result.calculated_total_score or 0),
                weighted_review_count=float(result.calculated_weighted_count or result.calculated_review_count or 0),  # Fallback to review_count if weighted is 0
                category_scores_summary=category_scores,
                created_at=result.created_at
            )
            freight_forwarders.append(response)
        
        return freight_forwarders
        
    except Exception as e:
        print(f"Error in get_freight_forwarders_aggregated: {e}")
        return []

@router.get("/{freight_forwarder_id}", response_model=FreightForwarderResponse)
async def get_freight_forwarder(
    freight_forwarder_id: str,
    db: Session = Depends(get_db)
):
    """Get specific freight forwarder by ID"""
    freight_forwarder = db.query(FreightForwarder).filter(
        FreightForwarder.id == freight_forwarder_id
    ).first()
    
    if not freight_forwarder:
        raise HTTPException(status_code=404, detail="Freight forwarder not found")
    
    # Calculate company rating from reviews.aggregate_rating
    try:
        avg_rating = freight_forwarder.average_rating if hasattr(freight_forwarder, 'average_rating') else 0.0
    except Exception:
        avg_rating = 0.0
    
    # Count total reviews for each company
    try:
        review_count = freight_forwarder.review_count if hasattr(freight_forwarder, 'review_count') else 0
    except Exception:
        review_count = 0
    
    # Calculate total aggregated score
    try:
        total_score = freight_forwarder.total_aggregated_score if hasattr(freight_forwarder, 'total_aggregated_score') else 0.0
    except Exception:
        total_score = 0.0
    
    # Calculate weighted review count
    try:
        weighted_count = freight_forwarder.weighted_review_count if hasattr(freight_forwarder, 'weighted_review_count') else 0.0
        # Fallback: if weighted_count is 0 or None, use review_count instead
        if not weighted_count or weighted_count == 0:
            weighted_count = review_count
    except Exception:
        weighted_count = review_count  # Fallback to review_count
    
    # Aggregate category scores from review_category_scores
    try:
        category_scores = freight_forwarder.category_scores_summary if hasattr(freight_forwarder, 'category_scores_summary') else {}
    except Exception:
        category_scores = {}
    
    # Create response manually to avoid SQL generation issues
    return FreightForwarderResponse(
        id=freight_forwarder.id,
        name=freight_forwarder.name,
        website=freight_forwarder.website,
        logo_url=freight_forwarder.logo_url,
        description=freight_forwarder.description,
        headquarters_country=freight_forwarder.headquarters_country,
        average_rating=avg_rating,
        review_count=review_count,
        total_aggregated_score=total_score,
        weighted_review_count=weighted_count,
        category_scores_summary=category_scores,
        created_at=freight_forwarder.created_at
    )

@router.get("/{freight_forwarder_id}/branches", response_model=List[BranchResponse])
async def get_freight_forwarder_branches(
    freight_forwarder_id: str,
    db: Session = Depends(get_db)
):
    """Get branches for a specific freight forwarder"""
    branches = db.query(Branch).filter(
        Branch.freight_forwarder_id == freight_forwarder_id,
        Branch.is_active == True
    ).all()
    
    return [BranchResponse.from_orm(branch) for branch in branches]

@router.post("/", response_model=FreightForwarderResponse, status_code=status.HTTP_201_CREATED)
async def create_freight_forwarder(
    freight_forwarder_data: FreightForwarderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new freight forwarder"""
    try:
        # Check if user has permission to create freight forwarders
        if current_user.user_type not in ["admin", "shipper"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create freight forwarders"
            )
        
        # Check if freight forwarder with same name already exists
        existing_ff = db.query(FreightForwarder).filter(
            FreightForwarder.name.ilike(freight_forwarder_data.name)
        ).first()
        
        if existing_ff:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Freight forwarder with name '{freight_forwarder_data.name}' already exists"
            )
        
        # Create new freight forwarder
        new_freight_forwarder = FreightForwarder(
            name=freight_forwarder_data.name,
            website=freight_forwarder_data.website,
            logo_url=freight_forwarder_data.logo_url,
            description=freight_forwarder_data.description,
            headquarters_country=freight_forwarder_data.headquarters_country
        )
        
        db.add(new_freight_forwarder)
        db.commit()
        db.refresh(new_freight_forwarder)
        
        # Return the created freight forwarder
        return FreightForwarderResponse(
            id=new_freight_forwarder.id,
            name=new_freight_forwarder.name,
            website=new_freight_forwarder.website,
            logo_url=new_freight_forwarder.logo_url,
            description=new_freight_forwarder.description,
            headquarters_country=new_freight_forwarder.headquarters_country,
            average_rating=0.0,
            review_count=0,
            category_scores_summary={},
            created_at=new_freight_forwarder.created_at
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create freight forwarder: {str(e)}"
        ) 