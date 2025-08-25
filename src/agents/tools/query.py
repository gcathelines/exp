"""
Query tools for SQL generation and validation.
Contains natural language to SQL conversion with safety validation.
"""
import logging
import os
import re
from typing import Dict

import sqlparse
from crewai.tools import tool

logger = logging.getLogger(__name__)


def build_table_name(table_name: str) -> str:
    """
    Constructs full BigQuery table references.
    
    Args:
        table_name: Short table name (e.g., 'user_transaction')
        
    Returns:
        Full table reference (e.g., 'data-314708.intermediate_transaction.user_transaction')
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "data-314708")
    dataset = os.getenv("BIGQUERY_DATASET", "intermediate_transaction")
    
    return f"{project_id}.{dataset}.{table_name}"


def validate_date_safety(sql_query: str) -> Dict[str, str]:
    """
    Validates SQL enforces ≤30 day date constraints.
    
    Args:
        sql_query: SQL query to validate
        
    Returns:
        Dict with 'is_safe', 'message', 'suggested_fix'
    """
    try:
        parsed = sqlparse.parse(sql_query)[0]
        query_str = str(parsed).lower()
        
        # Check for date filtering patterns
        date_patterns = [
            r'date\s*>=\s*date_sub\s*\(\s*current_date\s*\(\s*\)\s*,\s*interval\s+(\d+)\s+day\s*\)',
            r'date\s*>=\s*current_date\s*\(\s*\)\s*-\s*(\d+)',
            r'date\s*between.*and.*current_date',
            r'where.*date.*>=.*date_sub.*interval\s+(\d+)\s+day'
        ]
        
        has_date_filter = False
        max_days = 0
        
        for pattern in date_patterns:
            match = re.search(pattern, query_str)
            if match:
                has_date_filter = True
                if match.groups():
                    days = int(match.groups()[0])
                    max_days = max(max_days, days)
        
        # Check for relative date terms
        relative_terms = ['last week', 'past week', 'last 7 days', 'last month', 'past month']
        for term in relative_terms:
            if term in query_str:
                has_date_filter = True
                if 'month' in term:
                    max_days = max(max_days, 30)
                elif 'week' in term:
                    max_days = max(max_days, 7)
        
        if not has_date_filter:
            return {
                "is_safe": False,
                "message": "Query lacks date filtering",
                "suggested_fix": "Add 'WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)' to limit data scan"
            }
        
        if max_days > 30:
            return {
                "is_safe": False,
                "message": f"Date range too large: {max_days} days",
                "suggested_fix": "Reduce date range to 30 days or less"
            }
        
        return {
            "is_safe": True,
            "message": "Date safety validation passed",
            "suggested_fix": ""
        }
        
    except Exception as e:
        logger.warning(f"Date validation error: {e}")
        return {
            "is_safe": False,
            "message": "Unable to validate date safety",
            "suggested_fix": "Ensure query includes proper date filtering"
        }


@tool
def generate_sql_query_tool(natural_language_query: str, table_name: str) -> str:
    """
    LLM-powered natural language to BigQuery SQL conversion with safety validation.
    
    This tool creates a structured prompt for LLM processing. The actual SQL generation
    is handled by the CrewAI agent using VertexAI/Gemini.
    
    Args:
        natural_language_query: User's natural language request
        table_name: Target table name (e.g., 'user_transaction')
        
    Returns:
        Structured prompt for LLM to generate safe BigQuery SQL
    """
    try:
        # Build full table reference
        full_table_name = build_table_name(table_name)
        
        # Create LLM prompt for dynamic SQL generation
        prompt = f"""
        TASK: Convert natural language to safe BigQuery SQL
        
        USER REQUEST: "{natural_language_query}"
        TARGET TABLE: `{full_table_name}`
        
        SAFETY REQUIREMENTS:
        1. MANDATORY: Add date filtering to limit data scan to ≤30 days
        2. MANDATORY: Include ORDER BY clause for consistent results  
        3. MANDATORY: Add LIMIT clause (≤1000 rows)
        4. Use proper BigQuery syntax and functions
        5. Prevent SQL injection - use only safe column references
        
        INSTRUCTIONS:
        1. First, you need to understand the table schema by running: DESCRIBE `{full_table_name}`
        2. Based on the actual schema, generate appropriate SQL that answers the user's question
        3. Always include date filtering using the actual date column name from schema
        4. Use actual column names from the schema - do not assume column names
        5. Return only the SQL query, no explanations
        
        EXAMPLE PATTERN:
        SELECT [columns]
        FROM `{full_table_name}` 
        WHERE [date_column] >= DATE_SUB(CURRENT_DATE(), INTERVAL [days] DAY)
        [GROUP BY if needed]
        ORDER BY [appropriate_column]
        LIMIT [appropriate_limit]
        
        Generate the SQL query now:
        """
        
        logger.info(f"Prepared SQL generation prompt for query: {natural_language_query[:50]}...")
        
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"SQL prompt preparation error: {str(e)}")
        raise Exception(f"Unable to prepare SQL generation prompt: {str(e)}")