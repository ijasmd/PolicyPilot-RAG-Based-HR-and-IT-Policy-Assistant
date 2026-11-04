# PolicyPilot: Complete Day-to-Day Execution Plan
**AI/ML Internship Capstone Project — Team 2**  
**Members:** Ijas, Mano, Rahul, Rohith  
**Project:** PolicyPilot: RAG-based HR and IT Policy Assistant  

---

## Overview
This day-to-day plan maps the **8 Milestone Phases** defined in Section 6 of the Capstone Playbook into granular daily action items, assigned owners, deliverables, and acceptance criteria.

---

### Day 1: Kickoff, Problem Statement, Scope & Data Audit
**Focus:** Alignment, charter creation, git repository setup, and dataset audit.

- **Team Action Items:**
  - Kickoff meeting: review problem statement and acceptance criteria (grounded enterprise assistant vs general chatbot).
  - Setup GitHub / local repository matching the recommended structure.
  - Clone or link starter data from `AI_ML_Internship_Updated_Bundle/datasets/team2_policypilot`.
- **Individual Assignments:**
  - **Ijas:** Inspect all 6 policy text files (`HR-001` to `HR-003`, `IT-001` to `IT-003`). Verify schema, encoding, and metadata consistency.
  - **Mano:** Set up local vector environment and define retrieval baseline requirements.
  - **Rahul:** Audit `evaluation_questions.csv` (10 starter questions). Categorize answerable vs unanswerable types.
  - **Rohith:** Draft Project Charter and definition of done in `docs/` and establish task board (Backlog → Ready → In Progress → Review → Done).
- **Deliverables:**
  - `README.md` initial draft
  - Data audit log
  - Verified repository structure

---

### Day 2: EDA, Corpus Ingestion & Baseline Retrieval
**Focus:** Ingestion engine, text normalization, and initial retrieval baseline.

- **Team Action Items:**
  - Complete corpus parser and document data model.
  - Execute first baseline retrieval experiment and record metrics.
- **Individual Assignments:**
  - **Ijas:** Implement `src/data/ingestion.py` using Pydantic. Ensure policy IDs, titles, and text bodies are parsed cleanly.
  - **Mano:** Implement first TF-IDF baseline retriever in `src/models/retriever.py`. Test query matching.
  - **Rahul:** Label initial 35 query samples for intent classification categories (`leave`, `remote_work`, `credentials`, etc.).
  - **Rohith:** Draft grounded prompt template and define abstention refusal message format.
- **Deliverables:**
  - Working `ingestion.py` loading all 6 policies.
  - Baseline retrieval script with execution log.
  - Initial `weekly_status.md` update.

---

### Day 3: End-to-End Minimum Viable Workflow (MVW)
**Focus:** Connecting Ingestion → Retrieval → Intent → RAG Generation.

- **Team Action Items:**
  - Connect all components into an end-to-end working script.
  - Conduct mentor architecture review.
- **Individual Assignments:**
  - **Ijas:** Implement sentence-based and sliding-window chunking in `src/features/chunking.py`.
  - **Mano:** Integrate chunked corpus into vector index and compute cosine similarity scores.
  - **Rahul:** Build baseline classifier (Logistic Regression) in `src/models/intent_classifier.py`.
  - **Rohith:** Implement `src/models/rag_engine.py` unifying retrieval and intent prediction into unified RAG response.
- **Deliverables:**
  - End-to-end command `python -m src.models.rag_engine` running successfully.
  - Architecture diagram committed.

---

### Day 4: Model, Retrieval & Extraction Improvements
**Focus:** Neural network intent classifier and retrieval sensitivity experiments.

- **Team Action Items:**
  - Train Multi-Layer Perceptron (ANN) classifier.
  - Compare sentence-level vs window-based chunking.
- **Individual Assignments:**
  - **Ijas:** Measure document chunk statistics (token counts, boundary fidelity, metadata linkage).
  - **Mano:** Run chunk-size ablation study (Sentence chunks vs Window size 150/30 overlap). Calculate Recall@k.
  - **Rahul:** Expand intent dataset to 140 balanced samples. Train MLP Classifier (`hidden_layer_sizes=(64, 32)`).
  - **Rohith:** Implement strict citation formatting (e.g. `[HR-001]`) and threshold-based decision gating.
- **Deliverables:**
  - Neural network MLP model exceeding baseline F1.
  - Retrieval comparison report in `reports/`.

---

### Day 5: Evaluation Set, Metrics, Error Analysis & Security Review
**Focus:** Rigorous benchmark evaluation across answerable and unanswerable queries.

