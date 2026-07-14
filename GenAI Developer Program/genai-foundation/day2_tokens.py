# text = 'I love GenAI'
# tokens = text.split()
# print('Lenth of Tokens :' + str(len(tokens)))

import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

text = "I love GenAI"

tokens = encoding.encode(text)

print("Token IDs:", tokens)
print("Token count:", len(tokens))