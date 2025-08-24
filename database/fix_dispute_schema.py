#!/usr/bin/env python3
"""
Fix Dispute Table Schema Mismatch
This script fixes the column name mismatch between the model and database schema.
"""

import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_dispute_schema():
    """Fix the dispute table schema to match the model"""
    try:
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not found")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if the column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'disputes' 
                AND column_name IN ('reported_by', 'resolved_by')
            """))
            
            existing_columns = [row[0] for row in result]
            logger.info(f"Existing columns in disputes table: {existing_columns}")
            
            if 'resolved_by' in existing_columns and 'reported_by' not in existing_columns:
                # Database has resolved_by but model expects reported_by
                # Rename the column
                logger.info("Renaming 'resolved_by' to 'reported_by'")
                conn.execute(text("ALTER TABLE disputes RENAME COLUMN resolved_by TO reported_by"))
                conn.commit()
                logger.info("✅ Successfully renamed 'resolved_by' to 'reported_by'")
                
            elif 'reported_by' in existing_columns:
                logger.info("✅ Column 'reported_by' already exists")
                
            else:
                # Neither column exists, create reported_by
                logger.info("Creating 'reported_by' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN reported_by UUID REFERENCES users(id)
                """))
                conn.commit()
                logger.info("✅ Successfully created 'reported_by' column")
            
            # Verify the final schema
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'disputes'
                ORDER BY ordinal_position
            """))
            
            logger.info("Final disputes table schema:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to fix dispute schema: {str(e)}")
        return False

def add_dispute_relationships():
    """Add missing foreign key constraints and indexes"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not found")
            return False
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if foreign key constraints exist
            result = conn.execute(text("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'disputes' 
                AND constraint_type = 'FOREIGN KEY'
            """))
            
            existing_constraints = [row[0] for row in result]
            logger.info(f"Existing foreign key constraints: {existing_constraints}")
            
            # Add missing foreign key constraints if they don't exist
            if 'disputes_review_id_fkey' not in existing_constraints:
                logger.info("Adding review_id foreign key constraint")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD CONSTRAINT disputes_review_id_fkey 
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                """))
                conn.commit()
                logger.info("✅ Added review_id foreign key constraint")
            
            if 'disputes_reported_by_fkey' not in existing_constraints:
                logger.info("Adding reported_by foreign key constraint")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD CONSTRAINT disputes_reported_by_fkey 
                    FOREIGN KEY (reported_by) REFERENCES users(id)
                """))
                conn.commit()
                logger.info("✅ Added reported_by foreign key constraint")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add dispute relationships: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Starting dispute schema fix...")
    
    if fix_dispute_schema():
        logger.info("✅ Dispute schema fixed successfully")
        
        if add_dispute_relationships():
            logger.info("✅ Dispute relationships added successfully")
        else:
            logger.error("❌ Failed to add dispute relationships")
    else:
        logger.error("❌ Failed to fix dispute schema")
