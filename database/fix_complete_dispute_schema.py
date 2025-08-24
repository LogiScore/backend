#!/usr/bin/env python3
"""
Fix Complete Dispute Table Schema
This script fixes all missing columns in the disputes table to match the current model.
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

def fix_complete_dispute_schema():
    """Fix the complete dispute table schema to match the model"""
    try:
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not found")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check current schema
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'disputes'
                ORDER BY ordinal_position
            """))
            
            current_columns = {row[0]: row[1] for row in result}
            logger.info(f"Current columns in disputes table: {list(current_columns.keys())}")
            
            # Expected columns from the model
            expected_columns = {
                'id': 'UUID',
                'review_id': 'UUID', 
                'reported_by': 'UUID',
                'reason': 'VARCHAR(255)',
                'description': 'TEXT',
                'status': 'VARCHAR(50)',
                'admin_notes': 'TEXT',
                'resolved_at': 'DATETIME',
                'created_at': 'DATETIME',
                'updated_at': 'DATETIME'
            }
            
            # Fix reported_by column if needed
            if 'resolved_by' in current_columns and 'reported_by' not in current_columns:
                logger.info("Renaming 'resolved_by' to 'reported_by'")
                conn.execute(text("ALTER TABLE disputes RENAME COLUMN resolved_by TO reported_by"))
                logger.info("✅ Successfully renamed 'resolved_by' to 'reported_by'")
            elif 'reported_by' not in current_columns:
                logger.info("Creating 'reported_by' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN reported_by UUID REFERENCES users(id)
                """))
                logger.info("✅ Successfully created 'reported_by' column")
            
            # Fix reason column if missing
            if 'reason' not in current_columns:
                logger.info("Creating 'reason' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN reason VARCHAR(255) NOT NULL DEFAULT 'General Dispute'
                """))
                logger.info("✅ Successfully created 'reason' column")
            
            # Fix description column if missing
            if 'description' not in current_columns:
                logger.info("Creating 'description' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN description TEXT
                """))
                logger.info("✅ Successfully created 'description' column")
            
            # Fix admin_notes column if missing
            if 'admin_notes' not in current_columns:
                logger.info("Creating 'admin_notes' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN admin_notes TEXT
                """))
                logger.info("✅ Successfully created 'admin_notes' column")
            
            # Fix resolved_at column if missing
            if 'resolved_at' not in current_columns:
                logger.info("Creating 'resolved_at' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN resolved_at TIMESTAMP WITH TIME ZONE
                """))
                logger.info("✅ Successfully created 'resolved_at' column")
            
            # Fix updated_at column if missing
            if 'updated_at' not in current_columns:
                logger.info("Creating 'updated_at' column")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                """))
                logger.info("✅ Successfully created 'updated_at' column")
            
            # Commit all changes
            conn.commit()
            
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
                logger.info("✅ Added review_id foreign key constraint")
            
            if 'disputes_reported_by_fkey' not in existing_constraints:
                logger.info("Adding reported_by foreign key constraint")
                conn.execute(text("""
                    ALTER TABLE disputes 
                    ADD CONSTRAINT disputes_reported_by_fkey 
                    FOREIGN KEY (reported_by) REFERENCES users(id)
                """))
                logger.info("✅ Added reported_by foreign key constraint")
            
            # Commit all changes
            conn.commit()
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to add dispute relationships: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Starting complete dispute schema fix...")
    
    if fix_complete_dispute_schema():
        logger.info("✅ Complete dispute schema fixed successfully")
        
        if add_dispute_relationships():
            logger.info("✅ Dispute relationships added successfully")
        else:
            logger.error("❌ Failed to add dispute relationships")
    else:
        logger.error("❌ Failed to fix dispute schema")
