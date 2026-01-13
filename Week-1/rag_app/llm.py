import ollama
from config import OLLAMA_MODEL

class LLM:
    def generate(self, query: str, context: str) -> str:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer only using the provided context. "
                        "If the answer is not present, say 'I don't know.'"
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{query}"
                }
            ]
        )

        return response["message"]["content"]
