from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff, PointStruct
from embeddings import EmbeddingModel
from config import VECTOR_DB_PATH, COLLECTION_NAME
import uuid

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(path=VECTOR_DB_PATH)
        self.embedder = EmbeddingModel()

        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedder.dimension,
                    distance=Distance.COSINE
                ),
                hnsw_config=HnswConfigDiff(
                    m=32,
                    ef_construct=200
                )
            )

    def upsert(self, texts: list[str], metadata: dict):
        vectors = self.embedder.embed(texts)
        points = []

        for text, vector in zip(texts, vectors):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "text": text,
                    **metadata
                }
            ))

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
