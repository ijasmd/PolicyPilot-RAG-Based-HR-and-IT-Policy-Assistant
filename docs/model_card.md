# Model / System Card: PolicyPilot

## Intended Use
PolicyPilot is an enterprise RAG-based decision-support and employee guidance assistant designed to answer questions regarding internal Human Resources and Information Technology policies with exact document citations (`[HR-001]`, `[IT-001]`, etc.). It classifies user intent using an ANN (Multi-Layer Perceptron) and strictly abstains from answering out-of-scope or unsupported queries.

## Out-of-Scope Use
- General chit-chat or external knowledge queries (e.g., weather, public figures, general news).
- Providing legal or binding contractual guarantees.
- Processing confidential employee personal records, PII, or company financial statements without authorization.
- Automatic financial expenditure approvals without designated manager sign-off.

## Dataset and Provenance
- Six synthetic HR and IT policy documents generated for the Capstone Playbook:
  - `HR-001`: Leave and Attendance Policy
  - `HR-002`: Remote Work Policy
  - `HR-003`: Expense and Purchase Requests Policy
  - `IT-001`: Passwords and Multi-Factor Authentication Policy
  - `IT-002`: Device and Data Security Policy
  - `IT-003`: Incident Reporting Policy
- Evaluation Dataset: 20 curated queries consisting of 10 starter benchmark questions plus 10 challenging paraphrased, ambiguous, and unanswerable queries.
- Intent Dataset: 140 balanced, labeled domain examples across 7 classes (`leave`, `remote_work`, `credentials`, `device_security`, `incidents`, `expenses`, and `unknown`).

## Train / Validation / Test Split
- Stratified 75% / 25% train-test split for intent classification with fixed seed (`random_state=42`).
- 20-sample held-out evaluation test set covering both answerable (13 queries) and unanswerable (7 queries) categories.

## Baseline
- Intent Baseline: Multinomial/Logistic Regression Classifier with sublinear TF-IDF.
- Retrieval Baseline: Un-chunked full-text keyword retrieval.

## Metrics
- **Mean Reciprocal Rank (MRR):** 92.3%
- **Recall@1:** 92.3%
- **Recall@3:** 100.0%
- **Abstention F1 Score:** 100.0% (Precision: 100%, Recall: 100%)
- **Citation Accuracy:** 100.0% on answerable queries
- **Overall System Accuracy:** 95.0%
- **Intent Classifier Weighted F1 (MLP ANN):** 76.7% vs Baseline 74.4%

## Error Analysis and Limitations
- The current corpus contains 6 policies. Very complex multi-hop queries that span multiple disjoint policies require cross-document re-ranking.
- Synthetic dataset: does not reflect real enterprise legal contracts. Real production rollout requires connecting to enterprise vector databases (e.g., Pinecone/Chroma/Qdrant) and company SSO authentication.

## Privacy & Security
- No real credentials, API keys, or personal identifying information are stored or logged.
- Query inputs are scrubbed of credentials before vector indexing.
- Prompt injection protection: queries cannot override the abstention instruction.

## Monitoring and Rollback
- REST endpoint `/health` tracks live policy ingestion and chunk counts.
- Automated evaluation runner `/metrics` enables regression detection before deployment.
- Rollback plan: Fallback to exact keyword lookup if vector ranking confidence falls below 0.10.

## Human Review
- All unsupported or low-confidence queries are routed directly to human HR/IT coordinators via the abstention mechanism.
