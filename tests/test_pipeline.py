"""
End-to-End Test Suite for PolicyPilot
Verifies Ingestion, Chunking, Retrieval, Intent Classification, RAG Citations, and Abstention.
"""

import os
import pytest
from fastapi.testclient import TestClient

from src.data.ingestion import load_all_policies, parse_policy_file
from src.features.chunking import create_corpus_chunks, chunk_by_sentence, chunk_by_window
from src.models.retriever import PolicyVectorRetriever
from src.models.intent_classifier import IntentClassifierService
from src.models.rag_engine import PolicyPilotRAGEngine
from src.models.evaluation import PolicyPilotEvaluator
from src.api.main import app

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw"))


def test_ingestion():
    policies = load_all_policies(DATA_DIR)
    assert len(policies) >= 6, f"Expected at least 6 policies, found {len(policies)}"
    
    ids = {p.policy_id for p in policies}
    expected_ids = {"HR-001", "HR-002", "HR-003", "IT-001", "IT-002", "IT-003"}
    assert expected_ids.issubset(ids), f"Mismatch in core policy IDs: {ids}"

    for p in policies:
        assert p.title, f"Missing title in {p.policy_id}"
        assert len(p.normalized_content) > 50, f"Policy {p.policy_id} content too short"
        assert p.category in {"HR", "IT"}


def test_chunking_strategies():
    policies = load_all_policies(DATA_DIR)
    s_chunks = create_corpus_chunks(policies, strategy="sentence")
    w_chunks = create_corpus_chunks(policies, strategy="window", window_size=150, overlap=30)

    assert len(s_chunks) >= len(policies), "Sentence chunks should be at least equal to document count"
    assert len(w_chunks) >= len(policies), "Window chunks should be non-empty"

    # Check offset validity
    for c in s_chunks:
        assert c.end_char > c.start_char
        assert c.policy_id
        assert c.chunk_id


def test_retriever():
    policies = load_all_policies(DATA_DIR)
    chunks = create_corpus_chunks(policies, strategy="sentence")
    retriever = PolicyVectorRetriever(chunks)

    # Test top-1 retrieval
    results = retriever.retrieve("How early should planned leave be submitted?", top_k=2)
    assert len(results) > 0
    assert results[0].chunk.policy_id == "HR-001"
    assert results[0].score > 0.1


def test_intent_classifier():
    service = IntentClassifierService()
    results = service.train_and_evaluate(test_size=0.25)
    
    assert "baseline" in results
    assert "mlp_neural_network" in results
    assert results["mlp_neural_network"]["weighted_f1"] >= 0.70

    # Test prediction
    pred = service.predict("Can I purchase equipment before approval?")
    assert pred["intent"] == "expenses"
    assert pred["mapped_policy_id"] == "HR-003"


def test_rag_answering_and_abstention():
    engine = PolicyPilotRAGEngine(data_dir=DATA_DIR)

    # 1. Answerable query
    res_ans = engine.answer_query("How early should planned leave be submitted?")
    assert res_ans.status == "ANSWERED"
    assert len(res_ans.citations) > 0
    assert res_ans.citations[0].policy_id == "HR-001"
    assert "HR-001" in res_ans.answer

    # 2. Unanswerable query -> must abstain
    res_abs = engine.answer_query("What is the company's maternity leave entitlement?")
    assert res_abs.status == "ABSTAINED"
    assert len(res_abs.citations) == 0
    assert "Abstention" in res_abs.answer


def test_evaluation_runner():
    engine = PolicyPilotRAGEngine(data_dir=DATA_DIR)
    evaluator = PolicyPilotEvaluator(engine)
    metrics = evaluator.run_evaluation()

    assert metrics["retrieval_metrics"]["mrr"] >= 0.75
    assert metrics["abstention_metrics"]["f1_score"] >= 0.80
    assert metrics["overall_system_accuracy"] >= 0.80


def test_fastapi_endpoints():
    client = TestClient(app)

    # Health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"

    # Policies
    r_pols = client.get("/policies")
    assert r_pols.status_code == 200
    assert len(r_pols.json()) >= 6

    # Ask
    r_ask = client.post("/ask", json={"query": "What should I do if an API key is exposed?"})
    assert r_ask.status_code == 200
    data = r_ask.json()
    assert data["status"] == "ANSWERED"
    assert data["citations"][0]["policy_id"] == "IT-001"

    # Metrics
    r_met = client.get("/metrics")
    assert r_met.status_code == 200
    assert "overall_system_accuracy" in r_met.json()
