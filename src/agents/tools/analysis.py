"""
Analysis tools for LLM-powered business insights generation.
Contains dynamic schema exploration and intelligent data interpretation.
"""
import logging
from typing import Any

import pandas as pd
from crewai.tools import tool

from ...utils.models import QueryResult

logger = logging.getLogger(__name__)


def calculate_confidence_score(
    query_complexity: str, 
    validation_passed: bool, 
    data_quality_score: float
) -> float:
    """
    Consistent confidence scoring (0.0-1.0) across all agents.
    
    Args:
        query_complexity: 'simple', 'medium', 'complex'
        validation_passed: Whether date/safety validation passed
        data_quality_score: Quality score of returned data (0.0-1.0)
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    base_scores = {
        'simple': 0.9,
        'medium': 0.75,
        'complex': 0.6
    }
    
    base_score = base_scores.get(query_complexity, 0.5)
    
    # Reduce confidence if validation failed
    if not validation_passed:
        base_score *= 0.7
    
    # Factor in data quality
    final_score = base_score * data_quality_score
    
    return max(0.0, min(1.0, final_score))


@tool
def generate_insights_tool(query_result: QueryResult, original_query: str, exploration_mode: bool = False) -> str:
    """
    LLM-powered business insights generation with optional schema exploration.
    
    Args:
        query_result: QueryResult from BigQuery execution  
        original_query: Original natural language query for context
        exploration_mode: If True, performs quick data exploration for intelligent recommendations
        
    Returns:
        Natural language business insights (or exploration recommendations)
    """
    try:
        if not query_result.data:
            return "No data found for your query. Try adjusting your date range or criteria."
        
        # Prepare structured data summary for LLM analysis
        df = pd.DataFrame(query_result.data)
        
        # Let LLM analyze schema context dynamically within the main prompt
        
        # Prepare data summary for LLM analysis
        data_summary = {
            "row_count": query_result.row_count,
            "execution_time": f"{query_result.execution_time:.2f}s",
            "columns": list(df.columns),
            "data_sample": query_result.data[:3] if len(query_result.data) > 3 else query_result.data,
            "original_query": original_query,
            "date_range": f"{query_result.date_range[0].strftime('%Y-%m-%d')} to {query_result.date_range[1].strftime('%Y-%m-%d')}"
        }
        
        # Add statistical summaries for LLM context
        numeric_stats = {}
        categorical_stats = {}
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64'] and not df[col].isna().all():
                # Dynamic numeric analysis - no hardcoded column assumptions
                numeric_stats[col] = {
                    "sum": float(df[col].sum()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "dtype": str(df[col].dtype)
                }
            else:
                # Dynamic categorical analysis - detect patterns from actual data
                unique_count = df[col].nunique()
                categorical_stats[col] = {
                    "unique_count": unique_count,
                    "top_values": df[col].value_counts().head(3).to_dict() if unique_count < 50 else None,
                    "sample_values": df[col].dropna().head(3).tolist(),
                    "dtype": str(df[col].dtype)
                }
        
        # Create LLM prompt for business insights
        if exploration_mode:
            prompt = f"""
            EXPLORATION MODE: Quick analysis of business data to suggest interesting insights.
            
            BUSINESS DATA OVERVIEW:
            - Query: "{original_query}"
            - Found: {query_result.row_count} records ({query_result.execution_time:.1f}s)
            - Time Period: {data_summary['date_range']}
            - Column Schema: {', '.join(df.columns)} (analyze these for business context)
            
            KEY STATISTICS:
            Numeric Data: {numeric_stats}
            Categories: {categorical_stats}
            
            SAMPLE RECORDS (first 3):
            {data_summary['data_sample']}
            
            Please identify 2-3 most interesting business patterns or insights that would be valuable for management to know. Focus on actionable insights like trends, anomalies, or opportunities.
            """
        else:
            prompt = f"""
            BUSINESS DATA ANALYSIS REQUEST
            
            User asked: "{original_query}"
            
            DATASET CONTEXT:
            - {query_result.row_count} records analyzed in {query_result.execution_time:.1f} seconds
            - Time period: {data_summary['date_range']} 
            - Column Schema: {', '.join(df.columns)} (infer business context from column names)
            
            NUMERICAL INSIGHTS:
            {numeric_stats}
            
            CATEGORICAL BREAKDOWN: 
            {categorical_stats}
            
            SAMPLE DATA:
            {data_summary['data_sample']}
            
            Please provide clear business insights that answer the user's question. Focus on:
            1. Key findings that directly address their query
            2. Notable trends or patterns 
            3. Business implications or recommendations
            4. Any concerning anomalies or opportunities
            
            Keep insights business-focused and actionable.
            """
        
        # This will be processed by the LLM when called by CrewAI agents
        # For now, return the structured prompt that the LLM will analyze
        logger.info(f"Prepared {'exploration' if exploration_mode else 'analysis'} prompt for query: {original_query[:50]}...")
        
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Data analysis preparation error: {e}")
        return f"Unable to prepare data for analysis: {str(e)[:100]}..."


# NOTE: Business context mapping moved to knowledge base (future enhancement)
# For now, LLM analyzes column names dynamically within the main prompt