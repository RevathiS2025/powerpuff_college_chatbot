import json
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List
from backend.rbac import get_accessible_roles


PERSIST_DIR = "chromadb_data"
COLLECTION_NAME = "docs"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
RE_RANK_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'




class VectorStore:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=PERSIST_DIR)
            self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.cross_encoder = None  # Lazy-init re-ranker when first used
            print("VectorStore initialized successfully.")
            print("Collections in DB:", [col.name for col in self.client.list_collections()])
        except Exception as e:
            print(f"Error initializing VectorStore: {e}")
            print("Please ensure you have run the document ingestion script first.")
            self.client = None
            self.collection = None
            self.model = None


    def _ensure_re_ranker(self):
        if self.cross_encoder is None:
            try:
                self.cross_encoder = CrossEncoder(RE_RANK_MODEL)
            except Exception as e:
                print(f"Warning: failed to load re-ranker ({RE_RANK_MODEL}): {e}")
                self.cross_encoder = None


    def retrieve_documents(self, query_text: str, user_role: str, n_results: int = 5, fetch_k: int = 20) -> List[str]:
        if not self.collection or not self.model:
            print("Error: VectorStore is not properly initialized.")
            return []


        query_embedding = self.model.encode(query_text).tolist()
        # Expand accessible roles using RBAC hierarchy
        accessible_roles = get_accessible_roles(user_role) or [user_role]


        # Pull a larger candidate set, include distances and metadatas
        raw_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances"]
        )


        documents = raw_results.get('documents', [[]])[0]
        metadatas = raw_results.get('metadatas', [[]])[0]
        distances = raw_results.get('distances', [[]])[0]


        # Filter by role intersection
        candidates = []  # (doc, distance)
        for doc, meta, dist in zip(documents, metadatas, distances):
            roles_field = meta.get("roles", [])
            if isinstance(roles_field, str):
                try:
                    roles_list = json.loads(roles_field)
                except json.JSONDecodeError:
                    roles_list = [r.strip() for r in roles_field.split(',') if r.strip()]
            else:
                roles_list = roles_field


            if any(r in roles_list for r in accessible_roles):
                candidates.append((doc, dist))


        if not candidates:
            return []


        # Re-rank with cross-encoder if available, else sort by distance
        self._ensure_re_ranker()
        if self.cross_encoder is not None:
            pairs = [(query_text, doc) for doc, _ in candidates]
            try:
                scores = self.cross_encoder.predict(pairs)
                # Sort by score descending
                ranked = [doc for (doc, _), _score in sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)]
            except Exception as e:
                print(f"Warning: re-ranking failed: {e}. Falling back to distance.")
                ranked = [doc for doc, dist in sorted(candidates, key=lambda x: x[1])]  # lower distance is better
        else:
            ranked = [doc for doc, dist in sorted(candidates, key=lambda x: x[1])]  # lower distance is better


        return ranked[:n_results]




if __name__ == '__main__':
    print("Running VectorStore test...")
    vector_store = VectorStore()


    if vector_store.collection:
        print("\n--- Testing as 'student' ---")
        q = "What is the course syllabus for engineering?"
        student_docs = vector_store.retrieve_documents(q, "student")
        print(f"Query: '{q}' | Role: 'student'")
        for i, doc in enumerate(student_docs, 1):
            print(f"  {i}. {doc[:120]}...")


        print("\n--- Testing as 'parent' ---")
        parent_docs = vector_store.retrieve_documents(q, "parent")
        print(f"Query: '{q}' | Role: 'parent'")
        if not parent_docs:
            print("✅ No documents found for 'parent' — correct behavior.")
        else:
            print("⚠ WARNING: Retrieved docs for 'parent', check role mapping:")
            for i, doc in enumerate(parent_docs, 1):
                print(f"  {i}. {doc[:120]}...")
    else:
        print("\nCould not run tests. Is the `chromadb_data` directory available?")