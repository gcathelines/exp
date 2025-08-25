"""
Query Agent for natural language to SQL conversion and BigQuery execution.
Uses LLM-powered tools for dynamic SQL generation and data retrieval.
"""
import logging
from typing import Any

from crewai import Agent

from ..utils.models import QueryResult, UserQuery
from .tools import generate_sql_query_tool, execute_bigquery_tool

logger = logging.getLogger(__name__)


def create_query_agent() -> Agent:
    """
    Create Query Agent for SQL generation and BigQuery execution.
    
    Returns:
        Configured CrewAI Query Agent
    """
    return Agent(
        role="SQL Query Specialist", 
        goal="Convert natural language to safe BigQuery SQL and execute queries efficiently",
        backstory="""You are an expert SQL developer specializing in BigQuery. 
        You understand business questions and convert them into optimized, safe SQL queries.
        You always include proper date filtering (≤30 days), use appropriate LIMIT clauses,
        and ensure queries are secure against injection attacks. You work with dynamic 
        schemas and never assume column names.""",
        tools=[generate_sql_query_tool, execute_bigquery_tool],
        verbose=True,
        max_iter=3
    )


class QueryOrchestrator:
    """
    Orchestrates the query workflow for SQL generation and execution.
    """
    
    def __init__(self):
        self.query_agent = create_query_agent()
        logger.info("Query Agent initialized")
    
    def process_query_request(self, user_query: str, table_name: str = "user_transaction") -> QueryResult:
        """
        Process user query through SQL generation and BigQuery execution.
        
        Args:
            user_query: Natural language query from user
            table_name: Target BigQuery table name
            
        Returns:
            QueryResult with data and metadata
        """
        try:
            logger.info(f"Processing query: {user_query[:100]}...")
            
            # Step 1: Generate SQL using LLM-powered tool
            sql_generation_task = f"""
            Convert this natural language query to safe BigQuery SQL: "{user_query}"
            Target table: {table_name}
            
            Requirements:
            1. First understand the table schema dynamically
            2. Generate appropriate SQL based on actual column names  
            3. Include mandatory date filtering (≤30 days)
            4. Add ORDER BY and LIMIT clauses
            5. Ensure query safety and optimization
            
            Return the final SQL query ready for execution.
            """
            
            sql_query = self.query_agent.execute_task(
                task=sql_generation_task,
                tools=[generate_sql_query_tool]
            )
            
            logger.info(f"Generated SQL: {sql_query[:200]}...")
            
            # Step 2: Execute SQL against BigQuery
            execution_task = f"""
            Execute this SQL query against BigQuery: {sql_query}
            Target table: {table_name}
            
            Return the structured query results with metadata.
            """
            
            query_result = self.query_agent.execute_task(
                task=execution_task,
                tools=[execute_bigquery_tool]
            )
            
            logger.info(f"Query executed successfully: {query_result.row_count if hasattr(query_result, 'row_count') else 'unknown'} rows")
            
            return query_result
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            # Return error result in QueryResult format
            from datetime import datetime, timedelta
            error_result = QueryResult(
                data=[],
                metadata={"error": str(e), "query": user_query},
                execution_time=0.0,
                row_count=0,
                date_range=(datetime.now() - timedelta(days=7), datetime.now())
            )
            return error_result
    
    def validate_and_execute(self, user_query: str, table_name: str = "user_transaction") -> dict[str, Any]:
        """
        Validate user query and execute with error handling.
        
        Args:
            user_query: Natural language query
            table_name: Target table name
            
        Returns:
            Structured response with data or error information
        """
        try:
            # Basic validation
            if not user_query or not user_query.strip():
                return {
                    "success": False,
                    "error": "Empty query provided",
                    "data": None
                }
            
            if len(user_query) > 1000:
                return {
                    "success": False, 
                    "error": "Query too long (max 1000 characters)",
                    "data": None
                }
            
            # Process the query
            result = self.process_query_request(user_query, table_name)
            
            if hasattr(result, 'data') and result.data:
                return {
                    "success": True,
                    "data": result,
                    "message": f"Query executed successfully: {result.row_count} rows returned in {result.execution_time:.2f}s"
                }
            else:
                return {
                    "success": False,
                    "error": "No data returned from query",
                    "data": result
                }
                
        except Exception as e:
            logger.error(f"Query validation/execution error: {e}")
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)[:200]}",
                "data": None
            }