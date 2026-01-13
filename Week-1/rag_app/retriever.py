from embeddings import EmbeddingModel
from vector_store import VectorStore
from config import COLLECTION_NAME, TOP_K, HNSW_EF_SEARCH

class Retriever:
    def __init__(self):
        self.store = VectorStore()
        self.embedder = EmbeddingModel()

    def retrieve(self, query: str) -> str:
        query_vector = self.embedder.embed([query])[0].tolist()

        results = self.store.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=TOP_K,
            search_params={"hnsw_ef": HNSW_EF_SEARCH}
        )

        return "\n\n".join(point.payload["text"] for point in results.points)
