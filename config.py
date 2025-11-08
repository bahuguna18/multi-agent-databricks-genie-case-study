"""
Local config for the `new agents` utilities.

This file centralizes API host, token and space IDs for the Genie clients.
It prefers values from environment variables (and a .env file if present)
but provides sensible defaults so the repository remains runnable.

Set values via environment variables or edit this file if you prefer hardcoding
for local development (not recommended for production).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Databricks / Genie configuration
DATABRICKS_HOST = os.getenv(
    "DATABRICKS_HOST"
)
DATABRICKS_TOKEN = os.getenv(
    "DATABRICKS_TOKEN"
)
SALES_GENIE_SPACE_ID = os.getenv("SALES_GENIE_SPACE_ID")
CUSTOMER_GENIE_SPACE_ID = os.getenv("CUSTOMER_GENIE_SPACE_ID")

# # --- INIT CLIENT ---
# client = OpenAI(api_key=OPENAI_API_KEY)
# OpenAI / LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# General agent settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

def validate_config(allow_empty_openai=False):
    """Validate presence of key configuration values.

    By default require Databricks host, token and both space IDs. If
    allow_empty_openai is True, OPENAI_API_KEY may be empty (useful for
    offline runs that don't call OpenAI).
    """
    missing = []
    if not DATABRICKS_HOST:
        missing.append("DATABRICKS_HOST")
    if not DATABRICKS_TOKEN:
        missing.append("DATABRICKS_TOKEN")
    if not SALES_GENIE_SPACE_ID:
        missing.append("SALES_GENIE_SPACE_ID")
    if not CUSTOMER_GENIE_SPACE_ID:
        missing.append("CUSTOMER_GENIE_SPACE_ID")
    if not allow_empty_openai and not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")

    if missing:
        raise ValueError(f"Missing required config values: {', '.join(missing)}")

    return True
