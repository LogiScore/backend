from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from database.database import get_db
from database.models import User, FreightForwarder, Review, ReviewCategoryScore
from auth.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory cache for score trends
# In production, this should be replaced with Redis or similar
_cache = {}
_cache_ttl = 3600  # 1 hour in seconds

def get_cache_key(freight_forwarder_id: str, period: str) -> str:
    """Generate cache key for score trends"""
    return f"score_trends_{freight_forwarder_id}_{period}"

def is_cache_valid(cache_entry: dict) -> bool:
    """Check if cache entry is still valid"""
    if not cache_entry:
        return False
    cache_time = cache_entry.get('timestamp', 0)
    return (datetime.now().timestamp() - cache_time) < _cache_ttl

def get_cached_data(cache_key: str) -> Optional[dict]:
    """Get data from cache if valid"""
    cache_entry = _cache.get(cache_key)
    if cache_entry and is_cache_valid(cache_entry):
        return cache_entry.get('data')
    return None

def set_cached_data(cache_key: str, data: dict) -> None:
    """Store data in cache with timestamp"""
    _cache[cache_key] = {
        'data': data,
        'timestamp': datetime.now().timestamp()
    }

def validate_annual_subscription(user: User) -> bool:
    """Check if user has active annual subscription"""
    if not user.subscription_tier:
        return False
    
    # Check if subscription is annual (contains 'annual' in tier name)
    is_annual = 'annual' in user.subscription_tier.lower()
    
    # Check if subscription is active
    is_active = user.subscription_status in ['active', 'trial']
    
    # Check if subscription hasn't expired
    is_not_expired = (
        user.subscription_end_date is None or 
        user.subscription_end_date > datetime.now()
    )
    
    return is_annual and is_active and is_not_expired

def calculate_period_dates(period: str) -> tuple:
    """Calculate start and end dates based on period"""
    now = datetime.now()
    
    if period == "6m":
        start_date = now - timedelta(days=180)  # 6 months
        return start_date, now, "month"
    elif period == "12m":
        start_date = now - timedelta(days=365)  # 12 months
        return start_date, now, "month"
    elif period == "24m":
        start_date = now - timedelta(days=730)  # 24 months
        return start_date, now, "quarter"
    else:
        # Default to 12 months
        start_date = now - timedelta(days=365)
        return start_date, now, "month"

