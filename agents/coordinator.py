"""
Coordinator Agent that orchestrates queries between Sales and Customer agents.
"""

import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage

from agents.sales_agent import SalesAgent
from agents.customer_agent import CustomerAgent
from config import OPENAI_API_KEY, LLM_MODEL


class CoordinatorAgent:
    """Coordinates between Sales and Customer agents to provide combined insights."""

    def __init__(self):
        """Initialize the coordinator and its agents."""
        self.sales_agent = SalesAgent()
        self.customer_agent = CustomerAgent()
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        )

        self._setup_tools()
        self.agent = self.llm.bind_tools(self.tools)

    # ----------------------------------------------------------------------
    # Tool setup
    # ----------------------------------------------------------------------

    def _setup_tools(self):
        """Define tools that the coordinator can use."""
        self.tools = [
            Tool(
                name="QuerySalesAgent",
                func=self._query_sales_agent,
                description="Handles questions about revenue, sales performance, and products."
            ),
            Tool(
                name="QueryCustomerAgent",
                func=self._query_customer_agent,
                description="Handles questions about customer segments, churn risk, and customer behavior."
            ),
            Tool(
                name="QueryBothAgents",
                func=self._query_both_agents,
                description="Combines sales and customer data for cross-domain insights."
            ),
        ]

    # ----------------------------------------------------------------------
    # Tool functions
    # ----------------------------------------------------------------------

    def _query_sales_agent(self, query: str) -> str:
        result = self.sales_agent.execute(query)
        if result["status"] == "success":
            return f"Sales Agent: {result['response']}"
        return f"Sales Agent Error: {result.get('error', 'Unknown error')}"

    def _query_customer_agent(self, query: str) -> str:
        result = self.customer_agent.execute(query)
        if result["status"] == "success":
            return f"Customer Agent: {result['response']}"
        return f"Customer Agent Error: {result.get('error', 'Unknown error')}"

    def _query_both_agents(self, query: str) -> str:
        """Query both agents and return merged results."""
        sales_data = self.sales_agent.execute(query)
        customer_data = self.customer_agent.execute(query)

        combined = {
            "sales_data": sales_data.get("response", "No sales data available"),
            "customer_data": customer_data.get("response", "No customer data available"),
            "query": query,
        }

        return json.dumps(combined, indent=2)

    # ----------------------------------------------------------------------
    # Core coordination logic
    # ----------------------------------------------------------------------

    def coordinate_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze and coordinate the query across multiple agents using LLM reasoning.
        """
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are a coordinator agent that decides how to route user queries "
                        "between Sales and Customer agents. "
                        "Use the Sales Agent for sales-related data, "
                        "Customer Agent for customer data, or both when needed."
                    )
                ),
                HumanMessage(content=query),
            ]

            response = self.agent.invoke(messages)

            # If LLM decides to call tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    for tool in self.tools:
                        if tool.name == tool_name:
                            query_arg = tool_args.get("query") or str(tool_args)
                            results.append(tool.func(query_arg))
                            break

                final_messages = messages + [response] + [HumanMessage(content=f"Tool results: {results}")]
                final_response = self.llm.invoke(final_messages)
                response_text = getattr(final_response, "content", str(final_response))
            else:
                response_text = getattr(response, "content", str(response))

            return {
                "agent_type": "CoordinatorAgent",
                "query": query,
                "response": response_text,
                "status": "success",
            }

        except Exception as e:
            return {
                "agent_type": "CoordinatorAgent",
                "query": query,
                "response": f"Error: {e}",
                "status": "error",
                "error": str(e),
            }

    # ----------------------------------------------------------------------
    # Predefined query methods
    # ----------------------------------------------------------------------

    def analyze_revenue_vs_churn(self, region: str = None) -> Dict[str, Any]:
        """Analyze regions with high revenue but high churn."""
        query = "What regions have high revenue but high customer churn?"
        if region:
            query += f" Focus on region: {region}."
        return self.coordinate_query(query)

    def compare_sales_with_segments(self) -> Dict[str, Any]:
        """Compare sales performance across customer segments."""
        query = "Compare sales performance with customer segments."
        return self.coordinate_query(query)

    def analyze_premium_customer_categories(self) -> Dict[str, Any]:
        """Identify which product categories appeal to premium customers."""
        query = "Which product categories appeal to Premium customers?"
        return self.coordinate_query(query)

    # ----------------------------------------------------------------------
    # Data synthesis
    # ----------------------------------------------------------------------

    def synthesize_insights(self, sales_data: Dict, customer_data: Dict) -> str:
        """Combine sales and customer data into a summarized insight."""
        prompt = (
            "Based on the following data, provide a concise analysis with insights and recommendations.\n\n"
            f"Sales Data:\n{json.dumps(sales_data, indent=2)}\n\n"
            f"Customer Data:\n{json.dumps(customer_data, indent=2)}"
        )

        result = self.llm.invoke(prompt)
        return getattr(result, "content", str(result))
