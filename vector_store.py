import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Initialize local embedding model for semantic search
# Utilizing 'all-MiniLM-L6-v2' for optimal local CPU performance and latency
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

DB_DIR = "./chroma_db"

# Configure persistent Chroma vector store for RAG memory
vector_store = Chroma(
    collection_name="workout_history",
    embedding_function=embeddings,
    persist_directory=DB_DIR
)

def save_workout_to_db(user_query: str, workout_plan: str):
    """
    Embeds and persists a generated workout session to local vector storage.
    This allows the agent to maintain historical context and track progressive overload.
    """
    doc = Document(
        page_content=workout_plan,
        metadata={"query": user_query}
    )
    vector_store.add_documents([doc])
    print(f"✅ Workout saved to memory: {user_query}")

def get_past_workouts(user_query: str, k: int = 2) -> str:
    """
    Retrieves the top-k most semantically relevant past workouts
    to inject as context for the agent's current generation cycle.
    """
    results = vector_store.similarity_search(user_query, k=k)
    
    if not results:
        return "No past workouts found."
    
    context = "\n\n".join([f"--- Past Workout ---\n{res.page_content}" for res in results])
    return context