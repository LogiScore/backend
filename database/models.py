from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UUID, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from database.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=False, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    company_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # For email/password auth
    reset_token = Column(String(255), nullable=True)  # For password reset
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)  # For password reset
    verification_code = Column(String(6), nullable=True)  # For email verification
    verification_code_expires = Column(DateTime(timezone=True), nullable=True)  # For email verification
    user_type = Column(String(20), default='shipper')
    subscription_tier = Column(String(20), default='free')
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Subscription management fields
    subscription_start_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    auto_renew_enabled = Column(Boolean, default=False)
    payment_method_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    last_billing_date = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    subscription_status = Column(String(20), default='active')  # active, past_due, canceled, expired, trial
    
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    reported_disputes = relationship("Dispute", foreign_keys="Dispute.reported_by", back_populates="reporter")
    review_subscriptions = relationship("ReviewSubscription", back_populates="user")
    review_notifications = relationship("ReviewNotification", back_populates="user")

class FreightForwarder(Base):
    __tablename__ = "freight_forwarders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    logo_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # Keep this column
    headquarters_country = Column(String(255), nullable=True)  # Keep this column
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Updated model with hybrid properties for calculated ratings
    
    # Relationships
    reviews = relationship("Review", back_populates="freight_forwarder")
    review_subscriptions = relationship("ReviewSubscription", back_populates="freight_forwarder")
    
    @hybrid_property
    def average_rating(self):
        """Calculate average rating from reviews.aggregate_rating"""
        if not self.reviews:
            return 0.0
        
        # Use the aggregate_rating field from reviews
        total_rating = sum(review.aggregate_rating or 0 for review in self.reviews if review.aggregate_rating is not None)
        valid_reviews = sum(1 for review in self.reviews if review.aggregate_rating is not None)
        
        if valid_reviews == 0:
            return 0.0
        
        return total_rating / valid_reviews
    
    @hybrid_property
    def review_count(self):
        """Get total number of review submissions"""
        return len(self.reviews) if self.reviews else 0
    
    @hybrid_property
    def total_aggregated_score(self):
        """Calculate total aggregated score from all reviews"""
        if not self.reviews:
            return 0.0
        
        # Sum all aggregate_rating values from reviews
        total_score = sum(review.aggregate_rating or 0 for review in self.reviews if review.aggregate_rating is not None)
        return total_score
    
    @hybrid_property
    def weighted_review_count(self):
        """Get weighted review count considering review weights"""
        if not self.reviews:
            return 0.0
        
        # Sum review weights (0.5 for anonymous, 1.0 for authenticated)
        total_weight = sum(review.review_weight or 1.0 for review in self.reviews)
        return total_weight
    
    @hybrid_property
    def category_scores_summary(self):
        """Aggregate category scores from review_category_scores"""
        # Return empty dict to avoid SQLAlchemy mapper conflicts
        # Complex calculation is handled in route handlers
        return {}



class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Changed to nullable for anonymous reviews
    freight_forwarder_id = Column(UUID(as_uuid=True), ForeignKey("freight_forwarders.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=True)  # Removed foreign key constraint to branches table
    city = Column(String(100), nullable=True)  # Added: city from branch for easier querying
    country = Column(String(100), nullable=True)  # Added: country from branch for easier querying
    review_type = Column(String(50), default="general")  # Added: general, import, export, domestic, warehousing
    is_anonymous = Column(Boolean, default=False)
    review_weight = Column(Numeric(3,2), default=1.0)  # Added: 0.5 for anonymous, 1.0 for authenticated
    aggregate_rating = Column(Numeric(3,2), nullable=True)  # Added: calculated from all question ratings
    weighted_rating = Column(Numeric(3,2), nullable=True)  # Added: aggregate_rating * review_weight
    total_questions_rated = Column(Integer, default=0)  # Added: count of questions with ratings > 0
    shipment_reference = Column(String(255), nullable=True)  # Added: shipment reference for tracking
    # Keep existing fields for backward compatibility
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    freight_forwarder = relationship("FreightForwarder", back_populates="reviews")
    category_scores = relationship("ReviewCategoryScore", back_populates="review")
    disputes = relationship("Dispute", back_populates="review")
    notifications = relationship("ReviewNotification", back_populates="review")

class ReviewCategoryScore(Base):
    __tablename__ = "review_category_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(100), nullable=False)  # Added: specific category identifier
    category_name = Column(String(100), nullable=False)  # Added: human-readable category name
    question_id = Column(String(100), nullable=False)  # Added: specific question identifier
    question_text = Column(Text, nullable=False)  # Added: the actual question text
    rating = Column(Integer, nullable=False)  # 0-5 star rating system
    rating_definition = Column(Text, nullable=False)  # Added: what the rating means
    weight = Column(Numeric(3,2), default=1.0)  # Added: question weight (usually 1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Keep existing field for backward compatibility
    category = Column(String(100), nullable=True)  # Legacy field, can be removed later
    score = Column(Float, nullable=True)  # Legacy field, can be removed later
    
    # Relationships
    review = relationship("Review", back_populates="category_scores")

class ReviewQuestion(Base):
    __tablename__ = "review_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(String(100), nullable=False)
    category_name = Column(String(100), nullable=False)
    question_id = Column(String(100), nullable=False, unique=True)
    question_text = Column(Text, nullable=False)
    rating_definitions = Column(JSON, nullable=False)  # JSON object with rating definitions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Dispute(Base):
    __tablename__ = "disputes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default='pending')
    admin_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="disputes")
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="reported_disputes")

class AdCampaign(Base):
    __tablename__ = "ad_campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    freight_forwarder_id = Column(UUID(as_uuid=True), ForeignKey("freight_forwarders.id"), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    ad_type = Column(String(50), nullable=False)  # banner, spotlight, featured
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    budget = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 

class ReviewSubscription(Base):
    __tablename__ = "review_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    freight_forwarder_id = Column(UUID(as_uuid=True), ForeignKey("freight_forwarders.id"), nullable=True)
    location_country = Column(String(100), nullable=True)  # For country-based notifications
    location_city = Column(String(100), nullable=True)  # For city-based notifications
    review_type = Column(String(50), nullable=True)  # general, import, export, domestic, warehousing
    notification_frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="review_subscriptions")
    freight_forwarder = relationship("FreightForwarder", back_populates="review_subscriptions")
    notifications = relationship("ReviewNotification", back_populates="subscription")

class ReviewNotification(Base):
    __tablename__ = "review_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("review_subscriptions.id"), nullable=False)
    notification_type = Column(String(50), default='new_review')  # new_review, review_update, etc.
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="review_notifications")
    review = relationship("Review", back_populates="notifications")
    subscription = relationship("ReviewSubscription", back_populates="notifications") 