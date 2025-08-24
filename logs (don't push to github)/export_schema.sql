-- Export current database schema
-- This will show what columns actually exist in your production database

-- Check reviews table structure
SELECT 
    'reviews' as table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'reviews' 
ORDER BY ordinal_position;

-- Check freight_forwarders table structure
SELECT 
    'freight_forwarders' as table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_name = 'freight_forwarders' 
ORDER BY ordinal_position;

-- Check if overall_rating column exists in reviews
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'reviews' AND column_name = 'overall_rating'
        ) THEN '✅ overall_rating column EXISTS'
        ELSE '❌ overall_rating column MISSING'
    END as overall_rating_status;

-- Check table relationships
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name IN ('reviews', 'freight_forwarders');
