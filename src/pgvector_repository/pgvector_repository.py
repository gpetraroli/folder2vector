from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from sqlalchemy import delete


class PGVectorRepository:
    def __init__(
        self,
        connection_string: str,
        collection_name: str,
        embeddings: Embeddings,
    ) -> None:
        self.embeddings = embeddings

        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

    def embed_documents(self, documents: list[Document]):
        self.vector_store.add_documents(documents)

    def delete_by_metadata(self, metadata: dict) -> None:
        store = self.vector_store
        with store._make_sync_session() as session:
            collection = store.get_collection(session)
            if not collection:
                return
            session.execute(
                delete(store.EmbeddingStore).where(
                    store.EmbeddingStore.collection_id == collection.uuid,
                    store.EmbeddingStore.cmetadata.contains(metadata),
                )
            )
            session.commit()

    def reset_collection(self) -> None:
        self.vector_store.delete_collection()
        self.vector_store.create_tables_if_not_exists()
        self.vector_store.create_collection()
