import os
from google import genai
from dotenv import load_dotenv
import chromadb
from gemini_helper import safe_generate

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Connect to your existing ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="pulseiq_documents")


def get_embedding(text):
    """Convert a question into a vector, same way we embedded the documents."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def search_documents(question, n_results=5):
    """
    Step 1: Convert the question into a vector, then find the 
    most similar chunks in ChromaDB (policy docs + reviews).
    """
    question_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )

    # Pull out the actual text chunks and their sources
    chunks = results['documents'][0]
    sources = [meta['source'] for meta in results['metadatas'][0]]

    return chunks, sources


def answer_from_documents(question):
    """
    Step 2: Give Gemini the retrieved chunks and ask it to answer
    using ONLY that information - this is the core RAG pattern.
    """
    chunks, sources = search_documents(question)

    # Build context from retrieved chunks, labeled by source
    context = "\n\n".join([f"[Source: {src}]\n{chunk}" for chunk, src in zip(chunks, sources)])

    prompt = f"""You are a business analyst assistant. Answer the user's question 
using ONLY the information in the context below. If the context doesn't contain 
enough information to answer, say so clearly - do not make up information.

Context:
{context}

Question: {question}

Provide a clear answer and mention which source(s) you used."""

    answer = safe_generate(prompt)
    return answer, sources


# ----- MAIN: Test it -----
if __name__ == "__main__":
    question = "What do customers say about delivery delays?"

    print(f"Question: {question}\n")

    answer, sources = answer_from_documents(question)
    print(f"Answer:\n{answer}\n")
    print(f"Sources used: {set(sources)}")