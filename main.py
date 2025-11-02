"""
Main entry point for the Multi-Agent Databricks Genie System.
Handles demo, example, and interactive modes for multi-agent coordination.
"""

import sys
import json
import time
from typing import Dict, Any

from config import validate_config
from agents.sales_agent import SalesAgent
from agents.customer_agent import CustomerAgent
from agents.coordinator import CoordinatorAgent


def print_divider(title: str = ""):
    """Print a readable divider with optional title"""
    print("\n" + "=" * 80)
    if title:
        print(f"{title}")
        print("=" * 80)
    print()


def show_response(response: Dict[str, Any]):
    """Print agent response in a readable format"""
    print(f"\n[{response.get('agent_type', 'Unknown Agent')}]")
    print(f"Query   : {response.get('query', '-')}")
    print(f"Status  : {response.get('status', 'unknown')}")
    print("-" * 80)
    print(response.get('response', 'No response available'))
    print("-" * 80)


# ------------------- DEMO FUNCTIONS -------------------

def demo_individual_agents():
    """Run demo showing each agent independently"""
    print_divider("Demo 1: Individual Agents")

    sales_agent = SalesAgent()
    customer_agent = CustomerAgent()

    # Sales Agent example
    print("\n[Sales Agent Test]")
    sales_query = "What is the total revenue?"
    sales_result = sales_agent.execute(sales_query)
    show_response(sales_result)

    # Customer Agent example
    print("\n[Customer Agent Test]")
    customer_query = "Show customer segments"
    customer_result = customer_agent.execute(customer_query)
    show_response(customer_result)


def demo_coordinator():
    """Run demo for coordinator handling multi-agent queries"""
    print_divider("Demo 2: Coordinator Agent")

    coordinator = CoordinatorAgent()

    print("\n[Query 1] Revenue vs Churn Analysis")
    res1 = coordinator.analyze_revenue_vs_churn()
    show_response(res1)

    print("\n[Query 2] Sales Performance vs Customer Segments")
    res2 = coordinator.compare_sales_with_segments()
    show_response(res2)

    print("\n[Query 3] Premium Customer Product Categories")
    res3 = coordinator.analyze_premium_customer_categories()
    show_response(res3)


# ------------------- INTERACTIVE MODE -------------------

def interactive_mode():
    """Start interactive query mode"""
    print_divider("Demo 3: Interactive Mode")

    coordinator = CoordinatorAgent()

    print("Type your queries (type 'exit' to quit):")
    print("Examples:")
    print(" - What is the total revenue in North region?")
    print(" - Show customer segments with high churn risk")
    print(" - Which regions have both high sales and low churn?\n")

    while True:
        try:
            query = input("Query: ").strip()
            if query.lower() in {"exit", "quit", "q"}:
                print("Exiting interactive mode.")
                break
            if not query:
                continue

            print("\nProcessing...")
            response = coordinator.coordinate_query(query)
            show_response(response)

        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'exit' to quit.")


# ------------------- REQUIRED QUERIES -------------------

def run_example_queries():
    """Run the required example queries"""
    print_divider("Running Example Queries")

    coordinator = CoordinatorAgent()

    queries = [
        "What regions have high revenue but high customer churn?",
        "Compare sales performance with customer segments",
        "Which product categories appeal to Premium customers?"
    ]

    results = []

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}/{len(queries)}: {query}")
        print('=' * 80)

        result = coordinator.coordinate_query(query)
        show_response(result)
        results.append(result)

        time.sleep(1)  # small delay

    return results


# ------------------- MAIN FUNCTION -------------------

def main():
    print_divider("Multi-Agent Databricks Genie System")

    # Validate config
    try:
        validate_config()
        print("[OK] Configuration validated.")
    except ValueError as e:
        print(f"[ERROR] Configuration issue: {e}")
        print("Please check your .env file (see .env.example for reference).")
        sys.exit(1)

    # Determine mode
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "examples"

    if mode == "demo":
        demo_individual_agents()
        demo_coordinator()
    elif mode in {"interactive", "i"}:
        interactive_mode()
    elif mode in {"examples", "required"}:
        run_example_queries()
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes:")
        print("  python main.py             -> Run example queries (default)")
        print("  python main.py demo        -> Run demo sequences")
        print("  python main.py interactive -> Interactive query mode")
        sys.exit(1)

    print_divider("Session Complete")


if __name__ == "__main__":
    main()
