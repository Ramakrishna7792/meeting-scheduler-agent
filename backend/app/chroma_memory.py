# backend/app/chroma_memory.py
import chromadb
from typing import Optional
try:
    from langchain_openai import OpenAIEmbeddings
except Exception:
    OpenAIEmbeddings = None

class MemoryStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("memory")
        self.embedder = None

    def _ensure_embedder(self):
        if self.embedder is None:
            if OpenAIEmbeddings is None:
                raise RuntimeError("OpenAIEmbeddings not available (ok for demo).")
            self.embedder = OpenAIEmbeddings()

    def add_memory(self, user_id: str, text: str):
        try:
            self._ensure_embedder()
            emb = self.embedder.embed_documents([text])[0]
            self.collection.add(ids=[f"{user_id}_{len(text)}"], documents=[text], embeddings=[emb], metadatas=[{"user_id": user_id}])
        except Exception:
            self.collection.add(ids=[f"{user_id}_{len(text)}_noembed"], documents=[text], metadatas=[{"user_id": user_id, "note": "no-embed"}])

    def query_memory(self, user_id: str, query: str):
        try:
            self._ensure_embedder()
            emb = self.embedder.embed_documents([query])[0]
            res = self.collection.query(query_embeddings=[emb], n_results=3)
            return res
        except Exception:
            return self.collection.query(query_texts=[query], n_results=3)
