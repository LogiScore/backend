from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import pandas as pd
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Global variable to store locations data
locations_df = None

def load_locations_data():
    """Load locations data from CSV file"""
    global locations_df
    
    try:
        # Try to find the CSV file in the documentation folder first
        csv_path = Path(__file__).parent.parent / "documentation" / "Locations.csv"
        
        if not csv_path.exists():
            # If not found in documentation, try project root
            csv_path = Path(__file__).parent.parent / "Locations.csv"
            
        if not csv_path.exists():
            # If not found in root, try current directory
            csv_path = Path("Locations.csv")
            
        if not csv_path.exists():
            logger.warning("Locations.csv not found. Creating sample data structure.")
            # Create sample data structure if CSV doesn't exist
            sample_data = {
                'Location': ['New York, NY, USA', 'London, , UK', 'Tokyo, , Japan'],
                'City': ['New York', 'London', 'Tokyo'],
                'State': ['NY', '', ''],
                'Country': ['USA', 'UK', 'Japan'],
                'Region': ['Americas', 'Europe', 'Asia'],
                'Subregion': ['North America', 'Western Europe', 'Eastern Asia']
            }
            locations_df = pd.DataFrame(sample_data)
            return
        
        # Load CSV data
        locations_df = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded {len(locations_df)} locations from CSV")
        
        # Validate required columns
        required_columns = ['Location', 'City', 'State', 'Country', 'Region', 'Subregion']
        missing_columns = [col for col in required_columns if col not in locations_df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns in CSV: {missing_columns}")
            raise ValueError(f"CSV must contain columns: {required_columns}")
            
        # Fill NaN values with empty strings
        locations_df = locations_df.fillna('')
        
    except Exception as e:
        logger.error(f"Error loading locations data: {e}")
        # Create fallback sample data
        sample_data = {
            'Location': ['New York, NY, USA', 'London, , UK', 'Tokyo, , Japan'],
            'City': ['New York', 'London', 'Tokyo'],
            'State': ['NY', '', ''],
            'Country': ['USA', 'UK', 'Japan'],
            'Region': ['Americas', 'Europe', 'Asia'],
            'Subregion': ['North America', 'Western Europe', 'Eastern Asia']
        }
        locations_df = pd.DataFrame(sample_data)
        logger.info("Using fallback sample data")

def generate_location_id(city: str, country: str) -> str:
    """Generate unique ID for location"""
    if not city or not country:
        return f"unknown-{hash(f'{city}-{country}') % 10000}"
    
    # Clean and format the ID
    city_clean = city.lower().replace(' ', '-').replace(',', '').replace('.', '')
    country_clean = country.lower().replace(' ', '-').replace(',', '').replace('.', '')
    
    return f"{city_clean}-{country_clean}"

@router.on_event("startup")
async def startup_event():
    """Load locations data when the application starts"""
    load_locations_data()

@router.get("/", response_model=List[dict])
async def get_locations(
    q: Optional[str] = Query(None, description="Search query for filtering locations"),
    limit: Optional[int] = Query(50, ge=1, le=1000, description="Maximum number of results"),
    region: Optional[str] = Query(None, description="Filter by region (e.g., 'Americas', 'Europe')"),
    country: Optional[str] = Query(None, description="Filter by country code or name")
):
    """
    Get locations with optional search and filtering.
    
    - **q**: Search query to filter locations by city, state, country, or location name
    - **limit**: Maximum number of results (1-1000, default: 50)
    - **region**: Filter by specific region
    - **country**: Filter by specific country
    """
    global locations_df
    
    if locations_df is None:
        load_locations_data()
    
    if locations_df is None or locations_df.empty:
        raise HTTPException(status_code=500, detail="Locations data not available")
    
    try:
        # Start with all locations
        filtered_df = locations_df.copy()
        
        # Apply search filter
        if q:
            query_lower = q.lower().strip()
            if query_lower:
                # Create mask for search across multiple fields
                mask = (
                    filtered_df['Location'].str.lower().str.contains(query_lower, na=False) |
                    filtered_df['City'].str.lower().str.contains(query_lower, na=False) |
                    filtered_df['State'].str.lower().str.contains(query_lower, na=False) |
                    filtered_df['Country'].str.lower().str.contains(query_lower, na=False)
                )
                filtered_df = filtered_df[mask]
        
        # Apply region filter
        if region:
            region_lower = region.lower().strip()
            if region_lower:
                filtered_df = filtered_df[
                    filtered_df['Region'].str.lower().str.contains(region_lower, na=False)
                ]
        
        # Apply country filter
        if country:
            country_lower = country.lower().strip()
            if country_lower:
                filtered_df = filtered_df[
                    filtered_df['Country'].str.lower().str.contains(country_lower, na=False)
                ]
        
        # Limit results
        filtered_df = filtered_df.head(limit)
        
        # Convert to response format
        locations = []
        for _, row in filtered_df.iterrows():
            location_id = generate_location_id(row['City'], row['Country'])
            
            locations.append({
                "id": location_id,
                "name": row['Location'] if row['Location'] else f"{row['City']}, {row['State']}, {row['Country']}".strip(', '),
                "city": row['City'] if row['City'] else "",
                "state": row['State'] if row['State'] else "",
                "country": row['Country'] if row['Country'] else "",
                "region": row['Region'] if row['Region'] else "",
                "subregion": row['Subregion'] if row['Subregion'] else ""
            })
        
        logger.info(f"Returning {len(locations)} locations (query: {q}, region: {region}, country: {country})")
        return locations
        
    except Exception as e:
        logger.error(f"Error processing locations request: {e}")
        raise HTTPException(status_code=500, detail="Error processing locations request")

@router.get("/regions")
async def get_regions():
    """Get list of available regions"""
    global locations_df
    
    if locations_df is None:
        load_locations_data()
    
    if locations_df is None or locations_df.empty:
        raise HTTPException(status_code=500, detail="Locations data not available")
    
    try:
        regions = locations_df['Region'].dropna().unique().tolist()
        regions = [r for r in regions if r.strip()]  # Remove empty strings
        return {"regions": sorted(regions)}
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(status_code=500, detail="Error getting regions")

@router.get("/countries")
async def get_countries():
    """Get list of available countries"""
    global locations_df
    
    if locations_df is None:
        load_locations_data()
    
    if locations_df is None or locations_df.empty:
        raise HTTPException(status_code=500, detail="Locations data not available")
    
    try:
        countries = locations_df['Country'].dropna().unique().tolist()
        countries = [c for c in countries if c.strip()]  # Remove empty strings
        return {"countries": sorted(countries)}
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Error getting countries")
