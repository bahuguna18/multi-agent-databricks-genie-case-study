# coordinator.py
from openai import OpenAI
from agents.sales_genie_client import query_sales_genie
from agents.customer_genie_client import query_customer_genie
import json

# --- CONFIGURATION ---
from config import OPENAI_API_KEY, LLM_MODEL, validate_config

# Initialize OpenAI client using config value
validate_config(allow_empty_openai=False)
client = OpenAI(api_key=OPENAI_API_KEY)


def coordinator(user_query: str):
    """
    Decides which Genie(s) to call (sales/customer), fetches their data,
    and then uses OpenAI to produce a neat, user-readable final answer.
    """

    # Step 1: Decide routing (Sales / Customer / Both)
    system_prompt = """You are a smart coordinator between two Databricks Genies:
    - Sales Genie handles queries about revenue, products, sales data, etc.
    - Customer Genie handles queries about customers, demographics, and customer data.

    Determine which agent(s) to call. If both are needed, split the query into sub-queries.
    You must respond strictly in valid JSON format only, like this:
    {
        "agents": ["sales", "customer"],
        "subqueries": {
            "sales": "Get total revenue by region",
            "customer": "Get number of customers by region"
        }
    }
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        response_format={"type": "json_object"}
    )

    routing = json.loads(response.choices[0].message.content)
    results = {}

    # Step 2: Route to appropriate Genie(s)
    if "sales" in routing.get("agents", []):
        print("➡️ Routing to Sales Genie...")
        results["sales"] = query_sales_genie(routing["subqueries"].get("sales", user_query))

    if "customer" in routing.get("agents", []):
        print("➡️ Routing to Customer Genie...")
        results["customer"] = query_customer_genie(routing["subqueries"].get("customer", user_query))

    if not results:
        return "⚠️ No agents selected — please refine your question."

    # Step 3: Always consolidate into a neat final summary
    consolidation_prompt = f"""
    You are a data analysis assistant. Convert the following raw data responses from Databricks Genies
    into a clear, user-readable summary for an executive audience.
    
    USER QUESTION:
    {user_query}

    RAW RESULTS (JSON or text):
    {json.dumps(results, indent=2)}

    Write a concise, natural language summary of the findings, highlighting key figures, comparisons,
    and insights. Use bullet points or short paragraphs where appropriate.
    """

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You summarize and explain analytical results in a professional, readable format."},
            {"role": "user", "content": consolidation_prompt}
        ]
    )

    final_answer = final_response.choices[0].message.content.strip()
    return final_answer
