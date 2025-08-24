# Migration: Add City and Country Fields to Reviews Table

## Overview
This migration adds `city` and `country` fields directly to the `reviews` table, populated from the associated `branches` table. This allows for easier querying and filtering of reviews by location without requiring JOINs.

## What This Migration Does

### 1. Schema Changes
- Adds `city VARCHAR(100)` column to `reviews` table
- Adds `country VARCHAR(100)` column to `reviews` table
- Both fields are nullable to maintain backward compatibility

### 2. Performance Optimizations
- Creates index on `city` field: `idx_reviews_city`
- Creates index on `country` field: `idx_reviews_country`
- Creates composite index on `(city, country)` for multi-field queries

### 3. Data Migration
- Populates existing reviews with city/country data from the `branches` table
- Uses the `branch_id` relationship to fetch location data
- Only updates reviews where city/country are NULL to avoid overwriting existing data

### 4. Documentation
- Adds column comments explaining the purpose of each field
- Documents that these fields are for easier querying and filtering

## Files Created/Modified

### New Files
- `add_city_country_to_reviews.sql` - SQL migration script
- `migrate_add_city_country.py` - Python migration script
- `MIGRATION_CITY_COUNTRY_README.md` - This documentation file

### Modified Files
- `database/models.py` - Added city and country fields to Review model
- `database/migrate_schema.py` - Updated main migration script to include new fields

## Running the Migration

### Option 1: Python Script (Recommended)
```bash
python migrate_add_city_country.py
```

### Option 2: SQL Script
```bash
psql $DATABASE_URL -f add_city_country_to_reviews.sql
```

### Option 3: Main Migration Script
```bash
python database/migrate_schema.py
```

## Benefits

1. **Performance**: Eliminates need for JOINs when filtering by location
2. **Simplicity**: Queries can filter directly on reviews table
3. **Analytics**: Easier to generate location-based reports and statistics
4. **Backward Compatibility**: Existing code continues to work unchanged

## Example Usage

### Before Migration (Required JOIN)
```sql
SELECT r.*, b.city, b.country 
FROM reviews r 
JOIN branches b ON r.branch_id = b.id 
WHERE b.city = 'London';
```

### After Migration (Direct Query)
```sql
SELECT * FROM reviews 
WHERE city = 'London';
```

### Filter by Country
```sql
SELECT * FROM reviews 
WHERE country = 'United Kingdom';
```

### Filter by City and Country
```sql
SELECT * FROM reviews 
WHERE city = 'London' AND country = 'United Kingdom';
```

## Verification

After running the migration, you can verify it was successful by:

1. Checking if columns exist:
```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'reviews' 
  AND column_name IN ('city', 'country');
```

2. Checking data population:
```sql
SELECT 
    COUNT(*) as total_reviews,
    COUNT(city) as reviews_with_city,
    COUNT(country) as reviews_with_country
FROM reviews;
```

3. Checking indexes:
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'reviews' 
  AND indexname LIKE '%city%' OR indexname LIKE '%country%';
```

## Rollback (If Needed)

To rollback this migration:

```sql
-- Drop indexes
DROP INDEX IF EXISTS idx_reviews_city;
DROP INDEX IF EXISTS idx_reviews_country;
DROP INDEX IF EXISTS idx_reviews_city_country;

-- Drop columns
ALTER TABLE reviews DROP COLUMN IF EXISTS city;
ALTER TABLE reviews DROP COLUMN IF EXISTS country;
```

## Notes

- The migration is idempotent and can be run multiple times safely
- Existing reviews will be populated with city/country data from branches
- New reviews should populate these fields when created (application logic update required)
- The fields are nullable, so existing functionality remains unchanged
