import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. Initialize the open-source embedding model (runs locally)
# "all-MiniLM-L6-v2" is highly efficient and perfect for semantic search
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Define the local storage directory for the database
DB_DIR = "./chroma_db"

# 3. Initialize the Chroma Vector Store
vector_store = Chroma(
    collection_name="workout_history",
    embedding_function=embeddings,
    persist_directory=DB_DIR
)

def save_workout_to_db(user_query: str, workout_plan: str):
    """Embeds and saves a completed workout session to persistent memory."""
    doc = Document(
        page_content=workout_plan,
        metadata={"query": user_query}
    )
    vector_store.add_documents([doc])
    print(f"✅ Workout saved to memory: {user_query}")

def get_past_workouts(user_query: str, k: int = 2) -> str:
    """Retrieves the most semantically relevant past workouts."""
    results = vector_store.similarity_search(user_query, k=k)
    
    if not results:
        return "No past workouts found."
    
    context = "\n\n".join([f"--- Past Workout ---\n{res.page_content}" for res in results])
    return context