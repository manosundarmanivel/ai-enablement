from pypdf import PdfReader
from chunking import chunk_text
from vector_store import VectorStore

def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)

def ingest_pdf(path: str):
    print(f"Ingesting document: {path}")

    text = load_pdf(path)
    chunks = chunk_text(text)

    store = VectorStore()
    store.upsert(
        texts=chunks,
        metadata={"source": path}
    )

    print(f"Successfully ingested {len(chunks)} chunks.")


if __name__ == "__main__":
    ingest_pdf("data/documents/sample.pdf")
