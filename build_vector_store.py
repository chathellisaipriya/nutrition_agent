from rag.document_loader import load_documents, split_documents
from rag.vector_store import build_vector_store

print("Loading documents...")
docs = load_documents()

print(f"Loaded {len(docs)} documents")

print("Splitting documents...")
chunks = split_documents(docs)

print(f"Created {len(chunks)} chunks")

print("Building FAISS index...")
build_vector_store(chunks)

print("✅ FAISS index created successfully!")