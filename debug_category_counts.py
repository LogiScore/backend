#!/usr/bin/env python3
"""
Debug script to investigate inflated category counts
"""

import os
import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.models import FreightForwarder, Review, ReviewCategoryScore
from database.database import get_db

def debug_category_counts():
    """Debug why category counts are inflated"""
    
    print("🔍 Debugging Category Counts")
    print("=" * 50)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Find Kuehne + Nagel
        ff = db.query(FreightForwarder).filter(
            FreightForwarder.name.ilike("%Kuehne%")
        ).first()
        
        if not ff:
            print("❌ Kuehne + Nagel not found")
            return
        
        print(f"✅ Found: {ff.name} (ID: {ff.id})")
        
        # Check total reviews
        total_reviews = db.query(Review).filter(
            Review.freight_forwarder_id == ff.id
        ).count()
        
        print(f"📊 Total reviews in database: {total_reviews}")
        
        # Check reviews by location
        reviews = db.query(Review).filter(
            Review.freight_forwarder_id == ff.id
        ).all()
        
        print(f"📍 Review locations:")
        for review in reviews:
            print(f"   - Review {review.id}: {review.city}, {review.country}")
        
        # Check reviews specifically for Stuttgart, Germany
        stuttgart_reviews = db.query(Review).filter(
            Review.freight_forwarder_id == ff.id,
            Review.city.ilike("%Stuttgart%"),
            Review.country.ilike("%Germany%")
        ).all()
        
        print(f"\n🇩🇪 Stuttgart, Germany reviews: {len(stuttgart_reviews)}")
        for review in stuttgart_reviews:
            print(f"   - Review {review.id}: {review.city}, {review.country}")
        
        # Check category scores
        print(f"\n🔍 Category scores analysis:")
        
        # Count total category score entries
        total_category_entries = db.query(ReviewCategoryScore).join(Review).filter(
            Review.freight_forwarder_id == ff.id
        ).count()
        
        print(f"   Total category score entries: {total_category_entries}")
        
        # Count by category
        category_counts = db.query(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name,
            func.count(ReviewCategoryScore.id).label('question_count'),
            func.count(func.distinct(Review.id)).label('review_count')
        ).join(Review).filter(
            Review.freight_forwarder_id == ff.id
        ).group_by(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name
        ).all()
        
        print(f"\n📋 Category breakdown:")
        for cat in category_counts:
            print(f"   {cat.category_name}:")
            print(f"     - Questions: {cat.question_count}")
            print(f"     - Reviews: {cat.review_count}")
        
        # Check if there are multiple reviews with same category scores
        print(f"\n🔍 Detailed review analysis:")
        for review in reviews:
            print(f"\n   Review {review.id}:")
            category_scores = db.query(ReviewCategoryScore).filter(
                ReviewCategoryScore.review_id == review.id
            ).all()
            
            for cs in category_scores:
                print(f"     - {cs.category_name}: Rating {cs.rating}, Weight {cs.weight}")
        
        # Test the SQL query from the route handler
        print(f"\n🧪 Testing route handler query:")
        test_query = db.query(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name,
            func.avg(ReviewCategoryScore.rating * ReviewCategoryScore.weight).label('avg_weighted_rating'),
            func.count(func.distinct(Review.id)).label('total_reviews')
        ).join(Review, ReviewCategoryScore.review_id == Review.id).filter(
            Review.freight_forwarder_id == ff.id
        ).group_by(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name
        )
        
        test_results = test_query.all()
        print(f"   Query results:")
        for result in test_results:
            print(f"     {result.category_name}: {result.total_reviews} reviews, avg rating {result.avg_weighted_rating}")
        
        # Test with location filtering
        print(f"\n🧪 Testing route handler query WITH location filtering:")
        test_query_filtered = db.query(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name,
            func.avg(ReviewCategoryScore.rating * ReviewCategoryScore.weight).label('avg_weighted_rating'),
            func.count(func.distinct(Review.id)).label('total_reviews')
        ).join(Review, ReviewCategoryScore.review_id == Review.id).filter(
            Review.freight_forwarder_id == ff.id,
            Review.city.ilike("%Stuttgart%"),
            Review.country.ilike("%Germany%")
        ).group_by(
            ReviewCategoryScore.category_id,
            ReviewCategoryScore.category_name
        )
        
        test_results_filtered = test_query_filtered.all()
        print(f"   Query results (Stuttgart, Germany):")
        for result in test_results_filtered:
            print(f"     {result.category_name}: {result.total_reviews} reviews, avg rating {result.avg_weighted_rating}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_category_counts()
