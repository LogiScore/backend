from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_locations(
    q: Optional[str] = Query(None, description="Search query for filtering locations"),
    limit: Optional[int] = Query(50, ge=1, le=1000, description="Maximum number of results"),
    region: Optional[str] = Query(None, description="Filter by region (e.g., 'Americas', 'Europe')"),
    country: Optional[str] = Query(None, description="Filter by country code or name"),
    db: Session = Depends(get_db)
):
    """
    Get locations with optional search and filtering.
    
    - **q**: Search query to filter locations by city, state, country, or location name
    - **limit**: Maximum number of results (1-1000, default: 50)
    - **region**: Filter by specific region
    - **country**: Filter by specific country
    """
    try:
        # Build the base query
        base_query = """
        SELECT uuid, location_name, city, state, country, region, subregion
        FROM locations
        WHERE 1=1
        """
        
        params = {}
        
        # Add search filter
        if q and q.strip():
            search_query = """
            AND (
                LOWER(location_name) LIKE LOWER(:search_query) OR
                LOWER(city) LIKE LOWER(:search_query) OR
                LOWER(state) LIKE LOWER(:search_query) OR
                LOWER(country) LIKE LOWER(:search_query)
            )
            """
            base_query += search_query
            params['search_query'] = f"%{q.strip()}%"
        
        # Add region filter
        if region and region.strip():
            region_filter = "AND LOWER(region) = LOWER(:region)"
            base_query += region_filter
            params['region'] = region.strip()
        
        # Add country filter
        if country and country.strip():
            country_filter = "AND LOWER(country) LIKE LOWER(:country)"
            base_query += country_filter
            params['country'] = f"%{country.strip()}%"
        
        # Add ordering and limit
        base_query += " ORDER BY city, country LIMIT :limit"
        params['limit'] = limit
        
        # Execute query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Convert to response format
        locations = []
        for row in rows:
            locations.append({
                "id": str(row.uuid),  # Use UUID as ID for reviews system
                "uuid": str(row.uuid),  # Also include UUID field
                "name": row.location_name if row.location_name else f"{row.city}, {row.state}, {row.country}".strip(', '),
                "city": row.city if row.city else "",
                "state": row.state if row.state else "",
                "country": row.country if row.country else "",
                "region": row.region if row.region else "",
                "subregion": row.subregion if row.subregion else ""
            })
        
        logger.info(f"Returning {len(locations)} locations (query: {q}, region: {region}, country: {country})")
        return locations
        
    except Exception as e:
        logger.error(f"Error processing locations request: {e}")
        raise HTTPException(status_code=500, detail="Error processing locations request")

@router.get("/{location_uuid}")
async def get_location_by_uuid(
    location_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific location by UUID.
    Useful for reviews system to validate location references.
    """
    try:
        query = """
        SELECT uuid, location_name, city, state, country, region, subregion
        FROM locations
        WHERE uuid = :uuid
        """
        
        result = db.execute(text(query), {"uuid": location_uuid})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location = {
            "id": str(row.uuid),
            "uuid": str(row.uuid),
            "name": row.location_name if row.location_name else f"{row.city}, {row.state}, {row.country}".strip(', '),
            "city": row.city if row.city else "",
            "state": row.state if row.state else "",
            "country": row.country if row.country else "",
            "region": row.region if row.region else "",
            "subregion": row.subregion if row.subregion else ""
        }
        
        return location
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location by UUID: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving location")

@router.get("/regions")
async def get_regions(db: Session = Depends(get_db)):
    """Get list of available regions"""
    try:
        query = """
        SELECT DISTINCT region 
        FROM locations 
        WHERE region != '' AND region IS NOT NULL
        ORDER BY region
        """
        
        result = db.execute(text(query))
        regions = [row.region for row in result.fetchall()]
        
        return {"regions": regions}
        
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(status_code=500, detail="Error getting regions")

@router.get("/countries")
async def get_countries(db: Session = Depends(get_db)):
    """Get list of available countries"""
    try:
        query = """
        SELECT DISTINCT country 
        FROM locations 
        WHERE country != '' AND country IS NOT NULL
        ORDER BY country
        """
        
        result = db.execute(text(query))
        countries = [row.country for row in result.fetchall()]
        
        return {"countries": countries}
        
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Error getting countries")

@router.get("/search/autocomplete")
async def search_autocomplete(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Autocomplete endpoint for location search.
    Returns locations that start with the search query.
    """
    try:
        query = """
        SELECT uuid, location_name, city, state, country
        FROM locations
        WHERE (
            LOWER(city) LIKE LOWER(:search_query) OR
            LOWER(location_name) LIKE LOWER(:search_query)
        )
        ORDER BY 
            CASE 
                WHEN LOWER(city) = LOWER(:exact_query) THEN 1
                WHEN LOWER(city) LIKE LOWER(:exact_query) || '%' THEN 2
                ELSE 3
            END,
            city, country
        LIMIT :limit
        """
        
        params = {
            "search_query": f"{q.strip()}%",
            "exact_query": q.strip(),
            "limit": limit
        }
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        locations = []
        for row in rows:
            locations.append({
                "id": str(row.uuid),
                "uuid": str(row.uuid),
                "name": row.location_name if row.location_name else f"{row.city}, {row.state}, {row.country}".strip(', '),
                "city": row.city if row.city else "",
                "state": row.state if row.state else "",
                "country": row.country if row.country else ""
            })
        
        return locations
        
    except Exception as e:
        logger.error(f"Error in autocomplete search: {e}")
        raise HTTPException(status_code=500, detail="Error in autocomplete search")
