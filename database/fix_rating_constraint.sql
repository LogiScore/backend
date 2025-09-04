-- Fix review_category_scores rating constraint to accept 0-5 range instead of 0-4
-- This script updates the database constraint to match the application validation.

-- First, check if the constraint exists
SELECT conname, pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid = 'review_category_scores'::regclass 
AND contype = 'c'
AND conname = 'review_category_scores_rating_check';

-- Drop the old constraint if it exists
ALTER TABLE review_category_scores DROP CONSTRAINT IF EXISTS review_category_scores_rating_check;

-- Create new constraint with 0-5 range
ALTER TABLE review_category_scores 
ADD CONSTRAINT review_category_scores_rating_check 
CHECK (rating >= 0 AND rating <= 5);

-- Verify the new constraint
SELECT conname, pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid = 'review_category_scores'::regclass 
AND contype = 'c'
AND conname = 'review_category_scores_rating_check';
