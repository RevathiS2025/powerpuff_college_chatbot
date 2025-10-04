import json
import chromadb
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "chromadb_data"
COLLECTION_NAME = "docs"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'


class VectorStore:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=PERSIST_DIR)
            self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            print("VectorStore initialized successfully.")
            print("Collections in DB:", [col.name for col in self.client.list_collections()])
        except Exception as e:
            print(f"Error initializing VectorStore: {e}")
            print("Please ensure you have run the document ingestion script first.")
            self.client = None
            self.collection = None
            self.model = None

    def retrieve_documents(self, query_text: str, user_role: str, n_results: int = 5) -> list[str]:
        if not self.collection or not self.model:
            print("Error: VectorStore is not properly initialized.")
            return []

        query_embedding = self.model.encode(query_text).tolist()

        # ✅ Use Chroma's WHERE filter for direct role filtering (requires roles stored as lists)
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"roles": {"$contains": user_role}}
            )
        except Exception:
            # ✅ Fallback to manual filtering if roles are JSON strings in DB
            raw_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 5
            )
            documents = raw_results.get('documents', [[]])[0]
            metadatas = raw_results.get('metadatas', [[]])[0]

            filtered_docs = []
            for doc, meta in zip(documents, metadatas):
                try:
                    roles_list = json.loads(meta.get("roles", "[]"))
                except json.JSONDecodeError:
                    # fallback if not JSON (comma-separated string)
                    roles_list = [r.strip() for r in meta.get("roles", "").split(",") if r.strip()]

                if user_role in roles_list:
                    filtered_docs.append(doc)
                    if len(filtered_docs) >= n_results:
                        break
            return filtered_docs

        # Directly queried via Chroma filtering
        return results.get('documents', [[]])[0]


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
