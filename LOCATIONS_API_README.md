# LogiScore Locations API

## Overview
The Locations API provides a comprehensive endpoint for retrieving and filtering location data based on the CSV structure: `Location`, `City`, `State`, `Country`, `Region`, and `Subregion`.

## Endpoints

### 1. GET /api/locations
Retrieve locations with optional search and filtering.

**Query Parameters:**
- `q` (optional): Search query for filtering locations across all fields
- `limit` (optional): Maximum number of results (1-1000, default: 50)
- `region` (optional): Filter by specific region (e.g., "Americas", "Europe")
- `country` (optional): Filter by country code or name

**Example Requests:**
```bash
# Get all locations
GET /api/locations

# Search locations by query
GET /api/locations?q=new york

# Filter by region
GET /api/locations?region=Americas

# Search with limit
GET /api/locations?q=london&limit=10

# Combined filters
GET /api/locations?region=Europe&country=Germany&limit=20
```

**Response Format:**
```json
[
  {
    "id": "new-york-usa",
    "name": "New York, NY, USA",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "region": "Americas",
    "subregion": "North America"
  },
  {
    "id": "london-uk",
    "name": "London, , UK",
    "city": "London",
    "state": "",
    "country": "UK",
    "region": "Europe",
    "subregion": "Western Europe"
  }
]
```

### 2. GET /api/locations/regions
Get list of available regions.

**Response:**
```json
{
  "regions": ["Americas", "Asia", "Europe", "Oceania"]
}
```

### 3. GET /api/locations/countries
Get list of available countries.

**Response:**
```json
{
  "countries": ["Australia", "Brazil", "Canada", "China", "France", "Germany", "India", "Japan", "Mexico", "UK", "USA"]
}
```

## Implementation Details

### Data Loading
- CSV data is loaded once on application startup for performance
- Falls back to sample data if `Locations.csv` is not found
- Automatically handles missing or malformed data

### Search Functionality
- Searches across `Location`, `City`, `State`, and `Country` fields
- Case-insensitive search with partial matching
- Uses pandas for efficient string operations

### Filtering
- Region filtering: Exact match (case-insensitive)
- Country filtering: Partial match (case-insensitive)
- Filters can be combined with search queries

### ID Generation
- Unique IDs are generated from city and country combinations
- Format: `{city}-{country}` (lowercase, hyphenated)
- Handles special characters and edge cases

### Performance Features
- Data loaded once on startup, not per request
- Efficient pandas operations for filtering
- Configurable result limits (1-1000)
- Graceful error handling and logging

## File Structure

```
routes/
├── locations.py          # Main locations router
├── __init__.py
└── ... (other routes)

Locations.csv             # Location data file
test_locations.py         # Test script for endpoint
LOCATIONS_API_README.md   # This documentation
```

## CSV Format Requirements

The `Locations.csv` file must contain these columns:
- `Location`: Full location string (e.g., "New York, NY, USA")
- `City`: City name
- `State`: State/province (can be empty)
- `Country`: Country name or code
- `Region`: Geographic region (e.g., "Americas", "Europe")
- `Subregion`: Sub-region (e.g., "North America", "Western Europe")

## Error Handling

- **500 Internal Server Error**: When locations data is unavailable
- **Graceful fallbacks**: Sample data if CSV is missing
- **Input validation**: Query parameter validation and sanitization
- **Logging**: Comprehensive logging for debugging

## Testing

Run the test script to verify endpoint functionality:

```bash
# Start your FastAPI server first
python main.py

# In another terminal, run the test script
python test_locations.py
```

## Dependencies

- `fastapi`: Web framework
- `pandas`: CSV data handling
- `python-multipart`: Query parameter parsing

## Future Enhancements

- Database integration for larger datasets
- Caching for frequently accessed queries
- Pagination for large result sets
- Geocoding integration
- Location validation and standardization
- Rate limiting and API key authentication

## Security Considerations

- Input sanitization for search queries
- Parameter validation and limits
- No SQL injection risks (CSV-based)
- CORS configuration inherited from main app

## Deployment Notes

- Ensure `Locations.csv` is included in deployment
- Monitor memory usage with large CSV files
- Consider database migration for production use
- Implement proper logging and monitoring