- **Team Action Items:**
  - Run full benchmark evaluation and analyze failure modes.
  - Security audit: ensure no confidential credentials or prompts are leaked.
- **Individual Assignments:**
  - **Ijas:** Audit data provenance and ensure clean separation of training vs test queries.
  - **Mano:** Calculate Mean Reciprocal Rank (MRR), Recall@1, and Recall@3.
  - **Rahul:** Build automated evaluation framework `src/models/evaluation.py`. Compute per-class F1, confusion matrix, and Abstention F1 score.
  - **Rohith:** Conduct security review: test prompt injection resistance and guarantee abstention on missing policies.
- **Deliverables:**
  - `reports/evaluation_report.md` and `evaluation_report.json`.
  - Error analysis report documenting edge-case behavior.

---

### Day 6: API, Web UI, Automated Tests & Packaging
**Focus:** Productization, REST API, web dashboard, and test coverage.

- **Team Action Items:**
  - Deploy REST API and interactive web interface.
  - Implement comprehensive unit and integration test suite.
- **Individual Assignments:**
  - **Ijas:** Write unit tests for ingestion, metadata parsing, and chunking integrity.
  - **Mano:** Write unit tests for vector indexing and top-$k$ retrieval accuracy.
  - **Rahul:** Write unit tests for intent classification and evaluation metric calculations.
  - **Rohith:** Implement FastAPI server (`src/api/main.py`) with `/ask`, `/classify-intent`, `/metrics`, and interactive HTML UI. Write API endpoint tests.
- **Deliverables:**
  - 7/7 automated tests passing via `pytest`.
  - Live interactive web dashboard accessible via browser (`http://127.0.0.1:8000`).

---

### Day 7: Feature Freeze, Bug Bash, Reproducibility Check & Demo Rehearsal
**Focus:** Code freeze, documentation completion, model card, and presentation rehearsal.

- **Team Action Items:**
  - Feature freeze: zero new code; focus on bug fixes, polish, and execution speed.
  - Rehearse live demonstration strictly timing each section to match the 14-minute agenda.
- **Individual Assignments:**
  - **Ijas:** Run reproducibility check from a clean environment; verify `requirements.txt`.
  - **Mano:** Re-verify retrieval metrics and prepare retrieval failure examples for viva.
  - **Rahul:** Finalize `docs/model_card.md` and confusion matrix visualizations.
  - **Rohith:** Build presentation deck (`reports/PolicyPilot_Final_Presentation.pptx`) and prepare live UI demo script.
- **Deliverables:**
  - Completed `docs/model_card.md` and `docs/weekly_status.md`.
  - Finalized slide deck (`.pptx` and `.md`).
  - Recorded dry-run demo timing.

---

### Day 8: Final Presentation, Live Demo, Individual Viva & Scoring
**Focus:** Final presentation to mentors and evaluators (100-Point Rubric).

- **14-Minute Demo Agenda Breakdown:**
  1. **Minutes 0–2 (Problem, User & Scope):** Led by Ijas & Rohith.
     - Enterprise hallucination risk, need for decision support with grounded citations.
     - Scope: 6 HR/IT policies, decision to abstain when out of scope.
  2. **Minutes 2–5 (Live End-to-End Demo):** Led by Rohith.
     - Demonstrate query 1: Answerable with citation (`[HR-001]`).
     - Demonstrate query 2: IT security query (`[IT-001]`).
     - Demonstrate query 3: Unanswerable query (Maternity leave / Cap) showing crisp abstention.
  3. **Minutes 5–8 (Architecture & Workflow):** Led by Ijas & Mano.
     - Ingestion & sentence chunking pipeline.
     - Vector similarity index & cosine similarity ranking.
     - Neural network intent classifier (MLP).
  4. **Minutes 8–11 (Metrics, Error Analysis & Limitations):** Led by Rahul.
     - 95.0% Overall Accuracy, 92.3% MRR, 100% Abstention F1.
     - Comparison between Baseline vs Neural Network.
     - Failure cases and production roadmap.
  5. **Minutes 11–14 (Individual Contributions, Viva Q&A):** All Team Members.
     - Each member speaks to their owned subsystem:
       - **Ijas:** Ingestion, data dictionary, chunk boundary offsets.
       - **Mano:** Retrieval formulas, cosine vs BM25, Recall@k tradeoffs.
       - **Rahul:** Multi-Layer Perceptron architecture, backprop, per-class F1, confusion matrix.
       - **Rohith:** Prompt grounding, abstention gating, FastAPI, testing, deployment.
