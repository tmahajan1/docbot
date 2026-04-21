import os
import glob
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
from pathlib import Path
from google import genai


load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3-flash-preview"  # you can upgrade to gpt-4.1 later

DOCS_DIR = Path("docs")  # folder with your .md files

# This will hold all our chunks with embeddings
CHUNKS: list[dict] = []

def embed_text(text: str) -> np.ndarray:
    """Call OpenAI embeddings API and return a numpy vector."""
    resp = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    emb = resp.embeddings[0].values
    return np.array(emb, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1D vectors."""
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def load_docs_from_folder(folder: Path) -> list[dict]:
    docs: list[dict] = []

    for path in folder.glob("*.md"):
        text = path.read_text(encoding="utf-8")

        docs.append(
            {
                "id": path.stem,
                "title": path.stem.replace("_", " ").title(),
                "content": text,
                "path": str(path),
            }
        )

    return docs


def chunk_doc(doc: dict, max_chars: int = 800) -> list[dict]:
    """
    Take one doc dict and break its content into smaller chunks.
    Returns a list of chunk dicts with text + metadata (no embeddings yet).
    """
    text = doc["content"].strip()
    paragraphs = text.split("\n\n")  # split on blank lines

    chunks = []
    current = ""

    for p in paragraphs:
        # if adding this paragraph keeps us under limit, append to current chunk
        if len(current) + len(p) <= max_chars:
            if current:
                current += "\n\n" + p
            else:
                current = p
        else:
            # current chunk is full -> save it
            if current:
                chunks.append(current)
            # start a new chunk with this paragraph
            current = p

    # don't forget the last chunk
    if current:
        chunks.append(current)

    # now wrap these raw text chunks with metadata
    result = []
    for i, chunk_text in enumerate(chunks):
        result.append(
            {
                "id": f"{doc['id']}_chunk_{i}",
                "title": doc["title"],
                "path": doc["path"],
                "text": chunk_text,
                # embedding will be added later
            }
        )
    return result


def build_index(docs: list[dict]) -> list[dict]:
    """
    Take all docs, chunk them, embed each chunk, and return a list of
    chunk dicts with embeddings. This acts like our 'vector DB'.
    """
    index = []

    for doc in docs:
        chunk_dicts = chunk_doc(doc)  # get chunks for this doc
        for chunk in chunk_dicts:
            emb = embed_text(chunk["text"])  # np.array
            chunk["embedding"] = emb         # attach embedding to this chunk
            index.append(chunk)

    return index


def retrieve_relevant_chunks(question: str, index: list[dict], top_k: int = 3) -> list[dict]:
    """
    Given a question string and our index (list of chunks),
    return the top_k most similar chunks.
    """
    q_emb = embed_text(question)  # embedding for the question

    scored = []
    for chunk in index:
        score = cosine_similarity(q_emb, chunk["embedding"])
        scored.append((score, chunk))

    # sort by score descending (higher cosine = more similar)
    scored.sort(key=lambda x: x[0], reverse=True)

    # keep only top_k chunks
    top_chunks = [chunk for score, chunk in scored[:top_k]]
    return top_chunks


def build_messages(question: str, chunks: list[dict]) -> str:
    """
    Build a single prompt string for the chat completion, including system prompt, retrieved docs, and user question.
    """
    system_prompt = """
You are DocBot, an internal documentation assistant.
You answer questions ONLY using the documentation snippets provided to you.
If the answer is not clearly in the docs, say you don't know.
Be concise and, when possible, mention which doc (title) you used.
""".strip()

    # Build a single big context string from the top chunks
    context_parts = []
    for i, chunk in enumerate(chunks, start=1):
        part = f"[{i}] Title: {chunk['title']}\nPath: {chunk['path']}\n\n{chunk['text']}"
        context_parts.append(part)

    context_text = "\n\n---\n\n".join(context_parts)

    user_prompt = f"""
Here are some relevant documentation snippets:

{context_text}

---

User question:
{question}

Using ONLY the information in the snippets above, answer the question.
If the docs don't contain the answer, say you don't know.
""".strip()

    # Concatenate system and user prompts into a single string
    full_prompt = system_prompt + "\n\n" + user_prompt
    return full_prompt


def answer_question(question: str, index: list[dict], top_k: int = 3) -> str:
    """
    Full RAG pipeline for a single question:
    1. Retrieve top_k relevant chunks from the index
    2. Build messages with those chunks + question
    3. Call the chat model and return its answer text
    """
    # 1. Retrieve
    top_chunks = retrieve_relevant_chunks(question, index, top_k=top_k)
    if not top_chunks:
        return "I couldn't find any relevant documentation for this question."

    # 2. Build messages
    messages = build_messages(question, top_chunks)

    # 3. Call the LLM
    resp = client.models.generate_content(
        model=CHAT_MODEL,
        contents=messages,  # now a string
    )

    return resp.text


if __name__ == "__main__":
    # 1. Load docs from the docs/ folder
    docs = load_docs_from_folder(DOCS_DIR)
    if not docs:
        print(f"No .md files found in {DOCS_DIR}.")
        raise SystemExit(1)

    print(f"Loaded {len(docs)} docs:")
    for d in docs:
        print(" -", d["title"])

    # 2. Build the index (chunk + embed)
    print("\nBuilding index (chunking + embeddings)...")
    index = build_index(docs)
    print(f"Index built with {len(index)} chunks.\n")

    # 3. Simple chat loop
    print("DocBot is ready! Ask your questions (or type 'exit' to quit).")
    while True:
        q = input("\nYou: ").strip()
        if not q or q.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        answer = answer_question(q, index)
        print("\nDocBot:", answer)




