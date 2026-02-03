import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_KEY = os.getenv("OPEN_API_KEY")
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMP = 0.5