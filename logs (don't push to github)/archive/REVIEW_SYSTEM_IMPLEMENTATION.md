# LogiScore Review System Implementation

## 🎯 **Overview**
This document outlines the comprehensive review system that has been implemented in the LogiScore backend to support the new 35-question review format.

## 🏗️ **What Has Been Implemented**

### **1. Database Models Updated (`database/models.py`)**

#### **Review Model (Enhanced)**
- **New Fields Added:**
  - `review_type`: String for review type (general, import, export, domestic, warehousing)
  - `review_weight`: Numeric for review weight (0.5 for anonymous, 1.0 for authenticated)
  - `aggregate_rating`: Numeric for calculated average rating from all questions
  - `weighted_rating`: Numeric for aggregate_rating × review_weight
  - `total_questions_rated`: Integer count of questions with ratings > 0
  
- **Existing Fields Preserved:**
  - `overall_rating`: Changed to nullable for backward compatibility
  - `review_text`: Preserved for backward compatibility
  - All other existing fields maintained

#### **ReviewCategoryScore Model (Completely Redesigned)**
- **New Structure:**
  - `category_id`: Specific category identifier
  - `category_name`: Human-readable category name
  - `question_id`: Specific question identifier
  - `question_text`: The actual question text
  - `rating`: Integer 0-4 star rating
  - `rating_definition`: What the rating means
  - `weight`: Question weight (usually 1.0)
  
- **Legacy Fields Preserved:**
  - `category` and `score` fields kept for backward compatibility

#### **ReviewQuestion Model (New)**
- **Purpose:** Reference table for all 35 review questions
- **Fields:**
  - `category_id` and `category_name`
  - `question_id` (unique identifier)
  - `question_text` (the actual question)
  - `rating_definitions` (JSON object with rating meanings)
  - `is_active` flag for question management

### **2. API Endpoints Created (`routes/reviews.py`)**

#### **POST `/api/reviews`**
- **Purpose:** Submit a new comprehensive review
- **Features:**
  - Supports both authenticated and anonymous reviews
  - Handles all 35 questions across 8 categories
  - Calculates aggregate and weighted ratings
  - Creates detailed category scores for each question

#### **GET `/api/reviews/questions`**
- **Purpose:** Retrieve all review questions for frontend form
- **Response:** Questions grouped by category with rating definitions

#### **GET `/api/reviews/freight-forwarder/{id}`**
- **Purpose:** Get all reviews for a specific company
- **Features:** Ordered by creation date, supports pagination

#### **GET `/api/reviews/{id}`**
- **Purpose:** Get a specific review by ID
- **Features:** Full review details with all question responses

### **3. Authentication Enhancement (`auth/auth.py`)**

#### **New Function: `get_current_user_optional`**
- **Purpose:** Support both authenticated and anonymous reviews
- **Behavior:**
  - Returns user data if valid JWT token provided
  - Returns `None` if no token or invalid token
  - Enables anonymous review submission

### **4. Main App Integration (`main.py`)**
- Reviews router already included and configured
- No changes needed to existing configuration

## 🔧 **Technical Implementation Details**

### **Data Flow for Review Submission**
1. **Frontend** sends review data with all 35 question ratings
2. **Backend** validates freight forwarder exists
3. **Backend** creates main review record
4. **Backend** creates individual category scores for each question
5. **Backend** calculates aggregate and weighted ratings
6. **Response** includes complete review with ID

### **Rating System**
- **Scale:** 0-4 stars (0 = Not applicable, 1-4 = Poor to Excellent)
- **Weighting:** Anonymous reviews count 50%, authenticated reviews count 100%
- **Calculation:** Aggregate rating from all questions, then weighted by user type

### **Database Relationships**
- **Review** → **ReviewCategoryScore** (one-to-many)
- **Review** → **ReviewQuestion** (many-to-many via category scores)
- **Review** → **FreightForwarder** (many-to-one)
- **Review** → **User** (many-to-one, nullable for anonymous)

## 🚀 **Next Steps for Frontend Integration**

### **1. Update Frontend API Client**
```typescript
// In your frontend api.ts, add:
async createReview(reviewData: ReviewCreate): Promise<ReviewResponse> {
  const response = await this.client.post('/api/reviews', reviewData);
  return response.data;
}

async getReviewQuestions(): Promise<Category[]> {
  const response = await this.client.get('/api/reviews/questions');
  return response.data;
}
```

### **2. Modify Review Form Submission**
```typescript
// Replace console.log with actual API call:
const response = await apiClient.createReview(reviewData);
// Handle success/error appropriately
```

### **3. Load Questions Dynamically**
```typescript
// In your reviews page, load questions from API instead of hardcoded:
onMount(async () => {
  try {
    const questions = await apiClient.getReviewQuestions();
    reviewCategories = questions; // Update your local state
  } catch (error) {
    console.error('Failed to load review questions:', error);
  }
});
```

## 🧪 **Testing the Implementation**

### **1. Start Your Backend Server**
```bash
cd logiscore-backend
uvicorn main:app --reload
```

### **2. Run the Test Script**
```bash
python test_reviews.py
```

### **3. Test Endpoints Manually**
- Use Postman or curl to test each endpoint
- Verify database tables are created correctly
- Check that RLS policies are working

## 📋 **Database Migration Requirements**

Before testing, ensure you've run the Supabase SQL scripts:
1. **Create tables** with the new schema
2. **Populate** `review_questions` table with all 35 questions
3. **Enable RLS** and create appropriate policies

## ✅ **What's Working Now**
- ✅ Complete backend API structure
- ✅ Database models for comprehensive reviews
- ✅ Support for both authenticated and anonymous reviews
- ✅ 35-question review system architecture
- ✅ Rating calculation and weighting system
- ✅ Backward compatibility with existing code

## 🎯 **Ready for Frontend Integration**
The backend is now fully prepared to handle the comprehensive review system. The next step is to update your frontend to call these new endpoints instead of just logging to the console.
