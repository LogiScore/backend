-- Add missing columns to reviews table
-- This fixes the database compatibility issue with the backend

-- Add missing columns that are referenced in the code but don't exist in the database
ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS overall_rating FLOAT;

-- Add other missing columns that might be needed
ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS review_text TEXT;

-- Add missing columns for the new review system
ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS review_type VARCHAR(50) DEFAULT 'general';

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS is_anonymous BOOLEAN DEFAULT FALSE;

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS review_weight NUMERIC(3,2) DEFAULT 1.0;

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS aggregate_rating NUMERIC(3,2);

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS weighted_rating NUMERIC(3,2);

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS total_questions_rated INTEGER DEFAULT 0;

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

ALTER TABLE reviews 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Verify the columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'reviews' 
ORDER BY ordinal_position;
