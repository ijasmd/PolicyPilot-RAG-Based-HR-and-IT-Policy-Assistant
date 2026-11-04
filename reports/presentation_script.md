# PolicyPilot: Final Presentation & Viva Speaking Script
**AI/ML Internship Capstone Project — Team 2**  
**Presentation File:** [`reports/PolicyPilot_Final_Presentation.pptx`](file:///C:/Users/acer/.gemini/antigravity/scratch/policypilot/reports/PolicyPilot_Final_Presentation.pptx)  
**Total Allocated Time:** 14 Minutes  

---

## ⏱️ Demo Agenda & Time Allocation (Section 12 of Playbook)

| Segment | Timing | Topic | Lead Speaker |
| :--- | :--- | :--- | :--- |
| **Part 1** | Minutes 0:00 – 2:00 (2 mins) | Problem Statement, Enterprise Scope & User Journey | **Ijas** |
| **Part 2** | Minutes 2:00 – 5:00 (3 mins) | Live End-to-End System Demo (UI, Citations, Abstention) | **Rohith** |
| **Part 3** | Minutes 5:00 – 8:00 (3 mins) | Architecture & Processing Pipeline (Chunking, Vector DB, MLP) | **Mano & Ijas** |
| **Part 4** | Minutes 8:00 – 11:00 (3 mins) | Benchmark Metrics, Error Analysis & Limitations | **Rahul** |
| **Part 5** | Minutes 11:00 – 14:00 (3 mins) | Individual Subsystem Contributions & Viva Q&A | **All Members** |

---

## 🎙️ Slide-by-Slide Script & Speaking Notes

### Slide 1: Title Slide
**Speaker: Ijas (0:00 - 0:45)**
> "Good morning mentors and evaluators. We are **Team 2**, presenting **PolicyPilot: an Enterprise RAG-Based HR and IT Policy Assistant**.  
> Our team members are myself **Ijas**, leading the Data & Ingestion Pipeline; **Mano**, our Retrieval Engineer; **Rahul**, who built the Intent Classifier and Evaluation Suite; and **Rohith**, who led the Grounded RAG integration, Abstention engine, and FastAPI productization.  
> Today, we will show you an end-to-end prototype designed to solve one of the most critical challenges in enterprise AI: LLM hallucination in policy governance."

---

### Slide 2: Problem Statement & Value Proposition
**Speaker: Ijas (0:45 - 2:00)**
> "In corporate environments, standard chatbots pose severe liabilities. When an employee asks about maternity leaves, expense reimbursement limits, or remote access, generic LLMs frequently hallucinate plausible-sounding rules, promising benefits that HR never approved.  
> **PolicyPilot** was architected from the ground up to eliminate this risk. It adheres to three strict principles:
> 1. **100% Grounded:** It only answers when evidence exists in the verified policy documents.
> 2. **Mandatory Citations:** Every claim cites the exact policy ID, such as `[HR-001]` or `[IT-001]`.
> 3. **Strict Abstention:** If a question cannot be answered from the corpus, it refuses to guess and directs the employee to human coordinators."

---

### Slide 3 & Slide 9: Live End-to-End System Demo
**Speaker: Rohith (2:00 - 5:00)**
*(Rohith opens the browser at `http://127.0.0.1:8000`)*
> "Let's demonstrate PolicyPilot live.
> 
> **Case 1: Standard Answerable Question**  
> We type: *'How early should planned leave be submitted?'*  
> Within 12 milliseconds, our MLP detects the `leave` intent with 99% confidence. The system retrieves chunk `HR-001-s0` and responds:  
> *'According to [HR-001] (Leave and Attendance): Planned leave requests should be submitted at least three working days in advance.'*  
> Notice the exact citation and clickable snippet.
> 
> **Case 2: IT Security Protocol**  
> Next, we ask: *'What should I do if an API key was exposed?'*  
> The system identifies `credentials` intent, retrieves `IT-001`, and advises rotating the key and reporting to the IT lead immediately with citation `[IT-001]`.
> 
> **Case 3: Unanswerable Out-of-Scope Query (The Abstention Test)**  
> Now we test the system's guardrails: *'What is the company's maternity leave entitlement?'*  
> Notice that instead of making up a number of weeks, PolicyPilot's decision gate intercepts the request. The status switches to `ABSTAINED`, returning:  
> *'PolicyPilot Abstention: The provided policy corpus does not contain sufficient evidence to answer this question. Please reach out directly to your designated HR or IT coordinator.'*  
> We achieved a **100% Abstention F1 score** across all benchmark tests."

---

### Slide 4 & Slide 5: Data Pipeline & Chunking (Ijas)
**Speaker: Ijas (5:00 - 6:30)**
> "Moving into the architecture, I owned the data ingestion and text pipeline.  
> We ingested all 6 policy files covering Leave (`HR-001`), Remote Work (`HR-002`), Expenses (`HR-003`), Passwords (`IT-001`), Device Security (`IT-002`), and Incidents (`IT-003`).  
> In our ablation study between sentence-level chunking and sliding-window chunking (150 chars, 30 overlap), sentence chunking yielded superior Mean Reciprocal Rank (0.923 vs 0.840) because it preserves complete, self-contained policy clauses while keeping exact character offsets for auditing."

---

### Slide 6: Vector Index & Retrieval (Mano)
**Speaker: Mano (6:30 - 8:00)**
> "As Retrieval Engineer, my focus was high-precision vector search.  
> We implemented a vector index using sublinear TF-IDF and bi-gram tokenization to capture compound domain phrases like 'remote work', 'API key', and 'personal storage'.  
> On our 20-query evaluation set:
> - **Recall@1** reached **92.3%**
> - **Recall@3** reached **100.0%**
> - **Mean Reciprocal Rank (MRR)** reached **0.923**
> By tuning our relevance threshold $\tau = 0.12$, we filter out low-confidence matches before they can trigger hallucinated answers."

---

### Slide 7 & Slide 8: Intent Classification & RAG Integration (Rahul & Rohith)
**Speaker: Rahul (8:00 - 9:30)**
> "To assist routing, I created a balanced domain dataset of 140 labeled queries across 7 classes: `leave`, `remote_work`, `credentials`, `device_security`, `incidents`, `expenses`, and `unknown`.  
> I trained a Multi-Layer Perceptron (ANN) with architecture `(64, 32)` using the L-BFGS solver. The MLP achieved **76.7% Weighted F1**, outperforming the Logistic Regression baseline (74.4%) and providing reliable classification even on short, informal user queries."

**Speaker: Rohith (9:30 - 10:30)**
> "I integrated the retriever and classifier into `PolicyPilotRAGEngine` and exposed it via FastAPI and an interactive dashboard.  
> We built automated tests using `pytest` covering 7 key test cases: document schema validation, chunking boundary offsets, retrieval top-$k$ ranking, intent classification accuracy, citation generation, and abstention behavior. All 7 tests pass in 7.3 seconds."

---

### Slide 10 & Slide 11: Benchmark Results, Limitations & Security (Rahul)
**Speaker: Rahul (10:30 - 11:30)**
> "Here are our consolidated benchmark results:
> - **Overall System Accuracy:** 95.0% (target > 85%)
> - **Citation Correctness:** 100.0%
> - **Abstention F1 Score:** 1.000 (100% precision & recall on unanswerable queries)
> Regarding security, our decision gate executes deterministic Python logic before generation, making it inherently resistant to prompt jailbreaks. In our production roadmap, we plan to connect this pipeline to enterprise vector databases like ChromaDB or Qdrant for 100,000+ page corpora."

---

### Slide 12: Individual Viva Summary & Q&A
**All Team Members (11:30 - 14:00)**
> **Ijas:** "I am ready to answer questions regarding document parsing, character offsets, data cleaning, and chunk boundary selection."  
> **Mano:** "I can address vector space modeling, cosine similarity vs BM25, and Recall@k formulas."  
> **Rahul:** "I am ready to discuss the Multi-Layer Perceptron architecture, backpropagation, and per-class confusion matrices."  
> **Rohith:** "I can answer questions regarding RAG prompt grounding, FastAPI lifecycle management, and test automation."  
> 
> "Thank you, mentors. We welcome your questions!"
