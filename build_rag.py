import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
import chromadb
import time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ----- Set up ChromaDB (local, on your laptop) -----
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Delete old collection if it exists (so we can rebuild cleanly)
try:
    chroma_client.delete_collection(name="pulseiq_documents")
except:
    pass

collection = chroma_client.create_collection(name="pulseiq_documents")


def get_embedding(text):
    """Convert text into a vector (list of numbers) using Gemini's embedding model."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def load_policy_documents():
    """Load and chunk the 3 policy text files."""
    chunks = []
    metadata = []

    policy_files = {
        'return_policy.txt': 'Return Policy',
        'delivery_sla.txt': 'Delivery SLA',
        'seller_agreement.txt': 'Seller Agreement'
    }

    for filename, doc_type in policy_files.items():
        filepath = os.path.join('policy_docs', filename)
        with open(filepath, 'r') as f:
            text = f.read()

        # Simple chunking: split by double newline (paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        for para in paragraphs:
            chunks.append(para)
            metadata.append({'source': doc_type, 'type': 'policy'})

    return chunks, metadata


def load_review_samples(n=100):
    """Load a sample of real customer reviews with comments."""
    silver = pd.read_csv('data/silver_master.csv')

    # Only keep reviews that actually have written comments
    reviews_with_text = silver[silver['review_comment_message'].notna()]
    reviews_with_text = reviews_with_text[['review_comment_message', 'review_score', 'product_category_name']]

    # Take a sample (don't need all 40K+ reviews for a portfolio project)
    sample = reviews_with_text.sample(n=min(n, len(reviews_with_text)), random_state=42)

    chunks = []
    metadata = []

    for _, row in sample.iterrows():
        text = f"Review (score {row['review_score']}/5, category: {row['product_category_name']}): {row['review_comment_message']}"
        chunks.append(text)
        metadata.append({
            'source': 'Customer Review',
            'type': 'review',
            'category': row['product_category_name'],
            'score': str(row['review_score'])
        })

    return chunks, metadata


# ----- Build the full RAG database -----
print("Loading policy documents...")
policy_chunks, policy_metadata = load_policy_documents()
print(f"  {len(policy_chunks)} policy chunks loaded")

print("Loading review samples...")
review_chunks, review_metadata = load_review_samples(n=100)
print(f"  {len(review_chunks)} review chunks loaded")

all_chunks = policy_chunks + review_chunks
all_metadata = policy_metadata + review_metadata

print(f"\nGenerating embeddings for {len(all_chunks)} chunks (this takes a few minutes)...")

ids = []
embeddings = []

for i, chunk in enumerate(all_chunks):
    embedding = get_embedding(chunk)
    time.sleep(2)
    embeddings.append(embedding)
    ids.append(f"chunk_{i}")

    if (i + 1) % 10 == 0:
        print(f"  Processed {i + 1}/{len(all_chunks)}...")

# Store everything in ChromaDB
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=all_chunks,
    metadatas=all_metadata
)

print(f"\nRAG database built successfully! {len(all_chunks)} chunks stored in ChromaDB.")