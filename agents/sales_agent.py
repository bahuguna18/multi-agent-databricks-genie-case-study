"""
Sales Agent for querying Sales Analytics Genie workspace
"""
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from typing import Dict, Any

from agents.base_agent import BaseGenieAgent
from config import SALES_GENIE_SPACE_ID, OPENAI_API_KEY, LLM_MODEL


class SalesAgent(BaseGenieAgent):
    """Agent responsible for querying Sales Analytics data from Genie"""
    
    def __init__(self):
        """Initialize the Sales Agent"""
        super().__init__()
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        )
        self._initialize_tools()
        self._initialize_agent()
    
    def get_genie_space_id(self) -> str:
        """Return the Sales Genie Space ID"""
        return SALES_GENIE_SPACE_ID
    
    def _initialize_tools(self):
        """Initialize tools for the sales agent"""
        self.tools = [
            Tool(
                name="QuerySalesGenie",
                func=self._query_sales_data,
                description=(
                    "Query the Sales Analytics Genie workspace for sales data. "
                    "Use this for questions about revenue, product sales, "
                    "categories, regions, sales trends, or transaction data."
                )
            ),
            Tool(
                name="GetRevenueByRegion",
                func=self._get_revenue_by_region,
                description="Get total revenue grouped by region"
            ),
            Tool(
                name="GetProductCategorySales",
                func=self._get_product_category_sales,
                description="Get sales data by product category"
            )
        ]
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        # Bind tools to LLM for function calling
        self.agent = self.llm.bind_tools(self.tools)
    
    def _query_sales_data(self, query: str) -> str:
        """Query sales data from Genie"""
        result = self.query_genie(query)
        if result["status"] == "success":
            return result["response"]
        else:
            return f"Error querying sales data: {result.get('error', 'Unknown error')}"
    
    def _get_revenue_by_region(self, query: str) -> str:
        """Get revenue breakdown by region"""
        genie_query = f"Show revenue by region. {query}"
        result = self.query_genie(genie_query)
        return result["response"]
    
    def _get_product_category_sales(self, query: str) -> str:
        """Get sales by product category"""
        genie_query = f"Show sales by product category. {query}"
        result = self.query_genie(genie_query)
        return result["response"]
    
    def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a query using the sales agent
        
        Args:
            query: Natural language query about sales data
            
        Returns:
            Dictionary containing agent response and metadata
        """
        try:
            # Use LLM with tools for reasoning
            from langchain_core.messages import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content="You are a helpful assistant that queries sales data from Databricks Genie. Use the available tools to answer questions about sales, revenue, products, and regions."),
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
                "agent_type": "SalesAgent",
                "query": query,
                "response": response_text,
                "genie_response": genie_response,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent_type": "SalesAgent",
                "query": query,
                "response": f"Error: {str(e)}",
                "status": "error",
                "error": str(e)
            }
    
    def get_revenue_insights(self, region: str = None) -> Dict[str, Any]:
        """
        Get revenue insights, optionally filtered by region
        
        Args:
            region: Optional region filter
            
        Returns:
            Revenue insights dictionary
        """
        query = "What is the total revenue?"
        if region:
            query += f" Filter by region: {region}"
        
        return self.execute(query)

