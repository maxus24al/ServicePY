from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding 
from qdrant_client.models import Distance, VectorParams, TextIndexParams, TokenizerType
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION,
    VECTOR_SIZE,
)

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)
sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")

print(sparse_model)


def create_collection():
    if client.collection_exists(COLLECTION):
        return

    client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "name": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "type": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "description": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "image": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        },
        sparse_vectors_config={
                "text_sparse": models.SparseVectorParams(
                     modifier=models.Modifier.LEXICAL
                )
            }
    )
    
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="description",
        field_schema=TextIndexParams(
            type="text",
            tokenizer=TokenizerType.WORD,
            min_token_len = 2,
            max_token_len = 20,
            lowercase = True
        )
    )

    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="name",
        field_schema=TextIndexParams(
            type="text",
            tokenizer=TokenizerType.WORD,
            min_token_len = 2,
            max_token_len = 20,
            lowercase = True
        )
    )

    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="type",
        field_schema=TextIndexParams(
            type="text",
            tokenizer=TokenizerType.WORD,
            min_token_len = 2,
            max_token_len = 20,
            lowercase = True
        )
    )
    
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="type_keyword",
        field_schema=models.PayloadSchemaType.KEYWORD
    )