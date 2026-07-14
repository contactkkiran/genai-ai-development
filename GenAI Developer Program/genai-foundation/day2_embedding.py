import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Dog"
)
# print("Embedding Vector:", response.data[0].embedding)

print(response.data[0].embedding[:5])

print('------------------')
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Puppy"
)
# print("Embedding Vector:", response.data[0].embedding)

print(response.data[0].embedding[:5])