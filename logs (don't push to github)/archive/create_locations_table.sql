-- Create locations table for LogiScore
-- Run this in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    "UUID" VARCHAR(50) UNIQUE NOT NULL,
    "Location" VARCHAR(500) NOT NULL,
    "City" VARCHAR(200),
    "State" VARCHAR(200),
    "Country" VARCHAR(200) NOT NULL,
    "Region" VARCHAR(200),
    "Subregion" VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for fast searching
CREATE INDEX IF NOT EXISTS idx_locations_uuid ON locations("UUID");
CREATE INDEX IF NOT EXISTS idx_locations_city ON locations("City");
CREATE INDEX IF NOT EXISTS idx_locations_country ON locations("Country");
CREATE INDEX IF NOT EXISTS idx_locations_region ON locations("Region");
CREATE INDEX IF NOT EXISTS idx_locations_state ON locations("State");
CREATE INDEX IF NOT EXISTS idx_locations_location ON locations("Location");
CREATE INDEX IF NOT EXISTS idx_locations_city_country ON locations("City", "Country");

-- Verify table creation
SELECT 'Locations table created successfully!' as status;

-- Show table structure (run this separately in psql if needed)
-- \d locations;
