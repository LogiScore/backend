#!/usr/bin/env python3
"""
Migration script to convert Locations.csv to database table
Run this script to create the locations table and import CSV data
"""

import pandas as pd
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'logiscore')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"

def create_locations_table(engine):
    """Create the locations table with proper structure and indexes"""
    try:
        with engine.connect() as conn:
            # Create locations table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
                location_name VARCHAR(500) NOT NULL,
                city VARCHAR(200),
                state VARCHAR(200),
                country VARCHAR(200) NOT NULL,
                region VARCHAR(200),
                subregion VARCHAR(200),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
            
            conn.execute(text(create_table_sql))
            
            # Create indexes for fast searching
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_locations_uuid ON locations(uuid);",
                "CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city);",
                "CREATE INDEX IF NOT EXISTS idx_locations_country ON locations(country);",
                "CREATE INDEX IF NOT EXISTS idx_locations_region ON locations(region);",
                "CREATE INDEX IF NOT EXISTS idx_locations_state ON locations(state);",
                "CREATE INDEX IF NOT EXISTS idx_locations_location_name ON locations(location_name);",
                "CREATE INDEX IF NOT EXISTS idx_locations_city_country ON locations(city, country);"
            ]
            
            for index_sql in indexes_sql:
                conn.execute(text(index_sql))
            
            conn.commit()
            logger.info("Locations table and indexes created successfully")
            
    except Exception as e:
        logger.error(f"Error creating locations table: {e}")
        raise

def import_csv_data(engine, csv_path):
    """Import CSV data into the locations table"""
    try:
        # Read CSV file
        logger.info(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Clean and prepare data
        df = df.fillna('')
        
        # Rename columns to match database schema
        df = df.rename(columns={
            'Location': 'location_name',
            'City': 'city',
            'State': 'state',
            'Country': 'country',
            'Region': 'region',
            'Subregion': 'subregion'
        })
        
        logger.info(f"CSV loaded: {len(df)} locations found")
        
        # Import data to database
        with engine.connect() as conn:
            # Clear existing data (if any)
            conn.execute(text("DELETE FROM locations"))
            conn.commit()
            
            # Insert data in batches
            batch_size = 1000
            total_rows = len(df)
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                
                # Prepare data for insertion
                data_to_insert = []
                for _, row in batch.iterrows():
                    data_to_insert.append({
                        'location_name': row['location_name'],
                        'city': row['city'],
                        'state': row['state'],
                        'country': row['country'],
                        'region': row['region'],
                        'subregion': row['subregion']
                    })
                
                # Insert batch
                insert_sql = """
                INSERT INTO locations (location_name, city, state, country, region, subregion)
                VALUES (:location_name, :city, :state, :country, :region, :subregion)
                """
                
                conn.execute(text(insert_sql), data_to_insert)
                conn.commit()
                
                logger.info(f"Imported batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1} ({len(batch)} locations)")
            
            # Verify import
            result = conn.execute(text("SELECT COUNT(*) FROM locations"))
            count = result.scalar()
            logger.info(f"Import complete! Total locations in database: {count}")
            
    except Exception as e:
        logger.error(f"Error importing CSV data: {e}")
        raise

def verify_data(engine):
    """Verify the imported data"""
    try:
        with engine.connect() as conn:
            # Check total count
            result = conn.execute(text("SELECT COUNT(*) FROM locations"))
            total_count = result.scalar()
            logger.info(f"Total locations: {total_count}")
            
            # Check sample data with UUIDs
            result = conn.execute(text("SELECT uuid, location_name, city, state, country FROM locations LIMIT 5"))
            sample_data = result.fetchall()
            
            logger.info("Sample locations with UUIDs:")
            for row in sample_data:
                logger.info(f"  - {row.uuid}: {row.location_name} ({row.city}, {row.state}, {row.country})")
            
            # Check regions
            result = conn.execute(text("SELECT DISTINCT region FROM locations WHERE region != '' ORDER BY region"))
            regions = [row.region for row in result.fetchall()]
            logger.info(f"Available regions: {', '.join(regions)}")
            
            # Check countries
            result = conn.execute(text("SELECT COUNT(DISTINCT country) FROM locations"))
            country_count = result.scalar()
            logger.info(f"Unique countries: {country_count}")
            
            # Verify UUIDs are unique
            result = conn.execute(text("SELECT COUNT(*) as total, COUNT(DISTINCT uuid) as unique_uuids FROM locations"))
            uuid_check = result.fetchone()
            logger.info(f"UUID uniqueness check: {uuid_check.total} total, {uuid_check.unique_uuids} unique UUIDs")
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        raise

def main():
    """Main migration function"""
    try:
        logger.info("Starting locations CSV to database migration...")
        
        # Get database connection
        db_url = get_database_url()
        logger.info(f"Connecting to database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
        
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Find CSV file
        csv_path = Path(__file__).parent / "documentation" / "Locations.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Locations.csv not found at {csv_path}")
        
        # Create table and import data
        create_locations_table(engine)
        import_csv_data(engine, csv_path)
        verify_data(engine)
        
        logger.info("Migration completed successfully! 🎉")
        logger.info("Your locations API will now use the database instead of CSV files.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()
