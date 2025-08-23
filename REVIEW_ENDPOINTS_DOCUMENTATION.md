# LogiScore Review Endpoints Documentation

## Overview

This document describes the enhanced review endpoints that support country and city-based filtering, search functionality, and pagination for the LogiScore platform.

## Base URL

All endpoints are prefixed with `/api/reviews`

## Endpoints

### 1. Get Reviews with Filtering and Pagination

**Endpoint:** `GET /api/reviews/`

**Description:** Retrieves reviews with support for location-based filtering, search, and pagination.

**Query Parameters:**
- `country` (optional): Filter reviews by country (case-insensitive partial match)
- `city` (optional): Filter reviews by city (case-insensitive partial match)
- `freight_forwarder_id` (optional): Filter reviews by specific freight forwarder ID
- `search` (optional): Search in review content (questions, categories, rating definitions)
- `page` (optional): Page number for pagination (default: 1, minimum: 1)
- `page_size` (optional): Number of reviews per page (default: 20, range: 1-100)

**Example Requests:**

```bash
# Get all reviews
GET /api/reviews/

# Get reviews by country
GET /api/reviews/?country=australia

# Get reviews by city and country
GET /api/reviews/?city=berlin&country=germany

# Get reviews by city only
GET /api/reviews/?city=sydney

# Get reviews by freight forwarder
GET /api/reviews/?freight_forwarder_id=123e4567-e89b-12d3-a456-426614174000

# Search reviews
GET /api/reviews/?search=service

# Pagination
GET /api/reviews/?page=2&page_size=10

# Combined filters
GET /api/reviews/?country=australia&city=sydney&page=1&page_size=20
```

**Response Format:**

```json
{
  "reviews": [
    {
      "id": "uuid",
      "freight_forwarder_id": "uuid",
      "location_id": "uuid",
      "city": "Sydney",
      "country": "Australia",
      "review_type": "general",
      "is_anonymous": false,
      "review_weight": 1.0,
      "aggregate_rating": 4.0,
      "weighted_rating": 4.0,
      "total_questions_rated": 10,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "filters": {
    "country": "australia",
    "city": "sydney"
  }
}
```

### 2. Get Available Countries

**Endpoint:** `GET /api/reviews/countries`

**Description:** Retrieves a list of all countries that have reviews. Useful for frontend filtering dropdowns.

**Query Parameters:** None

**Example Request:**

```bash
GET /api/reviews/countries
```

**Response Format:**

```json
[
  "Australia",
  "Canada",
  "Germany",
  "United Kingdom",
  "United States"
]
```

### 3. Get Available Cities

**Endpoint:** `GET /api/reviews/cities`

**Description:** Retrieves a list of all cities that have reviews, optionally filtered by country.

**Query Parameters:**
- `country` (optional): Filter cities by country (case-insensitive partial match)

**Example Requests:**

```bash
# Get all cities
GET /api/reviews/cities

# Get cities in a specific country
GET /api/reviews/cities?country=australia
```

**Response Format:**

```json
[
  {
    "city": "Melbourne",
    "country": "Australia"
  },
  {
    "city": "Sydney",
    "country": "Australia"
  }
]
```

### 4. Get Review Statistics by Location

**Endpoint:** `GET /api/reviews/statistics/location`

**Description:** Retrieves review statistics (counts, averages, types) filtered by location.

**Query Parameters:**
- `country` (optional): Filter statistics by country (case-insensitive partial match)
- `city` (optional): Filter statistics by city (case-insensitive partial match)

**Example Requests:**

```bash
# Get statistics for a country
GET /api/reviews/statistics/location?country=australia

# Get statistics for a city
GET /api/reviews/statistics/location?city=sydney&country=australia
```

**Response Format:**

```json
{
  "total_reviews": 45,
  "average_rating": 3.8,
  "total_weighted_rating": 171.0,
  "review_types": {
    "general": 30,
    "import": 10,
    "export": 5
  },
  "anonymous_count": 15,
  "authenticated_count": 30,
  "location": {
    "country": "Australia",
    "city": "Sydney"
  }
}
```

## Filtering Logic

### Country Filter
- Uses case-insensitive partial matching with `ILIKE`
- Matches reviews where the country field contains the provided value
- Example: `country=australia` will match "Australia", "australia", "AUSTRALIA"

### City Filter
- Uses case-insensitive partial matching with `ILIKE`
- Can be combined with country filter for more precise results
- Example: `city=berlin&country=germany` will match reviews in Berlin, Germany

### Search Filter
- Searches across review content including:
  - Question text
  - Category names
  - Rating definitions
- Uses case-insensitive partial matching
- Joins with `ReviewCategoryScore` table for comprehensive search

### Combined Filters
- All filters can be used together
- Results are the intersection of all applied filters
- Pagination is applied after filtering

## Pagination

- **Page numbering starts at 1**
- **Default page size is 20**
- **Maximum page size is 100**
- **Total count and pages are calculated before pagination**
- **Results are ordered by creation date (newest first)**

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server-side error

Error responses include a `detail` field with error information.

## Performance Considerations

- **Indexing**: Ensure database indexes exist on:
  - `reviews.country`
  - `reviews.city`
  - `reviews.freight_forwarder_id`
  - `reviews.created_at`
  - `reviews.is_active`

- **Query Optimization**: 
  - Filters are applied in the most efficient order
  - Pagination is applied after filtering to minimize data transfer
  - Search queries use JOINs only when necessary

## Frontend Integration Examples

### React/Svelte Example

```javascript
// Get reviews by country
const fetchReviewsByCountry = async (country, page = 1) => {
  const response = await fetch(`/api/reviews/?country=${country}&page=${page}`);
  const data = await response.json();
  return data;
};

// Get available countries for dropdown
const fetchCountries = async () => {
  const response = await fetch('/api/reviews/countries');
  const countries = await response.json();
  return countries;
};

// Get cities in a country
const fetchCitiesByCountry = async (country) => {
  const response = await fetch(`/api/reviews/cities?country=${country}`);
  const cities = await response.json();
  return cities;
};
```

### Search and Filter Example

```javascript
// Combined search with filters
const searchReviews = async (filters) => {
  const params = new URLSearchParams();
  
  if (filters.country) params.append('country', filters.country);
  if (filters.city) params.append('city', filters.city);
  if (filters.search) params.append('search', filters.search);
  if (filters.page) params.append('page', filters.page);
  if (filters.pageSize) params.append('page_size', filters.pageSize);
  
  const response = await fetch(`/api/reviews/?${params.toString()}`);
  const data = await response.json();
  return data;
};
```

## Testing

Use the provided `test_review_endpoints.py` script to test all endpoints:

```bash
python test_review_endpoints.py
```

Make sure your backend is running on `http://localhost:8000` or update the `BASE_URL` in the test script.

## Database Requirements

The following database fields must exist in the `reviews` table:

- `country` (String, nullable)
- `city` (String, nullable)
- `freight_forwarder_id` (UUID, not null)
- `is_active` (Boolean, default true)
- `created_at` (DateTime)
- `aggregate_rating` (Numeric)
- `weighted_rating` (Numeric)

## Security Considerations

- All endpoints are publicly accessible (no authentication required)
- Input validation is performed on all query parameters
- SQL injection protection through SQLAlchemy ORM
- Rate limiting should be implemented at the application level
