# 🚀 1. Basic Prompt (Zero-shot)

# 👉 No examples, just instruction
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))