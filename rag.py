from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# Configuration
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore" / "courses"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "gemma4:e2b"


# --------------------------------------------------
# Embeddings and LLM
# --------------------------------------------------
def get_embeddings():
    """Create the embedding model used by the FAISS vector store."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_llm():
    """Create the local Ollama chat model used by the RAG tutor."""
    return ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
        num_ctx=2048,
        num_predict=512,
    )


# --------------------------------------------------
# Vector store loading and indexing
# --------------------------------------------------
def load_vector_store():
    """Load the persisted FAISS index or raise a helpful error if absent."""
    index_file = VECTORSTORE_DIR / "index.faiss"
    metadata_file = VECTORSTORE_DIR / "index.pkl"
    if not index_file.exists() or not metadata_file.exists():
        raise FileNotFoundError(
            f"Aucun index FAISS trouvé dans {VECTORSTORE_DIR}. "
            "Importez un PDF et cliquez sur « Indexer dans FAISS » d'abord."
        )

    return FAISS.load_local(
        str(VECTORSTORE_DIR),
        get_embeddings(),
        # Only load indexes that you created or otherwise trust.
        allow_dangerous_deserialization=True,
    )


def index_text(
    text: str,
    source: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
):
    """Split extracted text, embed it, and add it to the persistent FAISS index."""
    if not text or not text.strip():
        raise ValueError("Le texte extrait est vide ; rien à indexer.")
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Paramètres de découpage invalides.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": source, "chunk_id": i},
        )
        for i, chunk in enumerate(chunks, start=1)
        if chunk.strip()
    ]
    if not documents:
        raise ValueError("Aucun segment exploitable n'a été créé à partir du texte.")

    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings()
    index_file = VECTORSTORE_DIR / "index.faiss"
    metadata_file = VECTORSTORE_DIR / "index.pkl"

    if index_file.exists() and metadata_file.exists():
        vector_store = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        vector_store.add_documents(documents)
    else:
        vector_store = FAISS.from_documents(documents, embeddings)

    vector_store.save_local(str(VECTORSTORE_DIR))
    return len(documents)


# --------------------------------------------------
# Retrieval and context
# --------------------------------------------------
def retrieve_documents(vector_store, question: str, k: int = 5):
    """Retrieve the most relevant course chunks."""
    return vector_store.similarity_search(question, k=k)


def build_context(documents):
    """Combine retrieved chunks into a context with source metadata."""
    context_parts = []
    for i, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        chunk_id = document.metadata.get("chunk_id", "Unknown")
        context_parts.append(
            f"[Document {i}]\nSource: {source}\nChunk: {chunk_id}\n\n"
            f"{document.page_content}"
        )
    return "\n\n".join(context_parts)


# --------------------------------------------------
# Tutor prompt and RAG pipeline
# --------------------------------------------------
def build_tutor_prompt(question: str, context: str):
    """Build a grounded prompt for the course tutor."""
    return f"""
You are a learning tutor assisting a university student.
Answer in the same language as the student's question.
Use ONLY the course context below as factual evidence.
If the context does not contain enough information, say so clearly.
Do not invent information or present outside knowledge as course content.
Explain the answer clearly and pedagogically.

COURSE CONTEXT:
----------------
{context}
----------------

STUDENT QUESTION:
{question}

ANSWER:
"""


def ask_tutor(vector_store, llm, question: str, k: int = 5):
    """Ask a question using retrieval-augmented generation."""
    documents = retrieve_documents(vector_store, question, k=k)
    if not documents:
        return (
            "Je n'ai trouvé aucun passage pertinent dans les documents indexés. "
            "Vérifie que tes cours ont été ajoutés à FAISS.",
            [],
        )

    context = build_context(documents)
    prompt = build_tutor_prompt(question, context)
    response = llm.invoke(prompt)
    return response.content, documents
