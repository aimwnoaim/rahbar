"""The real retriever. Yours to build (sections 3.2 and 4.4).

Connection details are already here; the query is not.
"""

from __future__ import annotations

from ..config import Settings
from ..embedding import embed_query
from ..schemas import Passage


class ChromaRetriever:
    name = "chroma"

    def __init__(self, settings: Settings) -> None:
        import chromadb  # the thin client, from chromadb-client in requirements.txt
        from chromadb.config import Settings as ChromaSettings

        self.settings = settings
        self.client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port,
                                          settings=ChromaSettings(anonymized_telemetry=False))

    def retrieve(
        self, question: str, k: int, query_embedding: list[float] | None = None
    ) -> list[Passage]:
        collection = self.active_collection()
        vector = query_embedding or embed_query(question, self.settings)
        where = None if _asks_for_older_version(question) else {"superseded": False}
        result = collection.query(
            query_embeddings=[vector],
            n_results=max(1, k),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        ids = (result.get("ids") or [[]])[0]
        texts = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        passages = []
        for chunk_id, text, metadata, distance in zip(ids, texts, metadatas, distances):
            if not metadata or text is None or distance is None:
                continue
            passages.append(Passage(
                chunk_id=str(chunk_id),
                text=str(text),
                source=str(metadata.get("source", "unknown")),
                section=str(metadata.get("section", "unknown")),
                page=int(metadata["page"]) if metadata.get("page") is not None else None,
                score=max(-1.0, min(1.0, 1.0 - float(distance))),
            ))
        return passages

    def active_collection(self):  # type annotation omitted for Chroma's dynamic client type
        """Resolve the published generation, falling back to the starter dummy collection."""
        registry_name = f"{self.settings.collection[:40]}-registry"
        try:
            registry = self.client.get_collection(registry_name)
            active = (registry.metadata or {}).get("active_collection")
            if active:
                return self.client.get_collection(str(active))
        except Exception:
            pass
        return self.client.get_collection(self.settings.collection)

    def cache_revision(self) -> str:
        collection = self.active_collection()
        return str((collection.metadata or {}).get("index_revision", collection.name))


def _asks_for_older_version(question: str) -> bool:
    """Allow superseded chunks only when the question explicitly asks historically."""
    import re

    return bool(re.search(
        r"\b(older|old|previous|prior|superseded|historical|before\s+20\d{2}|20\d{2}\s+version)\b",
        question,
        re.IGNORECASE,
    ))
