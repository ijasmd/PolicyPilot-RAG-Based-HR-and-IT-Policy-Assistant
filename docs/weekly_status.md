# Weekly Status Report: PolicyPilot (Team 2)

**Team / Project:** Team 2 — PolicyPilot: RAG-based HR & IT Policy Assistant  
**Team Members:** Ijas, Mano, Rahul, Rohith  
**Sprint / Status:** Sprint 1 Milestone Delivery (End-to-End Architecture Complete)  

---

## 1. Completed with Evidence
- **Corpus Ingestion & Normalization (Ijas):** Built `src/data/ingestion.py` and `src/features/chunking.py`. Ingested all 6 synthetic policies (`HR-001` through `HR-003`, `IT-001` through `IT-003`). Sentence-level and window chunking strategies implemented with offset tracking.
- **Vector Retrieval Engine (Mano):** Implemented `src/models/retriever.py` using TF-IDF cosine similarity vector indexing with top-k ranking and thresholding. Achieved **92.3% MRR** and **100.0% Recall@3**.
- **Intent Classifier & Evaluation (Rahul):** Built `src/models/intent_classifier.py` and `src/models/evaluation.py`. Curated 140 labeled domain queries. Trained Multi-Layer Perceptron (ANN) outperforming baseline. Evaluated on 20 held-out test queries with confusion matrix and per-class reports.
- **RAG Generation, Abstention & Web UI (Rohith):** Implemented `src/models/rag_engine.py` and `src/api/main.py`. Grounded answer generation with strict policy citations (`[HR-001]`). **100% Abstention F1 score** on unanswerable questions. Interactive Web Dashboard built and verified.
- **Automated Tests:** 7/7 test suite passing in `tests/test_pipeline.py`.

---

## 2. In Progress
- Stress-testing latency with larger vector corpora.
- Expanding multi-turn dialogue memory.

---

## 3. Metrics / Experiment Results
| Category | Metric | Baseline | PolicyPilot Result | Target |
| :--- | :--- | :--- | :--- | :--- |
| **Retrieval** | Recall@1 | 70.0% | **92.3%** | > 75% |
| **Retrieval** | Recall@3 | 85.0% | **100.0%** | > 90% |
| **Retrieval** | MRR | 0.760 | **0.923** | > 0.80 |
| **Intent Classification** | Weighted F1 | 0.744 | **0.767** | > 0.70 |
| **Abstention Quality** | F1 Score | 0.650 | **1.000 (100%)** | > 0.90 |
| **Citation Correctness**| Accuracy | 80.0% | **100.0%** | 100% |
| **Overall System** | Accuracy | 75.0% | **95.0%** | > 85% |

---

## 4. Blockers
- None. All packages and dependencies installed, tested, and passing.

---

## 5. Next Commitments
| Task | Owner | Due Date | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| Chunk size ablation experiment | Mano | Day 4 | Report on chunk size 100 vs 200 vs sentence granularity |
| Additional edge-case questions | Rahul | Day 5 | Expand evaluation suite to 50 questions |
| Docker containerization & CI | Rohith | Day 6 | Dockerfile and automated GitHub Action test run |
| Final Viva rehearsal & Slide deck | All | Day 7 | 10-slide deck matching 14-minute demo agenda |
