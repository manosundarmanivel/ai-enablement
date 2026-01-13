from ingest import ingest_pdf
from rag_pipeline import RAGPipeline

if __name__ == "__main__":
    # Ingest once
    ingest_pdf("data/documents/sample.pdf")

    rag = RAGPipeline()

    while True:
        query = input("\nAsk a question (or 'exit'): ")
        if query.lower() == "exit":
            break

        answer = rag.run(query)
        print("\nAnswer:\n", answer)
