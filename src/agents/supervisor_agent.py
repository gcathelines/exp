"""
Supervisor Agent for intent classification and workflow routing.
Handles user query analysis and delegates to appropriate agents.
"""
import logging
from typing import Any

from crewai import Agent
from crewai.tools import tool

from ..utils.models import UserQuery, AgentResponse

logger = logging.getLogger(__name__)


@tool
def classify_user_intent(user_query: str) -> str:
    """
    Classify user intent to determine appropriate workflow routing.
    
    Args:
        user_query: Natural language query from user
        
    Returns:
        Classification result for routing decisions
    """
    # This will be processed by LLM to classify intent
    prompt = f"""
    TASK: Classify user intent for business intelligence query routing
    
    USER QUERY: "{user_query}"
    
    CLASSIFICATION OPTIONS:
    1. DIRECT_DATA: Simple data retrieval (count, show, list, get specific data)
       - Examples: "count transactions", "show revenue today", "list top users"
       - Route: Query Agent only
    
    2. ANALYSIS_REQUEST: User wants insights or analysis  
       - Examples: "analyze user behavior", "what trends do you see", "insights about revenue"
       - Route: Query Agent → Analysis Agent
    
    3. VISUALIZATION_REQUEST: Explicitly asks for charts/graphs
       - Examples: "show revenue in bar chart", "create graph of trends", "visualize data"
       - Route: Query Agent → Visualization Agent
    
    4. AMBIGUOUS: Unclear intent, needs clarification
       - Examples: "what's interesting", "tell me about our data", "any insights"
       - Route: Ask user for clarification with smart recommendations
    
    INSTRUCTIONS:
    1. Analyze the query for explicit keywords and intent
    2. Consider what the user likely wants as output
    3. Return ONLY the classification (DIRECT_DATA, ANALYSIS_REQUEST, VISUALIZATION_REQUEST, or AMBIGUOUS)
    4. No explanations, just the classification
    
    Classification:
    """
    
    logger.info(f"Prepared intent classification for: {user_query[:50]}...")
    return prompt.strip()


def create_supervisor_agent() -> Agent:
    """
    Create Supervisor Agent for intent classification and routing.
    
    Returns:
        Configured CrewAI Supervisor Agent
    """
    return Agent(
        role="Business Intelligence Supervisor",
        goal="Classify user intents and route queries to appropriate agents for optimal results",
        backstory="""You are an intelligent supervisor for a business intelligence system. 
        Your job is to understand what users really want from their queries and route them 
        to the right agents. You can classify simple data requests, analysis needs, 
        visualization requests, or identify when clarification is needed.""",
        tools=[classify_user_intent],
        verbose=True,
        allow_delegation=True,
        max_iter=2
    )


class SupervisorOrchestrator:
    """
    Orchestrates the supervisor workflow for user query processing.
    """
    
    def __init__(self):
        self.supervisor = create_supervisor_agent()
        logger.info("Supervisor Agent initialized")
    
    def process_user_query(self, user_query: UserQuery) -> dict[str, Any]:
        """
        Process user query through supervisor workflow.
        
        Args:
            user_query: Structured user query from CLI
            
        Returns:
            Workflow decision and next steps
        """
        try:
            # Use supervisor agent to classify intent
            classification_result = self.supervisor.execute_task(
                task=f"Classify the intent of this query: {user_query.query}",
                tools=[classify_user_intent]
            )
            
            # Parse classification and determine routing
            workflow = self._determine_workflow(classification_result, user_query)
            
            logger.info(f"Classified query as: {workflow['classification']} -> {workflow['route']}")
            
            return workflow
            
        except Exception as e:
            logger.error(f"Supervisor processing error: {e}")
            return {
                "classification": "ERROR", 
                "route": "DIRECT_DATA",  # Safe fallback
                "error": str(e),
                "user_query": user_query.query
            }
    
    def _determine_workflow(self, classification: str, user_query: UserQuery) -> dict[str, Any]:
        """
        Determine workflow routing based on classification.
        
        Args:
            classification: LLM classification result
            user_query: Original user query
            
        Returns:
            Workflow routing decision
        """
        classification_clean = classification.strip().upper()
        
        if "DIRECT_DATA" in classification_clean:
            return {
                "classification": "DIRECT_DATA",
                "route": "QUERY_ONLY", 
                "next_agent": "query_agent",
                "user_confirmation_needed": False,
                "user_query": user_query.query
            }
        
        elif "ANALYSIS_REQUEST" in classification_clean:
            return {
                "classification": "ANALYSIS_REQUEST", 
                "route": "QUERY_THEN_ANALYSIS",
                "next_agent": "query_agent",
                "follow_up_agent": "analysis_agent", 
                "user_confirmation_needed": True,
                "confirmation_message": f"I'll analyze the data for: '{user_query.query}'. This will run queries and generate business insights. Continue?",
                "user_query": user_query.query
            }
        
        elif "VISUALIZATION_REQUEST" in classification_clean:
            return {
                "classification": "VISUALIZATION_REQUEST",
                "route": "QUERY_THEN_VIZ", 
                "next_agent": "query_agent",
                "follow_up_agent": "visualization_agent",
                "user_confirmation_needed": True,
                "confirmation_message": f"I'll create visualizations for: '{user_query.query}'. This will generate charts and graphs. Continue?",
                "user_query": user_query.query
            }
        
        elif "AMBIGUOUS" in classification_clean:
            return {
                "classification": "AMBIGUOUS",
                "route": "USER_CLARIFICATION",
                "user_confirmation_needed": True,
                "clarification_message": f"I can help with '{user_query.query}' in several ways. Would you like me to: 1) Show you the raw data, 2) Provide business insights and analysis, or 3) Create charts and visualizations?",
                "user_query": user_query.query
            }
        
        else:
            # Safe fallback
            logger.warning(f"Unknown classification: {classification_clean}")
            return {
                "classification": "UNKNOWN",
                "route": "QUERY_ONLY",
                "next_agent": "query_agent", 
                "user_confirmation_needed": False,
                "user_query": user_query.query
            }