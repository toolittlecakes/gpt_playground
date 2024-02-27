import os
from dotenv import load_dotenv

load_dotenv()

LLM_REPORT_API_KEY: str = os.getenv("LLM_REPORT_API_KEY") # type: ignore
LUNARY_APP_ID: str = os.getenv("LUNARY_APP_ID") # type: ignore
