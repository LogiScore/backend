-- Comprehensive Fix: Add missing fields to reviews table
-- Date: 2025-01-14
-- Purpose: Fix all schema mismatches between models and actual database

-- 1. Add missing fields to reviews table
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS country VARCHAR(100);

-- 2. Create indexes for the new fields
CREATE INDEX IF NOT EXISTS idx_reviews_city ON reviews(city);
CREATE INDEX IF NOT EXISTS idx_reviews_country ON reviews(country);
CREATE INDEX IF NOT EXISTS idx_reviews_city_country ON reviews(city, country);

-- 3. Update existing reviews with city and country data from branches
UPDATE reviews 
SET 
    city = branches.city,
    country = branches.country
FROM branches 
WHERE reviews.branch_id = branches.id 
  AND reviews.city IS NULL 
  AND reviews.country IS NULL;

-- 4. Add column comments
COMMENT ON COLUMN reviews.city IS 'City from the associated branch for easier querying and filtering';
COMMENT ON COLUMN reviews.country IS 'Country from the associated branch for easier querying and filtering';

-- 5. Verify the fix
SELECT 
    'Reviews schema fix completed' as status,
    COUNT(*) as total_reviews,
    COUNT(city) as reviews_with_city,
    COUNT(country) as reviews_with_country
FROM reviews;

-- 6. Show final reviews table structure
SELECT 
    'Final reviews table structure' as info,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'reviews' 
ORDER BY ordinal_position;
