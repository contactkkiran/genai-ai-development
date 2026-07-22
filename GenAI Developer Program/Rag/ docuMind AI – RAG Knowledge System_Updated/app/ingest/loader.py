import os
from typing import TypedDict, Union

import pymupdf


class RawDocument(TypedDict):
    content: str
    metadata: dict[str, Union[int, str]]


def load_all_pdfs(folder_path: str) -> list[RawDocument]:
    docs = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)

            try:
                pdf = pymupdf.open(path)

                for page_num in range(pdf.page_count):
                    page = pdf.load_page(page_num)
                    text = page.get_text("text")

                    if not isinstance(text, str):
                        text = str(text)

                    # Skip empty pages
                    if not text.strip():
                        continue

                    docs.append({
                        "content": text,
                        "metadata": {
                            "source": file,
                            "page": page_num
                        }
                    })

                pdf.close()

            except Exception as e:
                print(f"Error processing {file}: {e}")

    return docs
