# Multi-Agent System using Databricks Genie

A lightweight multi-agent system built with Databricks Genie and simple orchestration code, designed to analyze Sales and Customer data across two Genie spaces and generate combined insights.

---

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file with your environment variables (or export them in your shell):

```
DATABRICKS_HOST=<your-workspace-url>
DATABRICKS_TOKEN=<your-access-token>
SALES_GENIE_SPACE_ID=<sales-space-id>
CUSTOMER_GENIE_SPACE_ID=<customer-space-id>
OPENAI_API_KEY=<openai-key>
LLM_MODEL=gpt-4o-mini
```

Keep secrets out of version control. Use a `.env` file locally and secret management in production.

---

## Run

Run sample queries using the CLI:

```bash
python main.py
```

Run the Streamlit chat UI (if you installed `streamlit`):

```bash
streamlit run ui_app.py
```

If you prefer an interactive mode (if implemented), you can run:

```bash
python main.py interactive
```

---

## How It Works (High Level)

• Sales Agent → Fetches sales-related insights from the Sales Genie space.

• Customer Agent → Fetches customer and churn-related insights from the Customer Genie space.

• Coordinator Agent → Uses an LLM to route the incoming question to one or both agents, gathers results, and optionally consolidates them into a single human-friendly summary.

Example query:

> “Which regions have high revenue but high churn?”

The coordinator may split this into two subqueries (sales and customer), call both Genies, then summarize:

```
Query: Which regions have high revenue but high churn?

Insight:
- North: High revenue, low churn
- South: Medium revenue, high churn
```

---

## Structure

```
agents/
 ├── base_agent.py           # (optional) shared logic for agents
 ├── sales_agent.py         # Sales Genie client/helpers
 ├── customer_agent.py      # Customer Genie client/helpers
 └── coordinator.py        # Routes queries and consolidates results
main.py
ui_app.py
config.py
requirements.txt
```

---
## Demo

<img width="816" height="828" alt="image" src="https://github.com/user-attachments/assets/c5549416-0f64-4a22-903a-d13389fc309e" />

<img width="816" height="875" alt="image" src="https://github.com/user-attachments/assets/9db7ad0c-10f1-4e01-ac0a-91592a8b52a6" />





