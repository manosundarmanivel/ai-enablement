from retriever import Retriever
from llm import LLM

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = LLM()

    def run(self, query: str) -> str:
        context = self.retriever.retrieve(query)
        return self.llm.generate(query, context)