def format_period_labels(period: str, start_date: datetime, end_date: datetime) -> List[str]:
    """Generate period labels for the response"""
    labels = []
    
    if period == "6m" or period == "12m":
        # Monthly labels
        current = start_date.replace(day=1)
        while current <= end_date:
            labels.append(current.strftime("%Y-%m"))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    else:  # 24m
        # Quarterly labels
        current = start_date.replace(day=1)
        while current <= end_date:
            quarter = ((current.month - 1) // 3) + 1
            labels.append(f"{current.year}-Q{quarter}")
            current = current.replace(month=current.month + 3)
    
    return labels

@router.get("/score-trends/{freight_forwarder_id}")
async def get_score_trends(
    freight_forwarder_id: str,
    period: str = Query("12m", regex="^(6m|12m|24m)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get score trends for a freight forwarder over a specified period.
    Requires annual subscription.
    """
    try:
        # Check if user has annual subscription
        if not validate_annual_subscription(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Annual subscription required to access score trends analytics"
            )
        
        # Check cache first
        cache_key = get_cache_key(freight_forwarder_id, period)
        cached_data = get_cached_data(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for freight_forwarder_id: {freight_forwarder_id}")
            return cached_data
        
        # Verify freight forwarder exists
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == freight_forwarder_id
        ).first()
        
        if not freight_forwarder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freight forwarder not found"
            )
        
        # Calculate period dates
        start_date, end_date, date_trunc = calculate_period_dates(period)
        
        # Build the SQL query for score trends
        query = text("""
            SELECT 
                rcs.category_name,
                DATE_TRUNC(:date_trunc, rcs.created_at) as period,
                AVG(rcs.rating * rcs.weight * COALESCE(r.review_weight, 1.0)) / AVG(rcs.weight * COALESCE(r.review_weight, 1.0)) as avg_score,
                COUNT(*) as review_count
            FROM review_category_scores rcs
            JOIN reviews r ON rcs.review_id = r.id
            WHERE r.freight_forwarder_id = :freight_forwarder_id
              AND r.is_active = true
              AND rcs.created_at >= :start_date
              AND rcs.created_at <= :end_date
            GROUP BY rcs.category_name, DATE_TRUNC(:date_trunc, rcs.created_at)
            ORDER BY period, rcs.category_name
        """)
        
        # Execute query
        result = db.execute(query, {
            'freight_forwarder_id': freight_forwarder_id,
            'start_date': start_date,
            'end_date': end_date,
            'date_trunc': date_trunc
        }).fetchall()
        
        # Process results
        categories_data = defaultdict(lambda: {
            'labels': [],
            'data': [],
            'review_counts': []
        })
        
        # Generate all period labels
        all_labels = format_period_labels(period, start_date, end_date)
        
        # Initialize all categories with empty data for all periods
        category_names = set()
        for row in result:
            category_names.add(row.category_name)
        
        for category_name in category_names:
            categories_data[category_name]['labels'] = all_labels.copy()
            categories_data[category_name]['data'] = [0.0] * len(all_labels)
            categories_data[category_name]['review_counts'] = [0] * len(all_labels)
        
        # Fill in actual data
        for row in result:
            category_name = row.category_name
            period_str = row.period.strftime("%Y-%m") if date_trunc == "month" else f"{row.period.year}-Q{((row.period.month - 1) // 3) + 1}"
            
            if period_str in all_labels:
                idx = all_labels.index(period_str)
                categories_data[category_name]['data'][idx] = float(row.avg_score) if row.avg_score else 0.0
                categories_data[category_name]['review_counts'][idx] = int(row.review_count)
        
        # Convert defaultdict to regular dict
        categories = dict(categories_data)
        
        # Prepare response
        response_data = {
            "freight_forwarder_id": freight_forwarder_id,
            "freight_forwarder_name": freight_forwarder.name,
            "period": period,
            "categories": categories
        }
        
        # Cache the result
        set_cached_data(cache_key, response_data)
        
        logger.info(f"Generated score trends for freight_forwarder_id: {freight_forwarder_id}, period: {period}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating score trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate score trends"
        )

@router.get("/score-trends/{freight_forwarder_id}/categories")
async def get_available_categories(
    freight_forwarder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available categories for a freight forwarder.
    Requires annual subscription.
    """
    try:
        # Check if user has annual subscription
        if not validate_annual_subscription(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Annual subscription required to access score trends analytics"
            )
        
        # Verify freight forwarder exists
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == freight_forwarder_id
        ).first()
        
        if not freight_forwarder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freight forwarder not found"
            )
        
        # Get unique categories for this freight forwarder
        query = text("""
            SELECT DISTINCT rcs.category_name
            FROM review_category_scores rcs
            JOIN reviews r ON rcs.review_id = r.id
            WHERE r.freight_forwarder_id = :freight_forwarder_id
              AND r.is_active = true
            ORDER BY rcs.category_name
        """)
        
        result = db.execute(query, {'freight_forwarder_id': freight_forwarder_id}).fetchall()
        categories = [row.category_name for row in result]
        
        return {
            "freight_forwarder_id": freight_forwarder_id,
            "freight_forwarder_name": freight_forwarder.name,
            "available_categories": categories
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available categories"
        )

@router.delete("/score-trends/cache")
async def clear_score_trends_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Clear the score trends cache (admin function).
    Requires annual subscription.
    """
    try:
        # Check if user has annual subscription
        if not validate_annual_subscription(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Annual subscription required to access cache management"
            )
        
        # Clear cache
        global _cache
        _cache.clear()
        
        logger.info(f"Score trends cache cleared by user: {current_user.email}")
        return {"message": "Score trends cache cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )
