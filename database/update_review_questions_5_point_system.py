#!/usr/bin/env python3
"""
Update review questions table to reflect the proper 5-point rating system.
This script updates the review_questions table with the correct questions and rating definitions
from the LogiScore Review Questions document.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Try different environment variable names
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Try constructing from individual components
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'logiscore')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        if db_password:
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            database_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    return database_url

def get_review_questions_data():
    """Get the review questions data based on the LogiScore Review Questions document"""
    return [
        # 1. Responsiveness
        {
            "category_id": "responsiveness",
            "category_name": "Responsiveness",
            "question_id": "resp_001",
            "question_text": "Acknowledges receipt of requests (for quotation or information) within 30 minutes (even if full response comes later)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "responsiveness",
            "category_name": "Responsiveness",
            "question_id": "resp_002",
            "question_text": "Provides clear estimated response time if immediate resolution is not possible",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "responsiveness",
            "category_name": "Responsiveness",
            "question_id": "resp_003",
            "question_text": "Responds within 6 hours to rate requests to/from locations within the same region",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "responsiveness",
            "category_name": "Responsiveness",
            "question_id": "resp_004",
            "question_text": "Responds within 24 hours to rate requests to/from other regions (e.g. Asia to US, US to Europe)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "responsiveness",
            "category_name": "Responsiveness",
            "question_id": "resp_005",
            "question_text": "Responds to emergency requests (e.g., urgent shipment delay, customs issues) within 30 minutes",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        
        # 2. Shipment Management
        {
            "category_id": "shipment_management",
            "category_name": "Shipment Management",
            "question_id": "ship_001",
            "question_text": "Proactively sends shipment milestones (e.g., pickup, departure, arrival, delivery) without being asked",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "shipment_management",
            "category_name": "Shipment Management",
            "question_id": "ship_002",
            "question_text": "Sends pre-alerts before vessel ETA",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "shipment_management",
            "category_name": "Shipment Management",
            "question_id": "ship_003",
            "question_text": "Provides POD (proof of delivery) within 24 hours of delivery",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "shipment_management",
            "category_name": "Shipment Management",
            "question_id": "ship_004",
            "question_text": "Proactively notifies delays or disruptions",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "shipment_management",
            "category_name": "Shipment Management",
            "question_id": "ship_005",
            "question_text": "Offers recovery plans in case of delays or missed transshipments",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        
        # 3. Documentation
        {
            "category_id": "documentation",
            "category_name": "Documentation",
            "question_id": "doc_001",
            "question_text": "Issues draft B/L or HAWB within 24 hours of cargo departure",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "documentation",
            "category_name": "Documentation",
            "question_id": "doc_002",
            "question_text": "Sends final invoices within 48 hours of shipment completion",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "documentation",
            "category_name": "Documentation",
            "question_id": "doc_003",
            "question_text": "Ensures documentation is accurate and complete on first submission",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "documentation",
            "category_name": "Documentation",
            "question_id": "doc_004",
            "question_text": "Final invoice matches quotation (no hidden costs and all calculations and volumes are correct)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        
        # 4. Customer Experience
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_001",
            "question_text": "Follows up on pending issues without the need for reminders",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_002",
            "question_text": "Rectifies documentation (shipping documents and invoices/credit notes) within 48 hours",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_003",
            "question_text": "Provides named contact person(s) for operations and customer service",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_004",
            "question_text": "Offers single point of contact for issue escalation",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_005",
            "question_text": "Replies in professional tone, avoids jargon unless relevant",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Never",
                "2": "Seldom",
                "3": "Usually",
                "4": "Most of the time",
                "5": "Every time"
            }
        },
        {
            "category_id": "customer_experience",
            "category_name": "Customer Experience",
            "question_id": "cust_006",
            "question_text": "Customer Service and Operations have vertical specific knowledge (e.g. Chemicals, Pharma, Hightech)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "None",
                "2": "Some",
                "3": "Aware but not knowledgable",
                "4": "Knowledgable",
                "5": "Very knowledgable"
            }
        },
        
        # 5. Technology Process
        {
            "category_id": "technology_process",
            "category_name": "Technology Process",
            "question_id": "tech_001",
            "question_text": "Offers online track-and-trace",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "Only via phone, messaging or email",
                "3": "Provided via the website, however data doesn't seem dynamic nor current",
                "4": "Provided via the website and data seems dynamic and current",
                "5": "Provided via web or mobile app, data is dynamic and current, able to schedule reports and triggered by milestones"
            }
        },
        {
            "category_id": "technology_process",
            "category_name": "Technology Process",
            "question_id": "tech_002",
            "question_text": "Has an online document portal to access shipment documents and invoices",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "Limited availability - only for selected customers",
                "3": "Basic availability - documents are not current or complete",
                "4": "On demand access - documents are available on scheduled basis",
                "5": "Available via web or mobile app on demand, with download and notification options"
            }
        },
        {
            "category_id": "technology_process",
            "category_name": "Technology Process",
            "question_id": "tech_003",
            "question_text": "Integrates with customer systems (e.g., EDI/API) where required",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "Limited availability - only for selected customers",
                "3": "Available however Forwarder lacks experience; project management and frequent technical issues",
                "4": "Standard capability - available and able to implement effortlessly",
                "5": "Advanced integration capabilities offering mature, flexible and secure integration services to a variety of ERP/TMS/WMS systems"
            }
        },
        {
            "category_id": "technology_process",
            "category_name": "Technology Process",
            "question_id": "tech_004",
            "question_text": "Able to provides regular reporting (e.g., weekly shipment report, KPI report)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "Reporting is manual",
                "3": "Limited available - only select customers",
                "4": "Standardized access for all customers. Available and setup either by provider or via a web portal.",
                "5": "Advances, customizable reporting via interactive dashboards on the web or mobile devices with advances analytical functions"
            }
        },
        
        # 6. Reliability & Execution
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_001",
            "question_text": "On-time pickup",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Seldom",
                "2": "Occasionally",
                "3": "Usually",
                "4": "Often",
                "5": "Always"
            }
        },
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_002",
            "question_text": "Shipped as promised",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Seldom",
                "2": "Occasionally",
                "3": "Usually",
                "4": "Often",
                "5": "Always"
            }
        },
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_003",
            "question_text": "On-time delivery",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Seldom",
                "2": "Occasionally",
                "3": "Usually",
                "4": "Often",
                "5": "Always"
            }
        },
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_004",
            "question_text": "Compliance with clients' SOP",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Does not define SOP's and has no quality system (ISO 9001)",
                "2": "Follows quality system, SOP's for large customers",
                "3": "Defines and usually follows",
                "4": "Defines and follows most of the time",
                "5": "Always follows clients' SOP"
            }
        },
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_005",
            "question_text": "Customs declaration errors",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Very often",
                "2": "Frequent errors",
                "3": "Occasional errors",
                "4": "Seldom errors",
                "5": "No errors"
            }
        },
        {
            "category_id": "reliability_execution",
            "category_name": "Reliability & Execution",
            "question_id": "rel_006",
            "question_text": "Claims ratio (number of claims / total shipments)",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Often",
                "2": "Regularly",
                "3": "Occasionally",
                "4": "Rarely",
                "5": "Never"
            }
        },
        
        # 7. Proactivity & Insight
        {
            "category_id": "proactivity_insight",
            "category_name": "Proactivity & Insight",
            "question_id": "pro_001",
            "question_text": "Provides trends relating to rates, capacities, carriers, customs and geopolitical issues that might impact global trade and the client and mitigation options the client could consider",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not able to provide any information",
                "2": "Provides some information when requested",
                "3": "Provides detailed updates when requested",
                "4": "Proactively provides regular periodic updates",
                "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
            }
        },
        {
            "category_id": "proactivity_insight",
            "category_name": "Proactivity & Insight",
            "question_id": "pro_002",
            "question_text": "Notifies customer of upcoming GRI or BAF changes in advance and mitigation options",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not able to provide any information",
                "2": "Provides some information when requested",
                "3": "Provides detailed updates when requested",
                "4": "Proactively provides regular periodic updates",
                "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
            }
        },
        {
            "category_id": "proactivity_insight",
            "category_name": "Proactivity & Insight",
            "question_id": "pro_003",
            "question_text": "Provides suggestions for consolidation, better routings, or mode shifts",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not able to provide any information",
                "2": "Provides some information when requested",
                "3": "Provides detailed updates when requested",
                "4": "Proactively provides regular periodic updates",
                "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
            }
        },
        
        # 8. After Hours Support
        {
            "category_id": "after_hours_support",
            "category_name": "After Hours Support",
            "question_id": "after_001",
            "question_text": "Has 24/7 support or provides emergency contact for after-hours escalation",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "Helpdesk/control tower only responds during working hours",
                "3": "Provides a helpdesk/control tower however responds only after 2-4 hours",
                "4": "Provides a helpdesk/control tower that responds within 1-2 hours",
                "5": "Provides 24/7 helpdesk/control tower"
            }
        },
        {
            "category_id": "after_hours_support",
            "category_name": "After Hours Support",
            "question_id": "after_002",
            "question_text": "Weekend or holiday contact provided in advance for critical shipments",
            "rating_definitions": {
                "0": "Not applicable",
                "1": "Not available",
                "2": "No contact available on weekends or holidays",
                "3": "Contact responds within 2-4 hours",
                "4": "Contact responds within 1-2 hours",
                "5": "Provides 24/7 contact"
            }
        }
    ]

def update_review_questions():
    """Update the review_questions table with the proper 5-point system"""
    try:
        database_url = get_database_url()
        if not database_url:
            logger.error("No database URL found in environment variables")
            return False
        
        logger.info(f"Connecting to database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Clear existing questions
                logger.info("Clearing existing review questions...")
                conn.execute(text("DELETE FROM review_questions"))
                
                # Insert new questions with 5-point system
                questions_data = get_review_questions_data()
                logger.info(f"Inserting {len(questions_data)} review questions...")
                
                for question in questions_data:
                    insert_query = text("""
                        INSERT INTO review_questions (
                            category_id, category_name, question_id, question_text, 
                            rating_definitions, is_active
                        ) VALUES (
                            :category_id, :category_name, :question_id, :question_text,
                            :rating_definitions, :is_active
                        )
                    """)
                    
                    conn.execute(insert_query, {
                        'category_id': question['category_id'],
                        'category_name': question['category_name'],
                        'question_id': question['question_id'],
                        'question_text': question['question_text'],
                        'rating_definitions': question['rating_definitions'],
                        'is_active': True
                    })
                    
                    logger.info(f"✓ Inserted question: {question['question_id']} - {question['category_name']}")
                
                # Commit the transaction
                trans.commit()
                logger.info("✓ All review questions updated successfully")
                
                # Verify the update
                result = conn.execute(text("SELECT COUNT(*) FROM review_questions WHERE is_active = true"))
                count = result.scalar()
                logger.info(f"✓ Total active questions in database: {count}")
                
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                logger.error(f"✗ Error updating review questions: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database connection error: {str(e)}")
        return False

def main():
    """Main function"""
    logger.info("=== LogiScore Review Questions 5-Point System Update ===")
    
    # Update review questions
    logger.info("Updating review questions to 5-point system...")
    success = update_review_questions()
    
    if success:
        logger.info("\n✓ Review questions update completed successfully!")
        logger.info("The review system now uses the proper 5-point scale (0-5) with all categories and questions from the LogiScore Review Questions document.")
    else:
        logger.error("\n✗ Review questions update failed!")
        logger.error("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
