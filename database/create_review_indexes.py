#!/usr/bin/env python3
"""
Script to create database indexes for optimal performance of review endpoints.
Run this after implementing the new review endpoints to ensure good performance.
"""

import os
import sys
from sqlalchemy import text
from database.database import get_engine, get_db
from sqlalchemy.orm import Session

def create_review_indexes():
    """Create indexes for the reviews table to optimize query performance"""
    
    # SQL statements for creating indexes
    index_statements = [
        # Index for country filtering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_country 
        ON reviews (country) 
        WHERE country IS NOT NULL AND country != '';
        """,
        
        # Index for city filtering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_city 
        ON reviews (city) 
        WHERE city IS NOT NULL AND city != '';
        """,
        
        # Composite index for city + country filtering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_city_country 
        ON reviews (city, country) 
        WHERE city IS NOT NULL AND city != '' AND country IS NOT NULL AND country != '';
        """,
        
        # Index for freight_forwarder_id filtering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_freight_forwarder_id 
        ON reviews (freight_forwarder_id);
        """,
        
        # Index for active reviews filtering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_is_active 
        ON reviews (is_active) 
        WHERE is_active = true;
        """,
        
        # Index for created_at ordering
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_created_at 
        ON reviews (created_at DESC);
        """,
        
        # Composite index for common query patterns
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_location_active 
        ON reviews (country, city, is_active, created_at DESC) 
        WHERE is_active = true;
        """,
        
        # Index for review_category_scores table (used in search)
        """
        CREATE INDEX IF NOT EXISTS idx_review_category_scores_search 
        ON review_category_scores (question_text, category_name, rating_definition);
        """,
        
        # Index for review_id in category scores (for JOINs)
        """
        CREATE INDEX IF NOT EXISTS idx_review_category_scores_review_id 
        ON review_category_scores (review_id);
        """
    ]
    
    try:
        # Get database engine
        engine = get_engine()
        
        # Create indexes
        with engine.connect() as connection:
            print("Creating database indexes for reviews table...")
            
            for i, statement in enumerate(index_statements, 1):
                try:
                    print(f"Creating index {i}/{len(index_statements)}...")
                    connection.execute(text(statement))
                    connection.commit()
                    print(f"✓ Index {i} created successfully")
                except Exception as e:
                    print(f"⚠ Warning creating index {i}: {e}")
                    # Continue with other indexes even if one fails
                    continue
            
            print("\n✅ Database indexes creation completed!")
            
            # Verify indexes were created
            print("\nVerifying indexes...")
            verify_query = text("""
                SELECT indexname, tablename, indexdef
                FROM pg_indexes 
                WHERE tablename IN ('reviews', 'review_category_scores')
                AND indexname LIKE 'idx_reviews%'
                ORDER BY tablename, indexname;
            """)
            
            result = connection.execute(verify_query)
            indexes = result.fetchall()
            
            if indexes:
                print(f"Found {len(indexes)} indexes:")
                for idx in indexes:
                    print(f"  - {idx[0]} on {idx[1]}")
            else:
                print("No indexes found. This might indicate an issue.")
                
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False
    
    return True

def analyze_table_performance():
    """Analyze table performance and provide recommendations"""
    
    try:
        engine = get_engine()
        
        with engine.connect() as connection:
            print("\n📊 Analyzing table performance...")
            
            # Check table sizes
            size_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE tablename IN ('reviews', 'review_category_scores')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            result = connection.execute(size_query)
            sizes = result.fetchall()
            
            if sizes:
                print("Table sizes:")
                for size in sizes:
                    print(f"  - {size[1]}: {size[2]}")
            
            # Check row counts
            count_query = text("""
                SELECT 
                    'reviews' as table_name,
                    COUNT(*) as row_count
                FROM reviews
                UNION ALL
                SELECT 
                    'review_category_scores' as table_name,
                    COUNT(*) as row_count
                FROM review_category_scores;
            """)
            
            result = connection.execute(count_query)
            counts = result.fetchall()
            
            if counts:
                print("\nRow counts:")
                for count in counts:
                    print(f"  - {count[0]}: {count[1]:,} rows")
            
            # Performance recommendations
            print("\n💡 Performance Recommendations:")
            print("  1. Monitor query performance with EXPLAIN ANALYZE")
            print("  2. Consider partitioning for large tables (>1M rows)")
            print("  3. Regular VACUUM and ANALYZE for optimal performance")
            print("  4. Monitor index usage with pg_stat_user_indexes")
            
    except Exception as e:
        print(f"⚠ Warning analyzing performance: {e}")

def main():
    """Main function to create indexes and analyze performance"""
    
    print("🚀 LogiScore Review Endpoints Database Optimization")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("database/database.py"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Create indexes
    success = create_review_indexes()
    
    if success:
        # Analyze performance
        analyze_table_performance()
        
        print("\n🎉 Database optimization completed successfully!")
        print("\nNext steps:")
        print("  1. Test your review endpoints")
        print("  2. Monitor query performance")
        print("  3. Run the test script: python test_review_endpoints.py")
    else:
        print("\n❌ Database optimization failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
