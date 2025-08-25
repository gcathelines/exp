"""
BigQuery tools for query execution and error handling.
Contains BigQuery client integration and error formatting utilities.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from crewai.tools import tool
from google.cloud import bigquery

from ...utils.models import QueryResult

logger = logging.getLogger(__name__)


def format_error_response(error_type: str, error_message: str, context: dict) -> str:
    """
    Standardized user-friendly error messages with suggestions.
    
    Args:
        error_type: Type of error ('BigQuery', 'VertexAI', 'Validation')
        error_message: Raw error message
        context: Additional context like query, table name
        
    Returns:
        User-friendly error message with suggestions
    """
    if error_type == "BigQuery":
        if "not found" in error_message.lower():
            return f"Table or dataset not found. Please check if the table exists and you have access permissions."
        elif "syntax error" in error_message.lower():
            return f"SQL syntax error. The generated query has invalid syntax. Try rephrasing your request."
        elif "exceeded" in error_message.lower():
            return f"Query would process too much data. Try narrowing your date range to last 2 weeks or fewer rows."
        else:
            return f"BigQuery error: {error_message[:200]}..."
    
    elif error_type == "VertexAI":
        return f"AI model error: Unable to process your request. Please try rephrasing your question."
    
    elif error_type == "Validation":
        if "date" in error_message.lower():
            return f"Date range too large. Please limit queries to 30 days or less. Try 'last 2 weeks' instead."
        else:
            return f"Query validation failed: {error_message}"
    
    return f"Unexpected error: {error_message[:200]}..."


def _extract_date_range(data: list[dict[str, Any]]) -> tuple[datetime, datetime]:
    """Extract date range from query results."""
    try:
        # Look for date columns
        date_cols = []
        if data:
            for key in data[0].keys():
                if 'date' in key.lower():
                    date_cols.append(key)
        
        if not date_cols:
            # Default to last 7 days if no date found
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            return (start_date, end_date)
        
        # Extract dates from first date column found
        date_col = date_cols[0]
        dates = [row[date_col] for row in data if row.get(date_col)]
        
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            
            # Convert to datetime if needed
            if isinstance(min_date, str):
                min_date = datetime.fromisoformat(min_date.replace('Z', '+00:00'))
            if isinstance(max_date, str):
                max_date = datetime.fromisoformat(max_date.replace('Z', '+00:00'))
                
            return (min_date, max_date)
            
    except Exception as e:
        logger.warning(f"Error extracting date range: {e}")
    
    # Default fallback
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    return (start_date, end_date)


@tool 
def execute_bigquery_tool(sql_query: str, table_name: str) -> QueryResult:
    """
    Execute SQL queries against BigQuery using Agent 2's own BigQuery client.
    
    Args:
        sql_query: SQL query to execute
        table_name: Target table name for context
        
    Returns:
        QueryResult from src/utils/models.py
    """
    try:
        # Initialize BigQuery client
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "data-314708")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path:
            client = bigquery.Client(project=project_id)
        else:
            client = bigquery.Client(project=project_id)
        
        # Execute query with timing
        start_time = datetime.now()
        query_job = client.query(sql_query)
        results = query_job.result()
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in results]
        row_count = len(data)
        
        # Extract date range from data if available
        date_range = _extract_date_range(data)
        
        # Build metadata
        metadata = {
            "job_id": query_job.job_id,
            "bytes_processed": query_job.total_bytes_processed or 0,
            "query": sql_query[:500] + "..." if len(sql_query) > 500 else sql_query
        }
        
        logger.info(f"BigQuery execution completed: {row_count} rows in {execution_time:.2f}s")
        
        return QueryResult(
            data=data,
            metadata=metadata,
            execution_time=execution_time,
            row_count=row_count,
            date_range=date_range
        )
        
    except Exception as e:
        error_message = format_error_response("BigQuery", str(e), {
            "query": sql_query,
            "table": table_name
        })
        logger.error(f"BigQuery execution error: {error_message}")
        raise Exception(error_message)