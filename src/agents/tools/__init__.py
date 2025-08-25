"""
CrewAI Tools for BI Chat CLI System.

This module provides 4 CrewAI tools for Agent 2:
- Query generation with embedded safety validation
- BigQuery execution with Agent 2's own client
- Data analysis and insights generation  
- Plotly visualization creation

Usage:
    from src.agents.tools import (
        generate_sql_query_tool,
        execute_bigquery_tool, 
        generate_insights_tool,
        generate_plotly_chart_tool
    )
"""

# Import all CrewAI tools
from .analysis import generate_insights_tool
from .bigquery import execute_bigquery_tool
from .query import generate_sql_query_tool
from .visualization import generate_plotly_chart_tool

# Export only the CrewAI tools that agents will use directly
__all__ = [
    "generate_sql_query_tool",
    "execute_bigquery_tool", 
    "generate_insights_tool",
    "generate_plotly_chart_tool"
]