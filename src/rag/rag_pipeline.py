import os
#import json
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.storage_context import StorageContext
from faiss import IndexFlatL2

# Configuration
DOCS_PATH = "docs/internal_guides"
INDEX_PATH = "rag_index"
EMBED_MODEL_NAME = "BAAI/bge-base-en-v1.5"

# 1. Load and parse internal documents
def load_and_split_documents(docs_path=DOCS_PATH):
    print("Loading internal documents from:", docs_path)
    documents = SimpleDirectoryReader(input_dir=docs_path).load_data()
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)
    return nodes

# 2. Embed and store into FAISS index
def build_vector_index(nodes, persist_path=INDEX_PATH):
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    # Get the actual embedding dimension
    test_embedding = embed_model.get_text_embedding("test")
    embedding_dim = len(test_embedding)
    print(f"Embedding dimension from model: {embedding_dim}")

    # Initialize FAISS index
    faiss_index = IndexFlatL2(embedding_dim)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    print(f"FAISS index dimension: {faiss_index.d}")


    # Build the vector index
    index = VectorStoreIndex(nodes, embed_model=embed_model, storage_context=storage_context)
    if not os.path.exists(persist_path):
        os.makedirs(persist_path)
    index.storage_context.persist(persist_path)
    print("RAG index built and persisted at:", persist_path)

# Entry point to create RAG vector index
def build_rag_index():
    nodes = load_and_split_documents()
    build_vector_index(nodes)


if __name__ == "__main__":
    build_rag_index()
    print("RAG pipeline completed successfully.")
