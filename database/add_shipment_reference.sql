-- LogiScore Database Migration: Add shipment_reference to reviews table
-- This script adds the missing shipment_reference column to the reviews table.
-- Run this directly in your Supabase SQL editor.

-- Check if column already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'reviews' AND column_name = 'shipment_reference'
    ) THEN
        -- Add the shipment_reference column
        ALTER TABLE reviews ADD COLUMN shipment_reference VARCHAR(255) NULL;
        
        -- Add an index for better query performance
        CREATE INDEX idx_reviews_shipment_reference ON reviews(shipment_reference);
        
        RAISE NOTICE 'shipment_reference column added successfully to reviews table';
    ELSE
        RAISE NOTICE 'shipment_reference column already exists in reviews table';
    END IF;
END $$;

-- Verify the column was added
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'reviews' AND column_name = 'shipment_reference';

-- Show the updated table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'reviews' 
ORDER BY ordinal_position;
