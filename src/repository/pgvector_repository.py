from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import delete as sql_delete

from folder2vector.config import DB_CONNECTION, EMBEDDING_MODEL, OLLAMA_URL


class PGVectorRepository:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="documents",
            connection=DB_CONNECTION,
            use_jsonb=True,
        )

    def embed_documents(self, documents: list[Document]):
        self.vector_store.add_documents(documents)
    
    def delete_existing_chunks(self, file_path: str) -> None:
        with self.vector_store._make_sync_session() as session:
            collection = self.vector_store.get_collection(session)
            if collection is None:
                return
            session.execute(
                sql_delete(self.vector_store.EmbeddingStore).where(
                    self.vector_store.EmbeddingStore.collection_id == collection.uuid,
                    self.vector_store.EmbeddingStore.cmetadata.contains({"source": file_path}),
                )
            )
            session.commit()
