"""
Configuration file for the Multi-Agent Databricks Genie System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Databricks Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
SALES_GENIE_SPACE_ID = os.getenv("SALES_GENIE_SPACE_ID", "")
CUSTOMER_GENIE_SPACE_ID =  os.getenv("CUSTOMER_GENIE_SPACE_ID", "")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Agent Configuration 
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TIMEOUT = 30  # seconds

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

required_vars = {
    "DATABRICKS_HOST": DATABRICKS_HOST,
    "DATABRICKS_TOKEN": DATABRICKS_TOKEN,
    "SALES_GENIE_SPACE_ID": SALES_GENIE_SPACE_ID,
    "CUSTOMER_GENIE_SPACE_ID": CUSTOMER_GENIE_SPACE_ID,
    "OPENAI_API_KEY": OPENAI_API_KEY
}

def validate_config():
    """Validate that all required configuration variables are set"""
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set them in your .env file or environment."
        )
    return True

