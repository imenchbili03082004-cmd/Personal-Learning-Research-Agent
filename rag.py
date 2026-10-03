from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore" / "courses"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OLLAMA_MODEL = "gemma4:31b-cloud"

OLLAMA_BASE_URL = "https://api.ollama.com"


# --------------------------------------------------
# Embeddings
# --------------------------------------------------

def get_embeddings():
    """
    Create the embedding model used by the FAISS vector store.
    """
    
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# --------------------------------------------------
# Vector store
# --------------------------------------------------

def load_vector_store():
    """
    Load the persisted FAISS vector store.
    """
    
    embeddings = get_embeddings()
    
    return FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )


# --------------------------------------------------
# Retrieval
# --------------------------------------------------

def retrieve_documents(
    vector_store,
    question: str,
    k: int = 5
):
    """
    Retrieve the most relevant course documents.
    """
    
    return vector_store.similarity_search(
        question,
        k=k
    )


# --------------------------------------------------
# Context
# --------------------------------------------------

def build_context(documents):
    """
    Combine retrieved documents into a single context.
    """
    
    context_parts = []
    
    for i, document in enumerate(documents, start=1):
        source = document.metadata.get(
            "source",
            "Unknown source"
        )
        
        chunk_id = document.metadata.get(
            "chunk_id",
            "Unknown"
        )
        
        context_parts.append(
            f"[Document {i}]\n"
            f"Source: {source}\n"
            f"Chunk: {chunk_id}\n\n"
            f"{document.page_content}"
        )
    
    return "\n\n".join(context_parts)


# --------------------------------------------------
# LLM
# --------------------------------------------------

def get_llm():
    """
    Create the Ollama Cloud LLM.
    """
    
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0
    )


# --------------------------------------------------
# Tutor prompt
# --------------------------------------------------

def build_tutor_prompt(
    question: str,
    context: str
):
    """
    Build the prompt for the RAG Tutor.
    """
    
    return f"""
You are a learning tutor assisting a student.

Your task is to answer the student's question using
the provided course context.

IMPORTANT RULES:

1. Use the course context as the primary source.
2. Do not invent information that is not supported
   by the context.
3. If the answer cannot be found in the context,
   clearly say that the information is not available
   in the provided course material.
4. Explain the answer clearly and pedagogically.
5. Do not present external knowledge as if it came
   from the course.

COURSE CONTEXT:
----------------
{context}
----------------

STUDENT QUESTION:
{question}

ANSWER:
"""


# --------------------------------------------------
# Tutor
# --------------------------------------------------

def ask_tutor(
    vector_store,
    llm,
    question: str,
    k: int = 5
):
    """
    Ask a question using the RAG Tutor pipeline.
    """
    
    documents = retrieve_documents(
        vector_store,
        question,
        k=k
    )
    
    context = build_context(documents)
    
    prompt = build_tutor_prompt(
        question,
        context
    )
    
    response = llm.invoke(prompt)
    
    return response.content, documents