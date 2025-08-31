# LogiScore Backend: shipment_reference Migration

## **Problem Summary**

The LogiScore backend was missing the `shipment_reference` column in the `reviews` table, causing shipment reference data to be lost even though the frontend was collecting and sending it properly.

### **Current Status**
- ✅ **Frontend**: Fully implemented and sending shipment reference
- ✅ **API Interface**: Properly defined with shipment reference field  
- ❌ **Backend Database**: Missing shipment reference column
- ❌ **Backend Model**: Missing shipment reference field
- ❌ **Backend API**: Not handling shipment reference storage

## **Solution Overview**

This migration adds the missing `shipment_reference` column to the `reviews` table and updates all necessary backend components to handle this field.

## **Files Modified**

### **1. Database Model** (`database/models.py`)
- Added `shipment_reference = Column(String(255), nullable=True)` to the Review model

### **2. API Models** (`routes/reviews.py`)
- Added `shipment_reference: Optional[str] = None` to `ReviewCreate` model
- Added `shipment_reference: Optional[str]` to `ReviewResponse` model
- Updated review creation logic to store `shipment_reference` from request data

### **3. Migration Scripts**
- **Python Migration**: `database/migrate_shipment_reference.py` (comprehensive migration script)
- **SQL Migration**: `database/add_shipment_reference.sql` (simple SQL script for Supabase)

## **Migration Options**

### **Option 1: Python Migration Script (Recommended)**
```bash
cd database
python migrate_shipment_reference.py
```

**Requirements:**
- Python 3.7+
- `psycopg2` package
- `DATABASE_URL` environment variable set
- Database connection permissions

**Features:**
- Comprehensive error handling
- Schema verification
- Automatic rollback on failure
- Detailed logging

### **Option 2: Direct SQL in Supabase**
1. Open your Supabase dashboard
2. Go to SQL Editor
3. Copy and paste the contents of `database/add_shipment_reference.sql`
4. Execute the script

**Features:**
- Simple and direct
- No additional dependencies
- Immediate execution
- Built-in verification queries

## **Migration Steps**

### **Step 1: Run Database Migration**
Choose one of the migration options above to add the column to your database.

### **Step 2: Deploy Backend Code Changes**
The backend code changes are already implemented in this migration:
- Updated database model
- Updated API models  
- Updated review creation logic

### **Step 3: Verify Migration**
After running the migration, verify that:
1. The `shipment_reference` column exists in the `reviews` table
2. The column is nullable (VARCHAR(255))
3. An index was created on the column for performance

## **Database Schema Changes**

### **Before Migration**
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    user_id UUID,
    freight_forwarder_id UUID NOT NULL,
    -- ... other existing columns ...
    -- NO shipment_reference column
);
```

### **After Migration**
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY,
    user_id UUID,
    freight_forwarder_id UUID NOT NULL,
    -- ... other existing columns ...
    shipment_reference VARCHAR(255) NULL,  -- NEW COLUMN
    -- ... other existing columns ...
);

-- New index for performance
CREATE INDEX idx_reviews_shipment_reference ON reviews(shipment_reference);
```

## **API Changes**

### **ReviewCreate Model**
```python
class ReviewCreate(BaseModel):
    freight_forwarder_id: UUID
    location_id: Union[UUID, str]
    review_type: str = "general"
    is_anonymous: bool = False
    review_weight: float = 1.0
    category_ratings: List[CategoryRating]
    aggregate_rating: float
    weighted_rating: float
    shipment_reference: Optional[str] = None  # NEW FIELD
```

### **ReviewResponse Model**
```python
class ReviewResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    freight_forwarder_id: UUID
    location_id: UUID
    city: Optional[str]
    country: Optional[str]
    review_type: str
    is_anonymous: bool
    review_weight: float
    aggregate_rating: float
    weighted_rating: float
    total_questions_rated: int
    shipment_reference: Optional[str]  # NEW FIELD
    created_at: datetime
```

## **Testing the Migration**

### **1. Verify Database Schema**
```sql
-- Check if column exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'reviews' AND column_name = 'shipment_reference';

-- View complete table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'reviews' 
ORDER BY ordinal_position;
```

### **2. Test API Endpoint**
Create a test review with shipment reference:
```json
{
  "freight_forwarder_id": "uuid-here",
  "location_id": "location-uuid-or-name",
  "review_type": "general",
  "is_anonymous": false,
  "review_weight": 1.0,
  "category_ratings": [...],
  "aggregate_rating": 3.5,
  "weighted_rating": 3.5,
  "shipment_reference": "SHIP-12345"
}
```

### **3. Verify Data Storage**
Check that the shipment reference is stored:
```sql
SELECT id, shipment_reference, created_at 
FROM reviews 
WHERE shipment_reference IS NOT NULL 
ORDER BY created_at DESC 
LIMIT 5;
```

## **Rollback Plan**

If you need to rollback the migration:

### **Remove Column**
```sql
-- Remove the index first
DROP INDEX IF EXISTS idx_reviews_shipment_reference;

-- Remove the column
ALTER TABLE reviews DROP COLUMN IF EXISTS shipment_reference;
```

### **Revert Code Changes**
- Remove `shipment_reference` field from `ReviewCreate` and `ReviewResponse` models
- Remove `shipment_reference` from Review object creation
- Remove `shipment_reference` from database model

## **Performance Considerations**

- **Index**: An index is automatically created on `shipment_reference` for efficient queries
- **Nullable**: The column is nullable, so it won't affect existing reviews
- **Size**: VARCHAR(255) provides adequate space for most shipment references
- **Storage**: Minimal storage impact as the field is optional

## **Security Considerations**

- **Input Validation**: The field accepts any string up to 255 characters
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Access Control**: Subject to existing review creation permissions

## **Monitoring and Maintenance**

### **Post-Migration Checks**
1. Monitor review creation for any errors
2. Verify shipment references are being stored correctly
3. Check database performance with the new index

### **Long-term Considerations**
- Consider adding validation rules for shipment reference format
- Monitor storage usage if shipment references become very long
- Evaluate if additional indexes are needed based on query patterns

## **Support and Troubleshooting**

### **Common Issues**

1. **Column Already Exists Error**
   - The migration scripts handle this gracefully
   - Check if the column was added in a previous migration

2. **Permission Denied Error**
   - Ensure your database user has ALTER TABLE permissions
   - Check if you're connected to the correct database

3. **Connection Issues**
   - Verify DATABASE_URL is correct
   - Check network connectivity to your database

### **Getting Help**
- Check the migration logs for detailed error messages
- Verify database connection and permissions
- Review the migration script output for any warnings

## **Conclusion**

This migration completes the shipment reference functionality by:
1. Adding the missing database column
2. Updating the backend models and API
3. Ensuring data persistence from frontend to database

After running this migration, the LogiScore system will properly store and retrieve shipment references, completing the 50% implementation gap and enabling full shipment tracking functionality.
