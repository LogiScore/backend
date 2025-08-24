# LogiScore Locations API

## Overview
The Locations API provides a comprehensive endpoint for retrieving and filtering location data from a PostgreSQL database with UUID support for the reviews system. The data structure includes: `uuid`, `location_name`, `city`, `state`, `country`, `region`, and `subregion`.

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
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "New York, NY, USA",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "region": "Americas",
    "subregion": "North America"
  },
  {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "uuid": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
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

### 4. GET /api/locations/{uuid}
Get a specific location by UUID. Useful for reviews system validation.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "New York, NY, USA",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "region": "Americas",
  "subregion": "North America"
}
```

### 5. GET /api/locations/search/autocomplete
Autocomplete endpoint for location search with smart ranking.

**Query Parameters:**
- `q` (required): Search query (minimum 2 characters)
- `limit` (optional): Maximum results (1-50, default: 10)

**Example:**
```bash
GET /api/locations/search/autocomplete?q=lon&limit=5
```

## Implementation Details

### Database Integration
- PostgreSQL database with optimized table structure
- UUID primary keys for reviews system integration
- Database indexes for fast searching and filtering
- Efficient SQL queries with parameterized statements

### Search Functionality
- Searches across `Location`, `City`, `State`, and `Country` fields
- Case-insensitive search with partial matching
- Uses pandas for efficient string operations

### Filtering
- Region filtering: Exact match (case-insensitive)
- Country filtering: Partial match (case-insensitive)
- Filters can be combined with search queries

### UUID System
- Each location has a unique UUID for reviews system integration
- UUIDs are automatically generated and indexed
- Consistent with database primary key strategy
- Enables efficient location lookups in reviews

### Performance Features
- Database indexes for fast queries
- Efficient SQL operations with parameterized queries
- Configurable result limits (1-1000)
- Graceful error handling and logging
- Scalable to millions of locations

## File Structure

```
routes/
├── locations.py          # Main locations router (database-based)
├── __init__.py
└── ... (other routes)

migrate_locations_to_db.py    # Migration script for CSV to database
run_locations_migration.py    # Simple migration runner
test_locations.py             # Test script for database endpoint
LOCATIONS_API_README.md       # This documentation
```

## Migration from CSV to Database

To convert your existing CSV data to the database:

1. **Run the migration script:**
   ```bash
   python run_locations_migration.py
   ```

2. **The script will:**
   - Create the `locations` table with UUIDs
   - Import all CSV data with proper indexing
   - Verify data integrity and UUID uniqueness
   - Enable the new database-based API

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
