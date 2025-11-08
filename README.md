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

## Notes & Tips

- The project expects `DATABRICKS_HOST` and `DATABRICKS_TOKEN` to be set. Genie clients construct API URLs from the host and space IDs in `config.py`.
- The `agents/*` clients poll Genie message endpoints until the result is `COMPLETED`, then return attachments or inline results to the coordinator.
- The coordinator currently uses OpenAI to both route and summarize results. If you want to run without OpenAI, modify `config.validate_config()` or add fallback logic in `agents/coordinator.py`.
- The folder in this workspace is named `new agents` (contains a space). Running scripts from outside that folder can cause import issues; either run commands from inside the folder, add the folder to `PYTHONPATH`, or rename the folder to `new_agents` and add `__init__.py` files.

---

If you'd like, I can also:
- rename the folder to `new_agents` and update imports to package-style,
- add a `.env.example` file,
- add `streamlit` to `requirements.txt`, or
- add a small `scripts/check_config.py` utility that validates environment variables before running.

---

Image (optional): place an `image.png` in the repo and reference it above to include a visual example in the README.

