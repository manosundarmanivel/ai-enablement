"""
RAG Tool for HR Policy Document Search and Retrieval
Uses FAISS for vector storage and AWS Bedrock embeddings
"""

from pathlib import Path
from langchain_core.tools import tool
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Paths - Week-4/data/ is two levels up from rag_tool/rag_tool.py
WEEK4_DIR = Path(__file__).parent.parent.parent
DOCS_PATH = WEEK4_DIR / "data" / "hr_policies"
VECTOR_STORE_PATH = WEEK4_DIR / "data" / "vector_store"

# Global vector store
_vector_store = None


def get_vector_store():
    """Get or create the vector store."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

    # Check if vector store exists
    if VECTOR_STORE_PATH.exists():
        print("[RAG] Loading existing vector store...")
        _vector_store = FAISS.load_local(
            str(VECTOR_STORE_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("[RAG] Creating new vector store...")
        _vector_store = create_vector_store(embeddings)

    return _vector_store


def create_vector_store(embeddings):
    """Create vector store from HR policy documents."""
    # Load documents
    loader = DirectoryLoader(
        str(DOCS_PATH),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()

    print(f"[RAG] Loaded {len(documents)} documents")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    splits = text_splitter.split_documents(documents)

    print(f"[RAG] Created {len(splits)} chunks")

    # Create vector store
    vector_store = FAISS.from_documents(splits, embeddings)

    # Save for future use
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(VECTOR_STORE_PATH))

    print(f"[RAG] Vector store saved to {VECTOR_STORE_PATH}")

    return vector_store


def vectorize_documents():
    """Manually vectorize documents (run before using the agent)."""
    global _vector_store

    print("=" * 50)
    print("Vectorizing HR Policy Documents")
    print("=" * 50)

    # Clear existing
    if VECTOR_STORE_PATH.exists():
        import shutil
        shutil.rmtree(VECTOR_STORE_PATH)
        print("[RAG] Cleared existing vector store")

    _vector_store = None
    embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
    _vector_store = create_vector_store(embeddings)

    print("\nVectorization complete!")
    return _vector_store


@tool
def search_hr_policies(query: str) -> str:
    """
    Search Presidio's HR Policy documents for information.

    Use this tool to find information about:
    - Employee handbook and workplace policies
    - AI and data handling compliance policies
    - Hiring and recruitment policies and metrics
    - Customer feedback reports and marketing campaign results
    - PTO, benefits, compensation information
    - Training and professional development

    Args:
        query: Natural language question about HR policies

    Returns:
        Relevant excerpts from HR policy documents
    """
    try:
        vector_store = get_vector_store()

        # Search for relevant documents
        docs = vector_store.similarity_search(query, k=4)

        if not docs:
            return "No relevant HR policy documents found."

        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            source = Path(doc.metadata.get("source", "Unknown")).name
            content = doc.page_content.strip()
            results.append(f"**Source {i}: {source}**\n{content}")

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"Error searching HR policies: {str(e)}"


def get_rag_tools():
    """Return RAG tools for use with LangChain agent."""
    return [search_hr_policies]
