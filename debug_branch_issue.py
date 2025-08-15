#!/usr/bin/env python3
"""
Debug script to investigate the branch lookup issue
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_branch_issue():
    """Debug the branch lookup issue"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable is required")
        return
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 Investigating branch lookup issue...")
        
        # 1. Check branches table structure
        print("\n1. Branches table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'branches' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 2. Check if branches exist
        print("\n2. Branches in database:")
        cursor.execute("SELECT COUNT(*) as total FROM branches")
        total_branches = cursor.fetchone()['total']
        print(f"  - Total branches: {total_branches}")
        
        if total_branches > 0:
            cursor.execute("""
                SELECT id, name, freight_forwarder_id, city, country, is_active 
                FROM branches 
                LIMIT 5
            """)
            branches = cursor.fetchall()
            for branch in branches:
                print(f"  - {branch['name']} (ID: {branch['id']}, FF: {branch['freight_forwarder_id']}, City: {branch['city']}, Country: {branch['country']})")
        
        # 3. Check freight forwarders
        print("\n3. Freight forwarders in database:")
        cursor.execute("SELECT COUNT(*) as total FROM freight_forwarders")
        total_ff = cursor.fetchone()['total']
        print(f"  - Total freight forwarders: {total_ff}")
        
        if total_ff > 0:
            cursor.execute("SELECT id, name FROM freight_forwarders LIMIT 3")
            ffs = cursor.fetchall()
            for ff in ffs:
                print(f"  - {ff['name']} (ID: {ff['id']})")
        
        # 4. Check branch-freight forwarder relationships
        print("\n4. Branch-Freight Forwarder relationships:")
        cursor.execute("""
            SELECT 
                b.id as branch_id,
                b.name as branch_name,
                b.freight_forwarder_id,
                ff.name as ff_name
            FROM branches b
            LEFT JOIN freight_forwarders ff ON b.freight_forwarder_id = ff.id
            LIMIT 5
        """)
        
        relationships = cursor.fetchall()
        for rel in relationships:
            print(f"  - Branch '{rel['branch_name']}' -> FF '{rel['ff_name']}' (FF ID: {rel['freight_forwarder_id']})")
        
        # 5. Test the specific query that's failing
        print("\n5. Testing the failing query:")
        if total_branches > 0 and total_ff > 0:
            # Get first branch and freight forwarder
            cursor.execute("SELECT id FROM branches LIMIT 1")
            branch_id = cursor.fetchone()['id']
            
            cursor.execute("SELECT id FROM freight_forwarders LIMIT 1")
            ff_id = cursor.fetchone()['id']
            
            print(f"  - Testing with branch_id: {branch_id}")
            print(f"  - Testing with freight_forwarder_id: {ff_id}")
            
            # Test the exact query from the API
            cursor.execute("""
                SELECT * FROM branches 
                WHERE id = %s AND freight_forwarder_id = %s
            """, (branch_id, ff_id))
            
            result = cursor.fetchone()
            if result:
                print(f"  ✅ Query successful: Found branch '{result['name']}'")
            else:
                print(f"  ❌ Query failed: No branch found with these IDs")
                
                # Check if branch exists at all
                cursor.execute("SELECT * FROM branches WHERE id = %s", (branch_id,))
                branch_exists = cursor.fetchone()
                if branch_exists:
                    print(f"  - Branch exists but freight_forwarder_id is: {branch_exists['freight_forwarder_id']}")
                else:
                    print(f"  - Branch with ID {branch_id} doesn't exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_branch_issue()
