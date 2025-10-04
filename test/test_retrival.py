import chromadb

# Path where your ingestion script saved Chroma data
PERSIST_DIR = "chromadb_data"

# Connect to existing ChromaDB
client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(name="docs")

# Print how many items are stored
print(f"Total stored vectors: {collection.count()}")

# Retrieve a few to see what's inside
results = collection.get(
    include=["documents", "embeddings", "metadatas"],  # include embeddings
    limit=2
)

for i in range(len(results["ids"])):
    print("\n--- Document", i+1, "---")
    print("ID:", results["ids"][i])
    print("Text Chunk:", results["documents"][i])
    print("Embedding length:", len(results["embeddings"][i]))
    print("Metadata:", results["metadatas"][i])

# Example similarity search
query = "exam schedule"
search_results = collection.query(
    query_texts=[query],
    n_results=3
)

print("\nTop matches for query:", query)
for doc, meta in zip(search_results["documents"][0], search_results["metadatas"][0]):
    print(f"- {doc[:60]}... | Roles: {meta['roles']}")
