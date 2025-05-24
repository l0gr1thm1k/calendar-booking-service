import os

from dotenv import load_dotenv

load_dotenv()

CHAT_INSTANCES_TO_HOLD = 4
INPUT_CHARACTER_LIMIT = 500
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL")