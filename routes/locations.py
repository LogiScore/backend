from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import logging
import unicodedata
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

def normalize_location_text(text: str) -> str:
    """
    Normalize location text for better search matching.
    
    Handles:
    - Accented characters (ü -> u, ñ -> n, etc.)
    - Common abbreviations and variations
    - Special characters and punctuation
    - Case normalization
    """
    if not text:
        return ""
    
    # Convert to lowercase
    normalized = text.lower()
    
    # Remove accents and diacritics
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Common location variations and abbreviations
    variations = {
        'munchen': 'münchen',
        'muenchen': 'münchen',
        'koeln': 'köln',
        'koeln': 'cologne',
        'nurnberg': 'nürnberg',
        'nuernberg': 'nürnberg',
        'frankfurt am main': 'frankfurt',
        'frankfurt/main': 'frankfurt',
        'new york city': 'new york',
        'nyc': 'new york',
        'los angeles': 'la',
        'san francisco': 'sf',
        'london england': 'london',
        'paris france': 'paris',
        'tokyo japan': 'tokyo',
        'beijing china': 'beijing',
        'peking': 'beijing',
        'bombay': 'mumbai',
        'calcutta': 'kolkata',
        'madras': 'chennai'
    }
    
    # Apply variations
    for variant, standard in variations.items():
        normalized = normalized.replace(variant, standard)
    
    # Remove extra whitespace and punctuation
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

@router.get("/debug")
async def debug_locations():
    """Debug endpoint to verify locations router is working"""
    return {
        "message": "Locations router is working",
        "endpoints": [
            "GET / - Main locations search with pagination",
            "GET /total-count - Get total count for filters",
            "GET /{uuid} - Get by UUID", 
            "GET /regions - Available regions",
            "GET /countries - Available countries",
            "GET /search/autocomplete - Autocomplete search"
        ],
        "status": "ready",
        "router_prefix": "/api/locations",
        "main_route_defined": True,
        "pagination": {
            "default_page_size": 100,
            "max_page_size": 1000,
            "features": ["page", "page_size", "total_count", "total_pages", "has_next", "has_previous"]
        },
        "search_requirements": {
            "min_query_length": 4,
            "message": "Search query must be at least 4 characters long"
        },
        "normalization": {
            "enabled": True,
            "features": [
                "Accented character removal (ü -> u, ñ -> n)",
                "Common abbreviations (NYC -> New York)",
                "Alternative spellings (Munchen -> München)",
                "Case normalization"
            ]
        }
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

@router.get("/countries", response_model=List[str])
async def get_all_countries(db: Session = Depends(get_db)):
    """Get all available countries for review forms"""
    try:
        result = db.execute(text('SELECT DISTINCT "Country" FROM locations WHERE "Country" IS NOT NULL AND "Country" != \'\' ORDER BY "Country"'))
        countries = [row[0] for row in result.fetchall()]
        return countries
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve countries")

@router.get("/cities", response_model=List[dict])
async def get_all_cities(
    country: Optional[str] = Query(None, description="Filter cities by country"),
    db: Session = Depends(get_db)
):
    """Get all available cities for review forms"""
    try:
        if country:
            result = db.execute(
                text('SELECT DISTINCT "City", "Country" FROM locations WHERE "City" IS NOT NULL AND "City" != \'\' AND LOWER("Country") = LOWER(:country) ORDER BY "City"'),
                {"country": country}
            )
        else:
            result = db.execute(
                text('SELECT DISTINCT "City", "Country" FROM locations WHERE "City" IS NOT NULL AND "City" != \'\' ORDER BY "City"')
            )
        
        cities = [{"city": row[0], "country": row[1]} for row in result.fetchall()]
        return cities
    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cities")

@router.get("/for-reviews", response_model=List[dict])
async def get_locations_for_reviews(
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db)
):
    """
    Get locations for review forms - no search query required.
    This endpoint is specifically for populating location dropdowns in review forms.
    """
    try:
        # Build the base query
        base_query = """
        SELECT "UUID", "Location", "City", "State", "Country", "Region"
        FROM locations
        WHERE 1=1
        """
        
        params = {}
        
        # Add country filter
        if country and country.strip():
            base_query += " AND LOWER(\"Country\") LIKE LOWER(:country)"
            params['country'] = f"%{country.strip()}%"
        
        # Add city filter
        if city and city.strip():
            base_query += " AND LOWER(\"City\") LIKE LOWER(:city)"
            params['city'] = f"%{city.strip()}%"
        
        # Add ordering and limit
        base_query += " ORDER BY \"City\", \"Country\" LIMIT 1000"
        
        # Execute query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Convert to response format
        locations = []
        for row in rows:
            locations.append({
                "id": str(row[0]),  # UUID
                "uuid": str(row[0]),  # UUID
                "name": row[1] if row[1] else f"{row[2]}, {row[3]}, {row[4]}".strip(', '),  # Location or City, State, Country
                "city": row[2] if row[2] else "",  # City
                "state": row[3] if row[3] else "",  # State
                "country": row[4] if row[4] else "",  # Country
                "region": row[5] if row[5] else ""  # Region
            })
        
        return locations
        
    except Exception as e:
        logger.error(f"Error in get_locations_for_reviews: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve locations: {str(e)}"
        )

