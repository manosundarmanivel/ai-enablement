from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]):
        return self.model.encode(texts)
