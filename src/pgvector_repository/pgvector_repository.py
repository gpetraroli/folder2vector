from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from sqlalchemy import cast, delete, func
from sqlalchemy.dialects.postgresql import JSONB


class PGVectorRepository:
    def __init__(
        self,
        connection_string: str,
        collection_name: str,
        embeddings: Embeddings,
    ) -> None:
        self.vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

    def embed_documents(self, documents: list[Document]) -> None:
        self.vector_store.add_documents(documents)

    def delete_by_metadata(self, metadata: dict[str, Any]) -> None:
        """Delete rows whose stored metadata contains the provided metadata.

        Extra keys on the row are ignored: ``{"source": "a.md"}`` deletes a row
        with ``{"source": "a.md", "page": 1}``. An empty dict would match every
        row, so it is rejected.
        """
        if not metadata:
            raise ValueError("metadata must be a non-empty dict")

        store = self.vector_store
        with store.session_maker() as session:
            collection = store.get_collection(session)
            if not collection:
                raise ValueError(
                    f"Collection {store.collection_name!r} does not exist"
                )
            session.execute(
                delete(store.EmbeddingStore).where(
                    store.EmbeddingStore.collection_id == collection.uuid,
                    store.EmbeddingStore.cmetadata.op("@>")(cast(metadata, JSONB)),
                )
            )
            session.commit()

    def delete_by_source_prefix(self, directory_source: str) -> None:
        """Delete rows whose ``source`` metadata is under ``directory_source``.

        ``"notes"`` deletes ``notes/a.md`` and ``notes/sub/b.md``, but not
        ``notes_backup/a.md``. A root/empty prefix is rejected so a bad path
        cannot wipe the collection; use ``reset_collection`` for that.
        """
        if not directory_source or directory_source in (".", "/"):
            raise ValueError("directory_source must be a non-root path")

        prefix = directory_source.rstrip("/") + "/"
        store = self.vector_store
        with store.session_maker() as session:
            collection = store.get_collection(session)
            if not collection:
                raise ValueError(
                    f"Collection {store.collection_name!r} does not exist"
                )
            source = store.EmbeddingStore.cmetadata["source"].astext
            session.execute(
                delete(store.EmbeddingStore).where(
                    store.EmbeddingStore.collection_id == collection.uuid,
                    func.starts_with(source, prefix),
                )
            )
            session.commit()

    def reset_collection(self) -> None:
        self.vector_store.delete_collection()
        self.vector_store.create_collection()