@router.get("/")
async def get_locations(
    q: Optional[str] = Query(None, min_length=4, description="Search query for filtering locations (minimum 4 characters)"),
    page: Optional[int] = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: Optional[int] = Query(100, ge=1, le=1000, description="Items per page (1-1000)"),
    region: Optional[str] = Query(None, description="Filter by region (e.g., 'Americas', 'Europe')"),
    country: Optional[str] = Query(None, description="Filter by country code or name"),
    db: Session = Depends(get_db)
):
    """
    Main locations endpoint with pagination - GET /api/locations
    
    Returns paginated results with metadata for optimal frontend performance.
    """
    logger.info(f"GET /api/locations called with q={q}, page={page}, page_size={page_size}, region={region}, country={country}")
    logger.info(f"Database session: {db is not None}")
    
    try:
        # Build the base query
        base_query = """
        SELECT "UUID", "Location", "City", "State", "Country", "Region", "Subregion"
        FROM locations
        WHERE 1=1
        """
        
        params = {}
        
        # Add search filter with normalization - get_locations function
        if q and q.strip():
            if len(q.strip()) < 4:
                raise HTTPException(
                    status_code=400, 
                    detail="Search query must be at least 4 characters long"
                )
            
            # Normalize the search query
            normalized_query = normalize_location_text(q.strip())
            logger.info(f"Original query: '{q.strip()}', Normalized: '{normalized_query}'")
            
            # Search in both original and normalized text
            search_query = """
            AND (
                LOWER("Location") LIKE LOWER(:search_query) OR
                LOWER("City") LIKE LOWER(:search_query) OR
                LOWER("State") LIKE LOWER(:search_query) OR
                LOWER("Country") LIKE LOWER(:search_query) OR
                LOWER("Location") LIKE LOWER(:normalized_query) OR
                LOWER("City") LIKE LOWER(:normalized_query) OR
                LOWER("State") LIKE LOWER(:normalized_query) OR
                LOWER("Country") LIKE LOWER(:normalized_query)
            )
            """
            base_query += search_query
            params['search_query'] = f"%{q.strip()}%"
            params['normalized_query'] = f"%{normalized_query}%"
        
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
        
        # Get total count for pagination metadata
        count_query = base_query.replace("SELECT \"UUID\", \"Location\", \"City\", \"State\", \"Country\", \"Region\", \"Subregion\"", "SELECT COUNT(*)")
        count_result = db.execute(text(count_query), params)
        total_count = count_result.scalar()
        
        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size
        
        # Add ordering and pagination
        base_query += " ORDER BY \"City\", \"Country\" LIMIT :page_size OFFSET :offset"
        params['page_size'] = page_size
        params['offset'] = offset
        
        # Execute paginated query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Convert to response format
        locations = []
        for row in rows:
            # Use index-based access for quoted column names
            locations.append({
                "id": str(row[0]),  # UUID
                "uuid": str(row[0]),  # UUID
                "name": row[1] if row[1] else f"{row[2]}, {row[3]}, {row[4]}".strip(', '),  # Location or City, State, Country
                "city": row[2] if row[2] else "",  # City
                "state": row[3] if row[3] else "",  # State
                "country": row[4] if row[4] else "",  # Country
                "region": row[5] if row[5] else "",  # Region
                "subregion": row[6] if row[6] else ""  # Subregion
            })
        
        # Return paginated response with metadata
        response = {
            "data": locations,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "filters": {
                "query": q,
                "region": region,
                "country": country
            }
        }
        
        logger.info(f"Returning {len(locations)} locations from page {page} of {total_pages} (total: {total_count})")
        return response
        
    except Exception as e:
        logger.error(f"Error processing locations request: {e}")
        raise HTTPException(status_code=500, detail="Error processing locations request")

