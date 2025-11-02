"""
Customer Agent for querying Customer Insights Genie workspace
"""
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from typing import Dict, Any

from agents.base_agent import BaseGenieAgent
from config import CUSTOMER_GENIE_SPACE_ID, OPENAI_API_KEY, LLM_MODEL


class CustomerAgent(BaseGenieAgent):
    """Agent responsible for querying Customer Insights data from Genie"""
    
    def __init__(self):
        """Initialize the Customer Agent"""
        super().__init__()
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        )
        self._initialize_tools()
        self._initialize_agent()
    
    def get_genie_space_id(self) -> str:
        """Return the Customer Genie Space ID"""
        return CUSTOMER_GENIE_SPACE_ID
    
    def _initialize_tools(self):
        """Initialize tools for the customer agent"""
        self.tools = [
            Tool(
                name="QueryCustomerGenie",
                func=self._query_customer_data,
                description=(
                    "Query the Customer Insights Genie workspace for customer data. "
                    "Use this for questions about customer segments, lifetime value, "
                    "churn risk, customer behavior, or customer demographics."
                )
            ),
            Tool(
                name="GetCustomerSegments",
                func=self._get_customer_segments,
                description="Get customer data grouped by segment"
            ),
            Tool(
                name="GetChurnRisk",
                func=self._get_churn_risk,
                description="Get churn risk analysis by region or segment"
            ),
            Tool(
                name="GetLifetimeValue",
                func=self._get_lifetime_value,
                description="Get customer lifetime value metrics"
            )
        ]
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        # Bind tools to LLM for function calling
        self.agent = self.llm.bind_tools(self.tools)
    
    def _query_customer_data(self, query: str) -> str:
        """Query customer data from Genie"""
        result = self.query_genie(query)
        if result["status"] == "success":
            return result["response"]
        else:
            return f"Error querying customer data: {result.get('error', 'Unknown error')}"
    
    def _get_customer_segments(self, query: str) -> str:
        """Get customer data by segment"""
        genie_query = f"Show customer segments. {query}"
        result = self.query_genie(genie_query)
        return result["response"]
    
    def _get_churn_risk(self, query: str) -> str:
        """Get churn risk analysis"""
        genie_query = f"Show churn risk analysis. {query}"
        result = self.query_genie(genie_query)
        return result["response"]
    
    def _get_lifetime_value(self, query: str) -> str:
        """Get lifetime value metrics"""
        genie_query = f"Show customer lifetime value. {query}"
        result = self.query_genie(genie_query)
        return result["response"]
    
    def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a query using the customer agent
        
        Args:
            query: Natural language query about customer data
            
        Returns:
            Dictionary containing agent response and metadata
        """
        try:
            # Use LLM with tools for reasoning
            from langchain_core.messages import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content="You are a helpful assistant that queries customer data from Databricks Genie. Use the available tools to answer questions about customer segments, churn risk, lifetime value, and customer behavior."),
                HumanMessage(content=query)
            ]
            
            response = self.agent.invoke(messages)
            
            # Check if tool calls are needed
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute tool calls
                results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    # Find and execute the tool
                    for tool in self.tools:
                        if tool.name == tool_name:
                            if "query" in tool_args:
                                result = tool.func(tool_args["query"])
                            else:
                                result = tool.func(str(tool_args))
                            results.append(result)
                            break
                
                # Get final response with tool results
                from langchain_core.messages import HumanMessage
                final_messages = messages + [response] + [HumanMessage(content=f"Tool results: {results}")]
                final_response = self.llm.invoke(final_messages)
                response_text = final_response.content if hasattr(final_response, 'content') else str(final_response)
            else:
                response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Also get raw Genie response for reference
            genie_response = self.query_genie(query)
            
            return {
                "agent_type": "CustomerAgent",
                "query": query,
                "response": response_text,
                "genie_response": genie_response,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent_type": "CustomerAgent",
                "query": query,
                "response": f"Error: {str(e)}",
                "status": "error",
                "error": str(e)
            }
    
    def get_churn_insights(self, region: str = None) -> Dict[str, Any]:
        """
        Get churn risk insights, optionally filtered by region
        
        Args:
            region: Optional region filter
            
        Returns:
            Churn insights dictionary
        """
        query = "Show customer segments and churn risk"
        if region:
            query += f" Filter by region: {region}"
        
        return self.execute(query)

