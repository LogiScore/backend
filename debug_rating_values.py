#!/usr/bin/env python3
"""
Debug script to investigate rating values and category score calculations
"""

import os
import sys
import uuid
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.models import FreightForwarder, Review, ReviewCategoryScore
from database.database import get_db

def debug_rating_values():
    """Debug rating values and category score calculations"""
    
    print("🔍 Debugging Rating Values and Category Score Calculations")
    print("=" * 70)
    
    try:
        # Get database session
        db = next(get_db())
        
        # List all freight forwarders to see what's available
        print("📋 Available Freight Forwarders:")
        all_ffs = db.query(FreightForwarder.name).limit(10).all()
        for ff_name in all_ffs:
            print(f"   - {ff_name[0]}")
        
        print("\n" + "=" * 70)
        
        # Find TOLL company using the ID from the logs
        toll_id = uuid.UUID("0428f361-b3af-44fb-8a26-47148df3c473")
        ff = db.query(FreightForwarder).filter(
            FreightForwarder.id == toll_id
        ).first()
        
        if not ff:
            print("❌ TOLL not found")
            return
        
        print(f"✅ Found: {ff.name} (ID: {ff.id})")
        
        # Check reviews for TOLL
        reviews = db.query(Review).filter(
            Review.freight_forwarder_id == ff.id
        ).all()
        
        print(f"📊 Total reviews for TOLL: {len(reviews)}")
        
        # Check reviews by location
        for review in reviews:
            print(f"\n📍 Review {review.id}:")
            print(f"   - City: {review.city}")
            print(f"   - Country: {review.country}")
            print(f"   - Aggregate Rating: {review.aggregate_rating}")
            print(f"   - Weighted Rating: {review.weighted_rating}")
            print(f"   - Total Questions Rated: {review.total_questions_rated}")
            
            # Get category scores for this review
            category_scores = db.query(ReviewCategoryScore).filter(
                ReviewCategoryScore.review_id == review.id
            ).all()
            
            print(f"   - Category Scores: {len(category_scores)} entries")
            
            for cs in category_scores:
                print(f"     - {cs.category_name}:")
                print(f"       * Rating: {cs.rating} (type: {type(cs.rating)})")
                print(f"       * Weight: {cs.weight} (type: {type(cs.weight)})")
                print(f"       * Question ID: {cs.question_id}")
                print(f"       * Question Text: {cs.question_text[:50]}...")
                print(f"       * Rating Definition: {cs.rating_definition[:50]}...")
        
        # Check if there are any reviews in Altona, Germany
        print(f"\n🇩🇪 Checking Altona, Germany reviews:")
        altona_reviews = db.query(Review).filter(
            Review.freight_forwarder_id == ff.id,
            Review.city.ilike("%Altona%"),
            Review.country.ilike("%Germany%")
        ).all()
        
        print(f"   Found {len(altona_reviews)} reviews in Altona, Germany")
        
        for review in altona_reviews:
            print(f"\n   📍 Altona Review {review.id}:")
            print(f"      - Aggregate Rating: {review.aggregate_rating}")
            print(f"      - Weighted Rating: {review.weighted_rating}")
            
            # Get category scores for this specific review
            category_scores = db.query(ReviewCategoryScore).filter(
                ReviewCategoryScore.review_id == review.id
            ).all()
            
            print(f"      - Category Scores: {len(category_scores)} entries")
            
            for cs in category_scores:
                print(f"        - {cs.category_name}:")
                print(f"          * Rating: {cs.rating} (type: {type(cs.rating)})")
                print(f"          * Weight: {cs.weight} (type: {type(cs.weight)})")
                print(f"          * Raw Rating Value: {repr(cs.rating)}")
                print(f"          * Raw Weight Value: {repr(cs.weight)}")
        
        # Test the calculation logic step by step
        print(f"\n🧪 Testing Calculation Logic Step by Step:")
        
        if altona_reviews:
            review = altona_reviews[0]
            print(f"   Using review {review.id} for calculation test")
            
            category_totals = {}
            category_review_counts = {}
            category_names = {}
            
            for category_score in review.category_scores:
                category_id = category_score.category_id
                category_name = category_score.category_name
                
                print(f"\n     Processing {category_name}:")
                print(f"       - Rating: {category_score.rating}")
                print(f"       - Weight: {category_score.weight}")
                
                if category_id not in category_totals:
                    category_totals[category_id] = 0
                    category_review_counts[category_id] = set()
                    category_names[category_id] = category_name
                
                # Test the weighted rating calculation
                rating = category_score.rating or 0
                weight = category_score.weight or 1.0
                weighted_rating = rating * weight
                
                print(f"       - Raw Rating: {rating}")
                print(f"       - Raw Weight: {weight}")
                print(f"       - Weighted Rating: {weighted_rating}")
                
                category_totals[category_id] += weighted_rating
                category_review_counts[category_id].add(review.id)
                
                print(f"       - Running Total: {category_totals[category_id]}")
            
            # Calculate averages
            print(f"\n     Final Calculations:")
            for category_id in category_totals:
                if len(category_review_counts[category_id]) > 0:
                    average = category_totals[category_id] / len(category_review_counts[category_id])
                    print(f"       - {category_names[category_id]}: {average}")
        
        # Check if there are any rating issues in the database
        print(f"\n🔍 Database Rating Analysis:")
        
        # Check for null ratings
        null_ratings = db.query(ReviewCategoryScore).filter(
            ReviewCategoryScore.rating.is_(None)
        ).count()
        print(f"   Null ratings: {null_ratings}")
        
        # Check for zero ratings
        zero_ratings = db.query(ReviewCategoryScore).filter(
            ReviewCategoryScore.rating == 0
        ).count()
        print(f"   Zero ratings: {rating}")
        
        # Check rating range
        min_rating = db.query(func.min(ReviewCategoryScore.rating)).scalar()
        max_rating = db.query(func.max(ReviewCategoryScore.rating)).scalar()
        print(f"   Rating range: {min_rating} to {max_rating}")
        
        # Check weight range
        min_weight = db.query(func.min(ReviewCategoryScore.weight)).scalar()
        max_weight = db.query(func.max(ReviewCategoryScore.weight)).scalar()
        print(f"   Weight range: {min_weight} to {max_weight}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rating_values()
