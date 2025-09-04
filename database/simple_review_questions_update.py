#!/usr/bin/env python3
"""
Simple script to update review questions - can be run directly in database
"""

import json

# The review questions data
REVIEW_QUESTIONS = [
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
    }
    # Add more questions as needed...
]

def generate_sql():
    """Generate SQL to update review questions"""
    sql_statements = []
    
    # Clear existing questions
    sql_statements.append("DELETE FROM review_questions;")
    
    # Insert new questions
    for question in REVIEW_QUESTIONS:
        rating_definitions_json = json.dumps(question['rating_definitions'])
        sql = f"""
        INSERT INTO review_questions (
            category_id, category_name, question_id, question_text, 
            rating_definitions, is_active
        ) VALUES (
            '{question['category_id']}',
            '{question['category_name']}',
            '{question['question_id']}',
            '{question['question_text']}',
            '{rating_definitions_json}',
            true
        );
        """
        sql_statements.append(sql)
    
    return "\n".join(sql_statements)

if __name__ == "__main__":
    print("SQL to update review questions:")
    print("=" * 50)
    print(generate_sql())