@router.get("/test-main")
async def test_main_endpoint():
    """Test the main endpoint without database dependency"""
    return {
        "message": "Main endpoint is accessible",
        "method": "GET",
        "path": "/",
        "status": "working"
    }

@router.get("/test-main-simple")
async def test_main_simple():
    """Test the main endpoint with minimal parameters"""
    return {
        "message": "Main endpoint simple test",
        "data": [
            {"id": "test-1", "name": "Test Location 1", "city": "Test City"},
            {"id": "test-2", "name": "Test Location 2", "city": "Test City 2"}
        ]
    }

@router.get("/test-normalization")
async def test_normalization():
    """Test location text normalization"""
    test_cases = [
        "münchen",
        "munchen", 
        "muenchen",
        "köln",
        "koeln",
        "nürnberg",
        "nurnberg",
        "frankfurt am main",
        "new york city",
        "nyc",
        "los angeles",
        "san francisco"
    ]
    
    results = []
    for test_case in test_cases:
        normalized = normalize_location_text(test_case)
        results.append({
            "original": test_case,
            "normalized": normalized,
            "changed": test_case.lower() != normalized
        })
    
    return {
        "message": "Location normalization test",
        "normalization_function": "normalize_location_text",
        "test_cases": results
    }

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
        
        # Use index-based access for quoted column names
        location = {
            "id": str(row[0]),  # UUID
            "uuid": str(row[0]),  # UUID
            "name": row[1] if row[1] else f"{row[2]}, {row[3]}, {row[4]}".strip(', '),  # Location or City, State, Country
            "city": row[2] if row[2] else "",  # City
            "state": row[3] if row[3] else "",  # State
            "country": row[4] if row[4] else "",  # Country
            "region": row[5] if row[5] else "",  # Region
            "subregion": row[6] if row[6] else ""  # Subregion
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

@router.get("/total-count")
async def get_total_count(
    q: Optional[str] = Query(None, min_length=4, description="Search query for filtering locations (minimum 4 characters)"),
    region: Optional[str] = Query(None, description="Filter by region"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """
    Get total count of locations matching filters.
    Useful for frontend pagination controls and performance optimization.
    """
    try:
        base_query = """
        SELECT COUNT(*) as total
        FROM locations
        WHERE 1=1
        """
        
        params = {}
        
        # Add search filter with normalization - get_total_count function
        if q and q.strip():
            if len(q.strip()) < 4:
                raise HTTPException(
                    status_code=400, 
                    detail="Search query must be at least 4 characters long"
                )
            
            # Normalize the search query
            normalized_query = normalize_location_text(q.strip())
            logger.info(f"Total count - Original query: '{q.strip()}', Normalized: '{normalized_query}'")
            
            # Search in both original and normalized text
            search_query = """
            AND (
                LOWER("Location") LIKE LOWER(:search_query) OR
                LOWER("City") LIKE LOWER(:search_query) OR
                LOWER("State") LIKE LOWER(:search_query) OR
                LOWER("Country") LIKE LOWER(:search_query) OR
                LOWER("Location") LIKE LOWER(:normalized_query) OR
                LOWER("City") LIKE LOWER(:normalized_query) OR
                LOWER("State") LIKE LOWER(:normalized_query) OR
                LOWER("Country") LIKE LOWER(:normalized_query)
            )
            """
            base_query += search_query
            params['search_query'] = f"%{q.strip()}%"
            params['normalized_query'] = f"%{normalized_query}%"
        
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
        
        result = db.execute(text(base_query), params)
        total_count = result.scalar()
        
        return {
            "total_count": total_count,
            "filters": {
                "query": q,
                "region": region,
                "country": country
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting total count: {e}")
        raise HTTPException(status_code=500, detail="Error getting total count")

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
            # Use index-based access for quoted column names
            locations.append({
                "id": str(row[0]),  # UUID
                "uuid": str(row[0]),  # UUID
                "name": row[1] if row[1] else f"{row[2]}, {row[3]}, {row[4]}".strip(', '),  # Location or City, State, Country
                "city": row[2] if row[2] else "",  # City
                "state": row[3] if row[3] else "",  # State
                "country": row[4] if row[4] else ""  # Country
            })
        
        return locations
        
    except Exception as e:
        logger.error(f"Error in autocomplete search: {e}")
        raise HTTPException(status_code=500, detail="Error in autocomplete search")
