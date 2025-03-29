from langchain.chains import RetrievalQA
from langchain.vectorstores.faiss import FAISS
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_rag_chain(docs):
    """
    Build a Retrieval-Augmented Generation (RAG) chain using the provided documents.
    """
    # Initialize embeddings and vector database
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)
    
    # Create a retriever from the vector database
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Initialize the LLM
    llm = Ollama(model="llama2")
    
    # Build the RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )
    
    return qa
