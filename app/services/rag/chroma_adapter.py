from typing import List, Dict, Any, Optional
import chromadb

class ChromaAdapter:
    """
    Adapter for ChromaDB interactions.
    """

    def __init__(self, collection_name: str = "default"):
        self._client = chromadb.Client()
        self._collection_name = collection_name
        self._collection = self._get_or_create_collection(collection_name)

    def _get_or_create_collection(self, name: str):
        try:
            return self._client.get_collection(name)
        except ValueError:
            return self._client.create_collection(name)

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Add documents with metadata.
        """
        self._collection.add(docs)

    def query(self, query_vector: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        return self._collection.query(query_vector=query_vector, n_results=n_results)