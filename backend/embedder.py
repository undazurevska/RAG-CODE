from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.vector_store import VectorDB

# Initialize the vector database
vector_db = VectorDB(filename="vectors.json")
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def embed_documents(texts):
    # Split the documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(texts)

    # Generate embeddings for each document
    embeddings = embeddings_model.embed_documents([doc.page_content for doc in docs])
    
    # Add embeddings and texts to the vector database
    vector_db.add_vectors([doc.page_content for doc in docs], embeddings)

    return embeddings, docs
    