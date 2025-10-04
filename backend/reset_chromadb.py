
#!/usr/bin/env python3
"""
Fixed script to completely reset ChromaDB storage and re-ingest documents.
"""

import os
import shutil
import sys
from pathlib import Path

def reset_chromadb():
    """Remove existing ChromaDB storage completely."""
    
    PERSIST_DIR = "chromadb_data"
    
    print("🗑️  RESETTING CHROMADB STORAGE")
    print("=" * 50)
    
    # Check if directory exists
    if os.path.exists(PERSIST_DIR):
        try:
            # Remove the entire directory and all contents
            shutil.rmtree(PERSIST_DIR)
            print(f"✅ Successfully removed existing ChromaDB data at: {PERSIST_DIR}")
        except Exception as e:
            print(f"❌ Error removing ChromaDB data: {e}")
            return False
    else:
        print(f"ℹ️  No existing ChromaDB data found at: {PERSIST_DIR}")
    
    return True

def verify_documents():
    """Check if raw documents exist before ingestion."""
    
    raw_path = Path("data/raw")
    
    if not raw_path.exists():
        print(f"❌ Raw data directory not found: {raw_path}")
        return False
    
    docx_files = list(raw_path.glob("*.docx"))
    
    if not docx_files:
        print(f"❌ No .docx files found in: {raw_path}")
        print("Please add your Word documents to data/raw/ before running ingestion.")
        return False
    
    print(f"📄 Found {len(docx_files)} .docx files:")
    for file in docx_files:
        print(f"   - {file.name}")
    
    return True

def run_ingestion_directly():
    """Run the document ingestion process directly without imports."""
    
    print("\n📥 STARTING DOCUMENT INGESTION")
    print("=" * 50)
    
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(current_dir))
        
        # Direct ingestion code (copied from your document_ingest.py)
        import os
        from docx import Document
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings

        # Parameters
        DOCX_FOLDER = "data/raw"
        CHUNK_SIZE = 500
        CHUNK_OVERLAP = 100
        PERSIST_DIR = "chromadb_data"

        # UPDATE THIS MAPPING WITH YOUR ACTUAL FILES AND ROLES
        DOCX_ROLE_MAP = {
            "college_overview.docx": ["parent", "dean"],
            "placement_records.docx": ["parent", "student", "dean"],
            "course_syllabus.docx": ["student", "professor", "dean"],
            "courses_offered.docx": ["parent", "dean"],  # Make sure this exists!
            "academic_policies.docx": ["professor", "dean"],
            "fee_structure.docx": ["parent", "dean"],
            # Add your actual file names here
        }

        def extract_text_from_docx(docx_path):
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text

        def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                chunks.append(chunk)
                start += chunk_size - overlap
            return chunks

        # Initialize ChromaDB
        client = chromadb.Client(Settings(persist_directory=PERSIST_DIR))
        collection = client.get_or_create_collection("docs")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        processed_count = 0
        
        for fname in os.listdir(DOCX_FOLDER):
            if fname.lower().endswith('.docx'):
                docx_path = os.path.join(DOCX_FOLDER, fname)
                roles = DOCX_ROLE_MAP.get(fname)
                
                if not roles:
                    print(f"⚠️  Skipping {fname}: No roles specified in DOCX_ROLE_MAP.")
                    continue

                print(f"📄 Processing: {fname} | Roles: {roles}")
                text = extract_text_from_docx(docx_path)
                
                if not text.strip():
                    print(f"⚠️  Warning: {fname} appears to be empty!")
                    continue
                
                chunks = chunk_text(text)
                print(f"   Created {len(chunks)} chunks")
                
                for idx, chunk in enumerate(chunks):
                    if chunk.strip():  # Only process non-empty chunks
                        embedding = model.encode(chunk).tolist()
                        doc_id = f"{fname}_{idx}"
                        metadata = {
                            "source_file": fname,
                            "chunk_id": idx,
                            "roles": roles
                        }
                        collection.add(
                            ids=[doc_id],
                            documents=[chunk],
                            embeddings=[embedding],
                            metadatas=[metadata]
                        )
                
                processed_count += 1
        
        # Persist the data
        client.persist()
        print(f"✅ Successfully processed {processed_count} documents!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install: pip install python-docx sentence-transformers chromadb")
        return False
        
    except Exception as e:
        print(f"❌ Document ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_new_data():
    """Verify that new data was created successfully."""
    
    print("\n🔍 VERIFYING NEW CHROMADB DATA")
    print("=" * 50)
    
    PERSIST_DIR = "chromadb_data"
    
    if not os.path.exists(PERSIST_DIR):
        print(f"❌ ChromaDB data directory was not created: {PERSIST_DIR}")
        return False
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.Client(Settings(persist_directory=PERSIST_DIR))
        collection = client.get_collection("docs")
        
        # Get count of documents
        results = collection.get()
        doc_count = len(results['ids'])
        
        print(f"✅ ChromaDB collection created successfully!")
        print(f"📊 Total document chunks stored: {doc_count}")
        
        # Show available roles
        all_roles = set()
        role_counts = {}
        
        for metadata in results['metadatas']:
            roles = metadata.get('roles', [])
            all_roles.update(roles)
            for role in roles:
                role_counts[role] = role_counts.get(role, 0) + 1
        
        print(f"🎭 Available roles: {sorted(all_roles)}")
        print("📈 Documents per role:")
        for role, count in sorted(role_counts.items()):
            print(f"   - {role}: {count} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying ChromaDB data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CHROMADB RESET AND REINGEST TOOL")
    print("=" * 60)
    
    # Check current directory structure
    print(f"📁 Current directory: {Path.cwd()}")
    print(f"📁 Backend exists: {Path('backend').exists()}")
    print(f"📁 Data/raw exists: {Path('data/raw').exists()}")
    
    # Step 1: Verify documents exist
    if not verify_documents():
        print("\n⚠️  Please add .docx files to data/raw/ and try again.")
        sys.exit(1)
    
    # Step 2: Ask for confirmation
    response = input("\n⚠️  This will DELETE all existing ChromaDB data. Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Operation cancelled.")
        sys.exit(0)
    
    # Step 3: Reset ChromaDB
    if not reset_chromadb():
        print("Failed to reset ChromaDB. Exiting.")
        sys.exit(1)
    
    # Step 4: Run ingestion
    if not run_ingestion_directly():
        print("Failed to run document ingestion. Exiting.")
        sys.exit(1)
    
    # Step 5: Verify new data
    if not verify_new_data():
        print("Warning: Could not verify new ChromaDB data.")
    
    print("\n🎉 RESET AND REINGEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("You can now test your RAG chatbot with fresh data.")
