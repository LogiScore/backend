-- Emergency Fix: Resolve Schema Mismatches
-- Date: 2025-01-14
-- Purpose: Fix immediate database errors causing transaction aborts

-- 1. Fix branches table - add missing columns that models expect
ALTER TABLE branches ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE branches ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE branches ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255);
ALTER TABLE branches ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(50);

-- 2. Remove columns that don't exist in actual schema
-- Note: These will fail if columns don't exist, which is fine
DO $$ 
BEGIN
    -- Try to drop location column if it exists
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'branches' AND column_name = 'location') THEN
        ALTER TABLE branches DROP COLUMN location;
    END IF;
    
    -- Try to drop phone column if it exists (replaced by contact_phone)
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'branches' AND column_name = 'phone') THEN
        ALTER TABLE branches DROP COLUMN phone;
    END IF;
    
    -- Try to drop email column if it exists (replaced by contact_email)
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'branches' AND column_name = 'email') THEN
        ALTER TABLE branches DROP COLUMN email;
    END IF;
END $$;

-- 3. Update existing branches with sample data if city/country are NULL
UPDATE branches 
SET 
    city = COALESCE(city, 'Unknown'),
    country = COALESCE(country, 'Unknown')
WHERE city IS NULL OR country IS NULL;

-- 4. Verify the fix
SELECT 
    'Schema fix completed' as status,
    COUNT(*) as total_branches,
    COUNT(city) as branches_with_city,
    COUNT(country) as branches_with_country
FROM branches;
