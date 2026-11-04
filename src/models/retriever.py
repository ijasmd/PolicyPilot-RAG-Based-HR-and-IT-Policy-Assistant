"""
Vector Index & Retrieval Engine for PolicyPilot
Owner: Mano (Retrieval Engineer)

Builds vector indices over policy chunks, computes similarity scores,
retrieves top-k evidence, and supports comparing retrieval strategies.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.features.chunking import DocumentChunk


class RetrievalResult:
    def __init__(self, chunk: DocumentChunk, score: float, rank: int):
        self.chunk = chunk
        self.score = float(score)
        self.rank = rank

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "policy_id": self.chunk.policy_id,
            "title": self.chunk.title,
            "chunk_id": self.chunk.chunk_id,
            "score": round(self.score, 4),
            "text": self.chunk.text,
            "category": self.chunk.category,
            "source_file": self.chunk.source_file,
        }


class PolicyVectorRetriever:
    """Vector Retriever supporting TF-IDF semantic matching and cosine similarity."""

    def __init__(self, chunks: List[DocumentChunk], ngram_range: tuple = (1, 2)):
        self.chunks = chunks
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            stop_words="english",
            norm="l2",
            sublinear_tf=True,
        )
        self._fit_index()

    def _fit_index(self):
        """Fit vectorizer on all chunk contents and store embeddings."""
        corpus = [f"{c.title} {c.text}" for c in self.chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3, threshold: float = 0.05) -> List[RetrievalResult]:
        """Retrieve top-k relevant chunks for a user query."""
        if not query.strip() or self.matrix.shape[0] == 0:
            return []

        query_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, self.matrix)[0]

        ranked_indices = np.argsort(sim_scores)[::-1]
        results = []
        rank = 1

        for idx in ranked_indices:
            score = sim_scores[idx]
            if score < threshold and len(results) >= 1:
                # Discard low-confidence matches beyond the first if below threshold
                break
            results.append(RetrievalResult(chunk=self.chunks[idx], score=score, rank=rank))
            rank += 1
            if len(results) >= top_k:
                break

        return results


def compare_retrieval_strategies(
    test_queries: List[Dict[str, str]],
    sentence_chunks: List[DocumentChunk],
    window_chunks: List[DocumentChunk],
    top_k: int = 3,
) -> Dict[str, Any]:
    """Compare retrieval performance between sentence chunking and window chunking."""
    s_retriever = PolicyVectorRetriever(sentence_chunks)
    w_retriever = PolicyVectorRetriever(window_chunks)

    s_hits = 0
    w_hits = 0
    total = len(test_queries)

    for item in test_queries:
        q = item["question"]
        expected_policy = item.get("expected_policy_id", "")
        if not expected_policy:
            continue

        s_res = s_retriever.retrieve(q, top_k=top_k)
        w_res = w_retriever.retrieve(q, top_k=top_k)

        s_policies = [r.chunk.policy_id for r in s_res]
        w_policies = [r.chunk.policy_id for r in w_res]

        if expected_policy in s_policies:
            s_hits += 1
        if expected_policy in w_policies:
            w_hits += 1

    return {
        "num_eval_queries": total,
        "sentence_recall_at_k": round(s_hits / total, 4) if total > 0 else 0.0,
        "window_recall_at_k": round(w_hits / total, 4) if total > 0 else 0.0,
        "sentence_chunk_count": len(sentence_chunks),
        "window_chunk_count": len(window_chunks),
    }


if __name__ == "__main__":
    from src.data.ingestion import load_all_policies
    from src.features.chunking import create_corpus_chunks
    import os

    raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    docs = load_all_policies(os.path.abspath(raw_dir))
    chunks = create_corpus_chunks(docs, strategy="sentence")
    retriever = PolicyVectorRetriever(chunks)

    test_q = "How early should I apply for planned leave?"
    hits = retriever.retrieve(test_q, top_k=2)
    print(f"Query: {test_q}")
    for h in hits:
        print(f"Rank {h.rank} [{h.chunk.policy_id}] Score: {h.score:.3f} -> {h.chunk.text}")
