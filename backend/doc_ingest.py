
import os
import json
from docx import Document
from sentence_transformers import SentenceTransformer
import chromadb

# -- ROLE MAP --
DOCX_ROLE_MAP = {
    "About_College.docx": ["parent", "dean","student"],
    "Courses_Offered.docx": ["parent", "dean","professor","student"],
    "Fees_Structure.docx": ["parent", "dean","student"],
    "course_syllabus.docx": ["student", "professor", "dean"],
    "Placement_Highlights.docx": ["student", "professor", "dean","parent"],
    "exam_schedule.docx": ["student", "professor", "dean"],
    "Placement_oppurtunities.docx": ["student", "dean","professor","parent"],
    "student_events.docx": ["student", "dean","professor"],
    "Academic_Policies.docx": ["professor", "dean"],
    "Event_coordination.docx": ["professor", "dean"],
    "Exam_evaluation.docx": ["professor", "dean"],
    "Leave_Application.docx": ["professor", "dean"],
    "Administrative_Policies.docx": ["dean"],
    "performance.docx": ["dean"],
    "Strategic_Planning.docx": ["dean"]
}

# -- PARAMETERS --
DOCX_FOLDER = r"D:/Powerpuff/college_genai/data/raw"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
PERSIST_DIR = "chromadb_data"

def extract_text_from_docx(docx_path):
    """Extract text from a .docx file."""
    doc = Document(docx_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def main():
    # Persistent ChromaDB client
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(name="docs")

    # Embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Process each .docx
    for fname in os.listdir(DOCX_FOLDER):
        if fname.lower().endswith(".docx"):
            roles = DOCX_ROLE_MAP.get(fname)
            if not roles:
                print(f"Skipping {fname}: No roles specified in DOCX_ROLE_MAP.")
                continue

            print(f"Processing: {fname} | Roles: {roles}")
            text = extract_text_from_docx(os.path.join(DOCX_FOLDER, fname))
            chunks = chunk_text(text)

            for idx, chunk in enumerate(chunks):
                embedding = model.encode(chunk).tolist()
                doc_id = f"{fname}_{idx}"
                metadata = {
                 "source_file": fname,
                 "chunk_id": idx,
                 "roles": json.dumps(roles)  # store as a Python list
                }
                collection.add(
                    ids=[doc_id],
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[metadata]
                )

    print(f"✅ Ingest complete. Total vectors in DB: {collection.count()}")

if __name__ == "__main__":
    main()
