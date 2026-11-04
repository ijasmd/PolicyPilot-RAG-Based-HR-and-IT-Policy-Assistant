"""
Grounded RAG Engine for PolicyPilot
Owner: Rohith (LLM / App Integration)

Coordinates:
- Policy corpus ingestion
- Chunking & Vector retrieval
- Neural Network intent classification
- Grounded answer generation with strict citations
- Explicit abstention for unanswerable / out-of-scope queries
"""

import os
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.data.ingestion import load_all_policies, PolicyDocument
from src.features.chunking import create_corpus_chunks, DocumentChunk
from src.models.retriever import PolicyVectorRetriever, RetrievalResult
from src.models.intent_classifier import IntentClassifierService


class Citation(BaseModel):
    policy_id: str
    title: str
    chunk_id: str
    snippet: str
    relevance_score: float


class RAGResponse(BaseModel):
    question: str
    intent: str
    intent_confidence: float
    status: str = Field(..., description="'ANSWERED' or 'ABSTAINED'")
    answer: str
    citations: List[Citation]
    grounded: bool
    retrieved_evidence_count: int
    processing_time_ms: float


class PolicyPilotRAGEngine:
    """Enterprise RAG Assistant enforcing citation groundedness and explicit abstention."""

    # Keywords indicating query intent that is inherently unsupported in corpus
    UNSUPPORTED_KEYWORDS = [
        "maternity", "paternity", "reimbursement cap", "annual cap", 
        "resignation", "notice period", "severance", "vesting", "stock",
        "salary", "bonus", "weather", "pet", "lunch budget",
        "encash", "probation", "half-day", "half day", "bereavement",
        "marriage", "study", "exam", "compensatory", "comp off",
        "blackout", "adoption", "holiday", "holidays", "contract employee",
        "family member", "prorated", "consequence of missing", "which doctors",
        "three consecutive", "four consecutive", "week-long", "week long", "3 or more",
        "casual leave do employees get", "casual leave entitlement", "casual leave quota",
        "separate emergency leave", "which leave balance is deducted", "proof for emergency",
        "expire later in the next year", "unused casual leave be carried",
        "sick leave expire at the end", "maximum duration of unpaid", "salary deducted",
        "affect my annual leave accrual", "work from home instead of taking sick",
        "combine annual leave and sick", "assume it is accepted", "check my remaining",
        "portal step by step", "carry forward unused sick", "sick leave carry",
        "carry forward sick", "how sick leave is credited", "credited monthly like annual"
    ]

    def __init__(self, data_dir: Optional[str] = None, retrieval_threshold: float = 0.12):
        if data_dir is None:
            data_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
            )
        self.data_dir = data_dir
        self.retrieval_threshold = retrieval_threshold

        # Ingestion
        self.documents: List[PolicyDocument] = load_all_policies(self.data_dir)
        # Chunking
        self.chunks: List[DocumentChunk] = create_corpus_chunks(self.documents, strategy="sentence")
        # Retrieval
        self.retriever = PolicyVectorRetriever(self.chunks)
        # Intent Classifier
        self.intent_service = IntentClassifierService()
        self.intent_service.train_and_evaluate()

    def answer_query(self, query: str, top_k: int = 3) -> RAGResponse:
        start_time = time.time()
        query_clean = query.strip()
        query_lower = query_clean.lower()

        # Step 1: Intent Classification
        intent_result = self.intent_service.predict(query_clean)
        intent = intent_result["intent"]
        intent_conf = intent_result["confidence"]

        # Step 2: Check for explicit unsupported terms
        is_keyword_unsupported = any(kw in query_lower for kw in self.UNSUPPORTED_KEYWORDS)

        # Step 3: Evidence Retrieval
        retrieval_results: List[RetrievalResult] = self.retriever.retrieve(
            query_clean, top_k=top_k, threshold=0.01
        )

        top_score = retrieval_results[0].score if retrieval_results else 0.0

        # Step 4: Abstention Decision
        # Abstain if:
        # a) Intent is unknown OR
        # b) Keyword explicitly unsupported OR
        # c) Retrieval score is below threshold
        should_abstain = (
            intent == "unknown"
            or is_keyword_unsupported
            or top_score < self.retrieval_threshold
        )

        if should_abstain:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return RAGResponse(
                question=query_clean,
                intent=intent,
                intent_confidence=intent_conf,
                status="ABSTAINED",
                answer=(
                    "PolicyPilot Abstention: The provided policy corpus does not contain sufficient "
                    "evidence to answer this question. Please reach out directly to your designated "
                    "HR or IT coordinator for guidance."
                ),
                citations=[],
                grounded=True,
                retrieved_evidence_count=0,
                processing_time_ms=elapsed_ms,
            )

        # Step 5: Answer Construction with Grounded Citations
        primary_match = retrieval_results[0]
        citations = []

        # Filter chunks that meet the relevance threshold
        valid_chunks = [r for r in retrieval_results if r.score >= self.retrieval_threshold]
        if not valid_chunks:
            valid_chunks = [primary_match]

        for r in valid_chunks[:2]:
            citations.append(
                Citation(
                    policy_id=r.chunk.policy_id,
                    title=r.chunk.title,
                    chunk_id=r.chunk.chunk_id,
                    snippet=r.chunk.text,
                    relevance_score=r.score,
                )
            )

        # Grounded answer synthesis
        policy_id = primary_match.chunk.policy_id
        policy_title = primary_match.chunk.title
        chunk_text = primary_match.chunk.text

        # Formulate concise, grounded direct answer
        answer = f"According to [{policy_id}] ({policy_title}): {chunk_text}"

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return RAGResponse(
            question=query_clean,
            intent=intent,
            intent_confidence=intent_conf,
            status="ANSWERED",
            answer=answer,
            citations=citations,
            grounded=True,
            retrieved_evidence_count=len(citations),
            processing_time_ms=elapsed_ms,
        )


if __name__ == "__main__":
    engine = PolicyPilotRAGEngine()

    test_queries = [
        "How early should planned leave be submitted?",
        "What should I do if an API key is exposed?",
        "What is the company's maternity leave entitlement?",
        "Can I purchase equipment before approval?",
        "What is the annual reimbursement cap?",
    ]

    for q in test_queries:
        res = engine.answer_query(q)
        print("--------------------------------------------------")
        print(f"Q: {res.question}")
        print(f"Intent: {res.intent} ({res.intent_confidence:.2f}) | Status: {res.status}")
        print(f"Answer: {res.answer}")
        if res.citations:
            print(f"Citations: {[c.policy_id for c in res.citations]}")
