-- Migration: Add city and country fields to reviews table
-- Date: 2025-01-14
-- Purpose: Add city and country fields from branches table to reviews table for easier querying

-- Add new columns to reviews table
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS country VARCHAR(100);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reviews_city ON reviews(city);
CREATE INDEX IF NOT EXISTS idx_reviews_country ON reviews(country);
CREATE INDEX IF NOT EXISTS idx_reviews_city_country ON reviews(city, country);

-- Update existing reviews with city and country data from branches table
UPDATE reviews 
SET 
    city = branches.city,
    country = branches.country
FROM branches 
WHERE reviews.branch_id = branches.id 
  AND reviews.city IS NULL 
  AND reviews.country IS NULL;

-- Add comments to document the new fields
COMMENT ON COLUMN reviews.city IS 'City from the associated branch for easier querying and filtering';
COMMENT ON COLUMN reviews.country IS 'Country from the associated branch for easier querying and filtering';

-- Verify the migration
SELECT 
    'Migration completed successfully' as status,
    COUNT(*) as total_reviews,
    COUNT(city) as reviews_with_city,
    COUNT(country) as reviews_with_country
FROM reviews;
