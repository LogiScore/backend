-- Add missing columns back to freight_forwarders table
-- This fixes the database compatibility issue with the backend

-- Add description column
ALTER TABLE freight_forwarders 
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add headquarters_country column
ALTER TABLE freight_forwarders 
ADD COLUMN IF NOT EXISTS headquarters_country VARCHAR(255);

-- Add global_rank column
ALTER TABLE freight_forwarders 
ADD COLUMN IF NOT EXISTS global_rank INTEGER;

-- Add is_active column
ALTER TABLE freight_forwarders 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Add updated_at column
ALTER TABLE freight_forwarders 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Add trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger if it doesn't exist
DROP TRIGGER IF EXISTS update_freight_forwarders_updated_at ON freight_forwarders;
CREATE TRIGGER update_freight_forwarders_updated_at
    BEFORE UPDATE ON freight_forwarders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'freight_forwarders' 
ORDER BY ordinal_position;
