import os

QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333

COLLECTION = "products"

EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "yandexai")
VECTOR_SIZE = 2560 if EMBED_PROVIDER == 'routerai' else 768