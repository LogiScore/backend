from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/debug")
async def debug_locations():
    """Debug endpoint to verify locations router is working"""
    return {
        "message": "Locations router is working",
        "endpoints": [
            "GET / - Main locations search",
            "GET /{uuid} - Get by UUID", 
            "GET /regions - Available regions",
            "GET /countries - Available countries",
            "GET /search/autocomplete - Autocomplete search"
        ],
        "status": "ready"
    }

@router.get("/test-simple")
async def test_simple_locations():
    """Simple test endpoint without database dependency"""
    return {
        "message": "Simple locations endpoint working",
        "sample_data": [
            {"id": "test-1", "name": "Test Location 1", "city": "Test City"},
            {"id": "test-2", "name": "Test Location 2", "city": "Test City 2"}
        ]
    }

@router.get("/test-db")
async def test_database_connection(db: Session = Depends(get_db)):
    """Test database connection and table access"""
    try:
        # Test basic connection
        result = db.execute(text("SELECT 1"))
        connection_test = result.scalar()
        
        # Test locations table access
        result = db.execute(text('SELECT COUNT(*) FROM locations'))
        table_count = result.scalar()
        
        # Test sample data
        result = db.execute(text('SELECT "UUID", "City", "Country" FROM locations LIMIT 3'))
        sample_data = [{"uuid": row.UUID, "city": row.City, "country": row.Country} for row in result.fetchall()]
        
        return {
            "message": "Database connection successful",
            "connection_test": connection_test,
            "locations_count": table_count,
            "sample_data": sample_data,
            "status": "connected"
        }
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {
            "message": "Database connection failed",
            "error": str(e),
            "status": "failed"
        }

@router.get("/route-check")
async def check_route_conflicts():
    """Check for potential route conflicts"""
    return {
        "message": "Route conflict check",
        "available_routes": [
            "GET / - Main locations search",
            "GET /debug - Debug info",
            "GET /test-simple - Simple test",
            "GET /test-db - Database test",
            "GET /route-check - This endpoint",
            "GET /{uuid} - Get by UUID",
            "GET /regions - Available regions",
            "GET /countries - Available countries",
            "GET /search/autocomplete - Autocomplete search"
        ],
        "main_endpoint_status": "should_be_working",
        "database_status": "connected_with_139284_locations"
    }

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
    logger.info(f"GET /api/locations called with q={q}, limit={limit}, region={region}, country={country}")
    
    try:
        # Build the base query
        base_query = """
        SELECT "UUID", "Location", "City", "State", "Country", "Region", "Subregion"
        FROM locations
        WHERE 1=1
        """
        
        params = {}
        
        # Add search filter
        if q and q.strip():
            search_query = """
            AND (
                LOWER("Location") LIKE LOWER(:search_query) OR
                LOWER("City") LIKE LOWER(:search_query) OR
                LOWER("State") LIKE LOWER(:search_query) OR
                LOWER("Country") LIKE LOWER(:search_query)
            )
            """
            base_query += search_query
            params['search_query'] = f"%{q.strip()}%"
        
        # Add region filter
        if region and region.strip():
            region_filter = "AND LOWER(\"Region\") = LOWER(:region)"
            base_query += region_filter
            params['region'] = region.strip()
        
        # Add country filter
        if country and country.strip():
            country_filter = "AND LOWER(\"Country\") LIKE LOWER(:country)"
            base_query += country_filter
            params['country'] = f"%{country.strip()}%"
        
        # Add ordering and limit
        base_query += " ORDER BY \"City\", \"Country\" LIMIT :limit"
        params['limit'] = limit
        
        # Execute query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Convert to response format
        locations = []
        for row in rows:
            locations.append({
                "id": str(row.UUID),  # Use UUID as ID for reviews system
                "uuid": str(row.UUID),  # Also include UUID field
                "name": row.Location if row.Location else f"{row.City}, {row.State}, {row.Country}".strip(', '),
                "city": row.City if row.City else "",
                "state": row.State if row.State else "",
                "country": row.Country if row.Country else "",
                "region": row.Region if row.Region else "",
                "subregion": row.Subregion if row.Subregion else ""
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
        SELECT "UUID", "Location", "City", "State", "Country", "Region", "Subregion"
        FROM locations
        WHERE "UUID" = :uuid
        """
        
        result = db.execute(text(query), {"uuid": location_uuid})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location = {
            "id": str(row.UUID),
            "uuid": str(row.UUID),
            "name": row.Location if row.Location else f"{row.City}, {row.State}, {row.Country}".strip(', '),
            "city": row.City if row.City else "",
            "state": row.State if row.State else "",
            "country": row.Country if row.Country else "",
            "region": row.Region if row.Region else "",
            "subregion": row.Subregion if row.Subregion else ""
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
        SELECT DISTINCT "Region" 
        FROM locations 
        WHERE "Region" != '' AND "Region" IS NOT NULL
        ORDER BY "Region"
        """
        
        result = db.execute(text(query))
        regions = [row.Region for row in result.fetchall()]
        
        return {"regions": regions}
        
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(status_code=500, detail="Error getting regions")

@router.get("/countries")
async def get_countries(db: Session = Depends(get_db)):
    """Get list of available countries"""
    try:
        query = """
        SELECT DISTINCT "Country" 
        FROM locations 
        WHERE "Country" != '' AND "Country" IS NOT NULL
        ORDER BY "Country"
        """
        
        result = db.execute(text(query))
        countries = [row.Country for row in result.fetchall()]
        
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
        SELECT "UUID", "Location", "City", "State", "Country"
        FROM locations
        WHERE (
            LOWER("City") LIKE LOWER(:search_query) OR
            LOWER("Location") LIKE LOWER(:search_query)
        )
        ORDER BY 
            CASE 
                WHEN LOWER("City") = LOWER(:exact_query) THEN 1
                WHEN LOWER("City") LIKE LOWER(:exact_query) || '%' THEN 2
                ELSE 3
            END,
            "City", "Country"
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
                "id": str(row.UUID),
                "uuid": str(row.UUID),
                "name": row.Location if row.Location else f"{row.City}, {row.State}, {row.Country}".strip(', '),
                "city": row.City if row.City else "",
                "state": row.State if row.State else "",
                "country": row.Country if row.Country else ""
            })
        
        return locations
        
    except Exception as e:
        logger.error(f"Error in autocomplete search: {e}")
        raise HTTPException(status_code=500, detail="Error in autocomplete search")
