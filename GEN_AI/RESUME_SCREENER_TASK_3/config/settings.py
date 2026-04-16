import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

MODEL_REPO = "mistralai/Mistral-7B-Instruct-v0.2"

MODEL_CONFIG = {
    "temperature": 0.1,
    "max_new_tokens": 512,
}