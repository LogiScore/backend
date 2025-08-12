from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.database import get_db
from database.models import FreightForwarder, Branch

router = APIRouter()

from datetime import datetime
from uuid import UUID

class FreightForwarderResponse(BaseModel):
    id: UUID
    name: str
    website: Optional[str]
    logo_url: Optional[str]
    average_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class BranchResponse(BaseModel):
    id: str
    name: str
    location: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
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
                # Safely get average_rating and review_count
                try:
                    avg_rating = ff.average_rating if hasattr(ff, 'average_rating') else 0.0
                except Exception:
                    avg_rating = 0.0
                
                try:
                    review_count = ff.review_count if hasattr(ff, 'review_count') else 0
                except Exception:
                    review_count = 0
                
                # Create response manually to avoid SQL generation issues
                response = FreightForwarderResponse(
                    id=ff.id,
                    name=ff.name,
                    website=ff.website,
                    logo_url=ff.logo_url,
                    average_rating=avg_rating,
                    review_count=review_count,
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
    
    # Safely get average_rating and review_count
    try:
        avg_rating = freight_forwarder.average_rating if hasattr(freight_forwarder, 'average_rating') else 0.0
    except Exception:
        avg_rating = 0.0
    
    try:
        review_count = freight_forwarder.review_count if hasattr(freight_forwarder, 'review_count') else 0
    except Exception:
        review_count = 0
    
    # Create response manually to avoid SQL generation issues
    return FreightForwarderResponse(
        id=freight_forwarder.id,
        name=freight_forwarder.name,
        website=freight_forwarder.website,
        logo_url=freight_forwarder.logo_url,
        average_rating=avg_rating,
        review_count=review_count,
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