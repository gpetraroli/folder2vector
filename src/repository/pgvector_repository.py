import json

import psycopg
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from folder2vector.config import (
    COLLECTION_NAME,
    DB_CONNECTION,
    EMBEDDING_MODEL,
    OLLAMA_URL,
)


def _psycopg_conninfo(sqlalchemy_url: str) -> str:
    url = sqlalchemy_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


class PGVectorRepository:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=COLLECTION_NAME,
            connection=DB_CONNECTION,
            use_jsonb=True,
        )
        self._conninfo = _psycopg_conninfo(DB_CONNECTION)

    def embed_documents(self, documents: list[Document]):
        self.vector_store.add_documents(documents)

    def delete_existing_chunks(self, file_path: str) -> None:
        with psycopg.connect(self._conninfo) as connection:
            connection.execute(
                """
                DELETE FROM langchain_pg_embedding AS e
                USING langchain_pg_collection AS c
                WHERE e.collection_id = c.uuid
                    AND c.name = %s
                    AND e.cmetadata @> %s::jsonb
                """,
                (COLLECTION_NAME, json.dumps({"source": file_path})),
            )

    def reset_collection(self) -> None:
        self.vector_store.delete_collection()
        self.vector_store.create_tables_if_not_exists()
        self.vector_store.create_collection()
