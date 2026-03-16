# config.py
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct")
API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")

# Exam size (you asked for 60 question full mocks)
EXAM_SIZE = int(os.getenv("EXAM_SIZE", "60"))
