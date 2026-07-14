import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain AI in one line"}
    ]
)

print(response.choices[0].message.content)

# Auto code generation is vs code default? pleae answser yes or no  
