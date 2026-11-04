"""
Document Chunking and Preprocessing Module
Owner: Ijas (Data & Text Pipeline)

Implements chunking strategies (sentence-based and window-based)
while strictly preserving policy metadata, IDs, and source character offsets.
"""

import re
from typing import List, Literal
from pydantic import BaseModel, Field
from src.data.ingestion import PolicyDocument


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk ID e.g., HR-001-c0")
    policy_id: str = Field(..., description="Parent policy ID")
    title: str = Field(..., description="Parent policy title")
    text: str = Field(..., description="Chunk text content")
    start_char: int = Field(..., description="Starting character index in parent document")
    end_char: int = Field(..., description="Ending character index in parent document")
    source_file: str = Field(..., description="Source filename")
    category: str = Field(..., description="HR or IT")


def split_into_sentences(text: str) -> List[str]:
    """Split text cleanly into sentences using punctuation boundaries."""
    # Split on periods, exclamation marks, question marks followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_by_sentence(doc: PolicyDocument) -> List[DocumentChunk]:
    """Chunk a policy document at sentence granularity.
    Best for precise citation and concise RAG retrieval.
    """
    sentences = split_into_sentences(doc.normalized_content)
    chunks = []
    current_offset = 0

    for idx, sentence in enumerate(sentences):
        start_char = doc.normalized_content.find(sentence, current_offset)
        if start_char == -1:
            start_char = current_offset
        end_char = start_char + len(sentence)
        current_offset = end_char

        chunks.append(
            DocumentChunk(
                chunk_id=f"{doc.policy_id}-s{idx}",
                policy_id=doc.policy_id,
                title=doc.title,
                text=sentence,
                start_char=start_char,
                end_char=end_char,
                source_file=doc.source_file,
                category=doc.category,
            )
        )
    return chunks


def chunk_by_window(doc: PolicyDocument, window_size: int = 200, overlap: int = 50) -> List[DocumentChunk]:
    """Sliding window chunking with configurable overlap.
    Allows testing chunk size sensitivity as required by the Playbook.
    """
    text = doc.normalized_content
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + window_size, len(text))
        # Snap to end of word if possible
        if end < len(text):
            next_space = text.rfind(" ", start, end)
            if next_space > start:
                end = next_space

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc.policy_id}-w{idx}",
                    policy_id=doc.policy_id,
                    title=doc.title,
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                    source_file=doc.source_file,
                    category=doc.category,
                )
            )
            idx += 1

        if end >= len(text):
            break
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def create_corpus_chunks(
    documents: List[PolicyDocument],
    strategy: Literal["sentence", "window"] = "sentence",
    window_size: int = 200,
    overlap: int = 50,
) -> List[DocumentChunk]:
    """Generate chunks for an entire corpus using the selected strategy."""
    all_chunks = []
    for doc in documents:
        if strategy == "sentence":
            all_chunks.extend(chunk_by_sentence(doc))
        else:
            all_chunks.extend(chunk_by_window(doc, window_size=window_size, overlap=overlap))
    return all_chunks


if __name__ == "__main__":
    from src.data.ingestion import load_all_policies
    import os

    raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    docs = load_all_policies(os.path.abspath(raw_dir))
    s_chunks = create_corpus_chunks(docs, strategy="sentence")
    w_chunks = create_corpus_chunks(docs, strategy="window", window_size=150, overlap=30)
    print(f"Sentence chunking created {len(s_chunks)} chunks.")
    print(f"Window chunking created {len(w_chunks)} chunks.")
    print(f"Sample sentence chunk: {s_chunks[0]}")
