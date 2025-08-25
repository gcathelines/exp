"""
Shared data models for the BI Chat CLI system.
Interface contracts between Agent 1 and Agent 2.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QueryResult(BaseModel):
    """Result from BigQuery execution"""
    data: list[dict[str, Any]]
    metadata: dict[str, Any]
    execution_time: float
    row_count: int
    date_range: tuple[datetime, datetime]  # Enforced 30-day limit


class TokenUsage(BaseModel):
    """LLM token usage tracking"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_estimate: float


class AgentResponse(BaseModel):
    """Response from any CrewAI agent"""
    content: str
    visualizations: list[dict] | None = None
    token_usage: TokenUsage
    confidence_score: float  # 0.0 - 1.0
    timestamp: datetime
    cached: bool = False


class UserSession(BaseModel):
    """User session data for persistence"""
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    last_activity: datetime
    conversation_history: list[dict]


class ObservabilityLog(BaseModel):
    """Agent decision tracking for debugging"""
    session_id: str
    agent_name: str
    decision_reason: str
    input_query: str
    output_sql: str
    confidence: float
    timestamp: datetime


class UserQuery(BaseModel):
    """Standardized user input"""
    query: str
    user_id: str
    session_id: str
    context: dict[str, Any] | None = None