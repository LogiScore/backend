-- Remove database constraints from reviews table
-- This script removes constraints that prevent reviews from being created

-- 1. Remove the foreign key constraint on branch_id
-- First, find the constraint name
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'reviews' 
AND constraint_type = 'FOREIGN KEY' 
AND constraint_name LIKE '%branch%';

-- 2. Remove the foreign key constraint (replace 'constraint_name' with actual name)
-- ALTER TABLE reviews DROP CONSTRAINT IF EXISTS reviews_branch_id_fkey;

-- 3. Make branch_id nullable if it's not already
ALTER TABLE reviews ALTER COLUMN branch_id DROP NOT NULL;

-- 4. Remove any check constraints that might prevent NULL branch_id
-- (This will remove all check constraints - be careful in production)
-- ALTER TABLE reviews DROP CONSTRAINT IF EXISTS reviews_branch_id_check;

-- 5. Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'reviews' 
AND column_name = 'branch_id';

-- 6. Check remaining constraints
SELECT 
    constraint_name, 
    constraint_type, 
    column_name
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu 
ON tc.constraint_name = ccu.constraint_name
WHERE tc.table_name = 'reviews';
