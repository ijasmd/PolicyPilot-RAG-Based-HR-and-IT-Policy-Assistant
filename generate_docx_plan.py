"""
Generates a comprehensive Day-by-Day Per-Person Project Plan in DOCX format
for Google Docs / Microsoft Word import.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_plan_docx(output_path: str):
    doc = Document()

    # Page Margins: 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    PRIMARY = RGBColor(30, 58, 138)       # Navy
    SECONDARY = RGBColor(37, 99, 235)    # Blue
    DARK_TEXT = RGBColor(30, 41, 59)     # Slate 800

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("PolicyPilot: Day-by-Day Project Plan\n(Per-Person Allocation)")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("AI/ML Internship Capstone Project — Team 2\nMentor Assignment & Google Docs Implementation Guide")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = SECONDARY

    doc.add_paragraph() # Spacing

    # Executive Overview
    h_ov = doc.add_heading("1. Project Executive Overview & Team Roster", level=1)
    h_ov.runs[0].font.color.rgb = PRIMARY

    p_desc = doc.add_paragraph(
        "This document details the complete 8-Day milestone execution plan for PolicyPilot (RAG-based HR & IT Policy Assistant). "
        "Every day is partitioned into specific morning and afternoon deliverables for each team member, including individual evidence artifacts, "
        "daily standup formats, and viva oral exam preparation."
    )
    p_desc.runs[0].font.size = Pt(11)

    # Roster Table
    table_roster = doc.add_table(rows=5, cols=4)
    table_roster.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Member Name", "Assigned Subsystem", "Primary Tech Stack", "Core Viva Exam Focus"]
    for i, h in enumerate(headers):
        cell = table_roster.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1E3A8A")
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(10)

    roster_data = [
        ("Ijas", "Data & Text Pipeline", "Python, Regex, Pydantic, Chunking", "Document parsing, character offsets, data cleaning & chunk ablation"),
        ("Mano", "Retrieval Engineer", "TF-IDF, Cosine Similarity, Vector DB", "Vector space modeling, Top-k retrieval, Recall@k formulas, MRR"),
        ("Rahul", "Intent & Evaluation", "Scikit-Learn, MLP Neural Net, Metrics", "Multi-Layer Perceptron (ANN), Per-class F1, confusion matrix, RAG rubric"),
        ("Rohith", "RAG & Productization", "FastAPI, Grounded RAG, UI, Pytest", "Prompt grounding, abstention gating, REST API architecture & automated testing")
    ]

    for row_idx, row in enumerate(roster_data, start=1):
        for col_idx, val in enumerate(row):
            cell = table_roster.cell(row_idx, col_idx)
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F1F5F9")

    doc.add_paragraph() # Spacing

    # -------------------------------------------------------------
    # 8-DAY GRANULAR BREAKDOWN
    # -------------------------------------------------------------
    days_data = [
        {
            "day": "Day 1",
            "title": "Kickoff, Problem Formulation, Scope & Data Audit",
            "milestone": "Project charter, GitHub repository initialization, and dataset verification.",
            "ijas": {
                "morning": "Inspect all raw policy text files (HR-001 through HR-003, IT-001 through IT-003). Check text encoding (UTF-8), newline formats, and trailing disclaimers.",
                "afternoon": "Create data dictionary recording document provenance, policy IDs, titles, and word/character counts. Commit verified data files into data/raw/.",
                "deliverables": "data/raw/ verified, data dictionary committed in docs/data_dictionary.md.",
                "viva": "Why must metadata (policy ID and title) be extracted during ingestion rather than lost in text chunking?"
            },
            "mano": {
                "morning": "Review vector database literature (dense embeddings vs sparse representations). Set up scikit-learn and numpy environment.",
                "afternoon": "Define retrieval baseline specifications: top-k ranking criteria, similarity distance metric (cosine similarity), and threshold parameters.",
                "deliverables": "configs/retrieval_config.json containing initial vector parameters.",
                "viva": "What is the mathematical definition of Cosine Similarity and how does it differ from Euclidean distance in high-dimensional text spaces?"
            },
            "rahul": {
                "morning": "Audit the 10 starter benchmark questions in evaluation_questions.csv. Categorize them into answerable vs unanswerable types.",
                "afternoon": "Define the 7 intent classification categories: leave, remote_work, credentials, device_security, incidents, expenses, and unknown.",
                "deliverables": "Initial label taxonomy document in docs/intent_taxonomy.md.",
                "viva": "Why is an explicit 'unknown' or out-of-scope intent category required for enterprise governance?"
            },
            "rohith": {
                "morning": "Review Capstone Playbook functional requirements and 100-point rubric. Draft project charter and acceptance criteria.",
                "afternoon": "Initialize Git repository with standard structure (data, docs, src, tests, configs, reports). Set up task board with columns (Backlog -> Ready -> In Progress -> Review -> Done).",
                "deliverables": "Repository structure committed, README.md initial charter, requirements.txt draft.",
                "viva": "What are the core acceptance criteria that distinguish PolicyPilot from an open-domain chatbot?"
            }
        },
        {
            "day": "Day 2",
            "title": "Corpus Ingestion, Normalization & Baseline Retrieval",
            "milestone": "Working ingestion parser and first end-to-end baseline retrieval script.",
            "ijas": {
                "morning": "Implement parse_policy_file() and load_all_policies() in src/data/ingestion.py using Pydantic PolicyDocument models.",
                "afternoon": "Add normalization routines: whitespace collapsing, header extraction, and category tagging (HR vs IT). Write unit tests for ingestion.",
                "deliverables": "src/data/ingestion.py passing validation tests on all policy files.",
                "viva": "How does your parser handle missing or malformed 'Policy ID:' headers?"
            },
            "mano": {
                "morning": "Implement PolicyVectorRetriever in src/models/retriever.py using TF-IDF vectorization and cosine similarity matrix multiplication.",
                "afternoon": "Test retrieval on starter queries: verify that 'How early should planned leave be submitted?' retrieves HR-001 at rank 1.",
                "deliverables": "Working baseline retriever script in src/models/retriever.py.",
                "viva": "Explain the difference between term frequency (TF) and inverse document frequency (IDF)."
            },
            "rahul": {
                "morning": "Draft initial labeled dataset of 70 query examples (10 per class) with realistic employee phrasing.",
                "afternoon": "Implement baseline classifier using LogisticRegression in src/models/intent_classifier.py. Record baseline weighted F1 score.",
                "deliverables": "src/models/intent_classifier.py baseline implementation.",
                "viva": "Why is Logistic Regression a suitable classical baseline before training a neural network?"
            },
            "rohith": {
                "morning": "Define grounded prompt template and strict citation syntax (e.g. 'According to [HR-001] (Title): ...').",
                "afternoon": "Define exact refusal / abstention message format for unanswerable queries. Draft docs/weekly_status.md for Sprint 1.",
                "deliverables": "Initial weekly_status.md report with Sprint 1 completed evidence.",
                "viva": "Why must an enterprise assistant abstain instead of giving an approximate answer?"
            }
        },
        {
            "day": "Day 3",
            "title": "Minimum Viable Workflow (MVW) & Mentor Architecture Review",
            "milestone": "Full pipeline connected: Ingestion -> Chunking -> Retrieval -> Intent -> RAG Output.",
            "ijas": {
                "morning": "Implement sentence-level chunking in src/features/chunking.py using punctuation boundary regex.",
                "afternoon": "Ensure DocumentChunk models preserve start_char, end_char, and parent policy_id. Implement chunk_by_window() for comparison.",
                "deliverables": "src/features/chunking.py with sentence and sliding-window chunkers.",
                "viva": "What are the trade-offs between sentence-level chunking and fixed token-window chunking?"
            },
            "mano": {
                "morning": "Index sentence chunks into the vector retriever. Update retrieval output to return chunk IDs and source snippets.",
                "afternoon": "Implement top-k filtering with score thresholds to suppress irrelevant chunks.",
                "deliverables": "Enhanced retriever returning structured RetrievalResult objects with scores.",
                "viva": "How do you choose an appropriate relevance threshold tau to separate signal from noise?"
            },
            "rahul": {
                "morning": "Connect intent classification output to the retrieval pipeline so that mapped policy IDs can cross-validate retrieval hits.",
                "afternoon": "Record baseline metrics: weighted F1, per-class precision, recall, and train-test split reproducibility seed (random_state=42).",
                "deliverables": "Intent classifier baseline metrics logged in reports/.",
                "viva": "How do you handle class imbalance when evaluating multi-class text classifiers?"
            },
            "rohith": {
                "morning": "Implement PolicyPilotRAGEngine in src/models/rag_engine.py connecting Ingestion, Retrieval, Intent, and Answer Synthesis.",
                "afternoon": "Implement decision gate: check if intent == 'unknown' or retrieval score < threshold, then trigger abstention response.",
                "deliverables": "End-to-end command python -m src.models.rag_engine running successfully.",
                "viva": "Walk through the exact control flow when a user submits a query to PolicyPilot."
            }
        },
        {
            "day": "Day 4",
            "title": "Model, Retrieval & Extraction Improvements",
            "milestone": "Neural network MLP classifier trained and chunk size ablation study completed.",
            "ijas": {
                "morning": "Run corpus statistics audit: calculate chunk length distributions, token density, and boundary integrity.",
                "afternoon": "Ingest extended leave subpolicies (HR-004 through HR-008) to support granular leave entitlements (annual, sick, carry-forward, unpaid).",
                "deliverables": "Expanded policy documents indexed in data/raw/.",
                "viva": "How does adding modular subpolicies affect chunk boundary granularity?"
            },
            "mano": {
                "morning": "Conduct chunk size ablation study: compare Sentence Chunking vs Window 150/30 overlap vs Window 250/50 overlap.",
                "afternoon": "Calculate Mean Reciprocal Rank (MRR) and Recall@k for each strategy. Document findings showing sentence chunking superiority (0.923 MRR).",
                "deliverables": "Ablation report documented in reports/evaluation_report.md.",
                "viva": "Why did sentence-level chunking achieve a higher MRR than sliding-window chunking in our corpus?"
            },
            "rahul": {
                "morning": "Expand labeled intent dataset to 140 balanced examples (20 per class) with paraphrased questions and domain vocabulary.",
                "afternoon": "Train Multi-Layer Perceptron (ANN) with architecture (64, 32) using L-BFGS solver. Show that MLP achieves 76.7% F1, beating the baseline.",
                "deliverables": "Trained MLP neural network classifier in src/models/intent_classifier.py.",
                "viva": "Why did the L-BFGS Quasi-Newton solver outperform Adam on our curated feature representation?"
            },
            "rohith": {
                "morning": "Refine citation formatting in rag_engine.py to inject exact document citations [HR-001] into generated text.",
                "afternoon": "Add latency benchmarking: record per-query processing time in milliseconds (sub-15ms performance).",
                "deliverables": "RAG engine delivering answers with exact citations and latency tracking.",
                "viva": "How do you ensure the LLM or synthesis module never introduces claims absent from retrieved evidence?"
            }
        },
        {
            "day": "Day 5",
            "title": "Evaluation Set, Metrics, Error Analysis & Security Review",
            "milestone": "Full benchmark evaluation across 20 core + 100 leave queries, error analysis, and security audit.",
            "ijas": {
                "morning": "Audit evaluation datasets (evaluation_questions.csv and PolicyPilot_Leave_QA_Dataset_100.csv) to guarantee strict zero-leakage separation from training.",
                "afternoon": "Verify document offset traceability from test queries back to source character positions.",
                "deliverables": "Cleaned, schema-verified evaluation datasets in data/raw/.",
                "viva": "What is data leakage in NLP evaluation, and what steps did you take to prevent it?"
            },
            "mano": {
                "morning": "Calculate formal retrieval metrics: Recall@1 (92.3%), Recall@3 (100.0%), and MRR (0.923).",
                "afternoon": "Perform retrieval error analysis: identify near-misses and examine cosine score distributions on unanswerable queries.",
                "deliverables": "Retrieval metrics section in reports/evaluation_report.md.",
                "viva": "Define Mean Reciprocal Rank (MRR) mathematically and compute it for a sample query ranking."
            },
            "rahul": {
                "morning": "Implement PolicyPilotEvaluator in src/models/evaluation.py to automate full benchmark runs across answerable and unanswerable queries.",
                "afternoon": "Compute Abstention Precision, Recall, and F1 Score (achieving 1.000 / 100% on benchmark unanswerables). Generate confusion matrix.",
                "deliverables": "Automated evaluation runner and reports/evaluation_report.json.",
                "viva": "Why is Abstention F1 a more critical metric than raw accuracy in enterprise compliance assistants?"
            },
            "rohith": {
                "morning": "Conduct security review: test prompt injection queries attempting to bypass policy rules or force fake policy claims.",
                "afternoon": "Implement deterministic Python decision gating outside prompt context so abstention cannot be overridden by user prompts.",
                "deliverables": "Security audit report in docs/model_card.md.",
                "viva": "How does architectural separation of decision gating protect against prompt injection attacks?"
            }
        },
        {
            "day": "Day 6",
            "title": "API, Web UI, Automated Tests & Productization",
            "milestone": "FastAPI REST service deployed, interactive browser dashboard live, and 7/7 automated tests passing.",
            "ijas": {
                "morning": "Write unit tests for parse_policy_file(), schema validation, and chunk boundary preservation in tests/test_pipeline.py.",
                "afternoon": "Verify ingestion behavior under empty files, special characters, and boundary conditions.",
                "deliverables": "Ingestion and chunking unit test cases in test suite.",
                "viva": "How do your automated tests verify that chunk character offsets are non-negative and strictly increasing?"
            },
            "mano": {
                "morning": "Write unit tests for PolicyVectorRetriever: test top-1 retrieval, threshold filtering, and empty query handling.",
                "afternoon": "Optimize vector index creation time and memory footprint during FastAPI startup.",
                "deliverables": "Retriever unit test cases in test suite.",
                "viva": "What is the computational complexity of cosine similarity search over N document chunks?"
            },
            "rahul": {
                "morning": "Write unit tests for IntentClassifierService: assert MLP F1 >= 0.70 and verify unknown category routing.",
                "afternoon": "Write automated evaluation runner test asserting overall accuracy >= 0.85.",
                "deliverables": "Intent classifier and evaluation test cases in test suite.",
                "viva": "Why is stratified k-fold cross-validation preferred over random train-test splitting?"
            },
            "rohith": {
                "morning": "Implement FastAPI REST API in src/api/main.py with endpoints (/ask, /classify-intent, /policies, /metrics, /health).",
                "afternoon": "Build interactive browser UI with preset test buttons, real-time citation pills, and live benchmark scorecard. Pass all 7 pytest tests.",
                "deliverables": "FastAPI server and Web UI running on http://127.0.0.1:8000; 7/7 pytest tests passing.",
                "viva": "Explain the role of FastAPI lifespan event handlers in pre-loading machine learning models."
            }
        },
        {
            "day": "Day 7",
            "title": "Feature Freeze, Reproducibility Check, Model Card & Demo Rehearsal",
            "milestone": "Zero code changes; full documentation finalized; 14-minute demo dry-run completed.",
            "ijas": {
                "morning": "Conduct clean environment reproducibility check: clone repo, install requirements.txt, and verify ingestion runs end-to-end.",
                "afternoon": "Document corpus inventory and licensing statement in docs/model_card.md.",
                "deliverables": "Reproducibility verification sign-off in weekly_status.md.",
                "viva": "If an auditor asks for the provenance of this dataset, what documentation proves it is synthetic training data?"
            },
            "mano": {
                "morning": "Prepare retrieval failure examples and boundary cases for presentation slide 11.",
                "afternoon": "Formulate production scaling roadmap: moving from in-memory cosine index to ChromaDB / FAISS for 100k+ documents.",
                "deliverables": "Retrieval failure analysis and vector scaling architecture diagram.",
                "viva": "How would you scale this vector retrieval system from 12 policy files to 50,000 corporate documents?"
            },
            "rahul": {
                "morning": "Finalize docs/model_card.md following official Capstone template (intended use, out-of-scope, metrics, limitations).",
                "afternoon": "Rehearse presentation Part 4 (Metrics, Error Analysis & Limitations) strictly within the 3-minute time allocation.",
                "deliverables": "Completed docs/model_card.md and rehearsed speaking segment.",
                "viva": "What are the primary limitations of the current intent classification and RAG evaluation model?"
            },
            "rohith": {
                "morning": "Generate final 12-slide presentation deck (PolicyPilot_Final_Presentation.pptx) and presentation_script.md.",
                "afternoon": "Lead 14-minute full team demo rehearsal: time each segment according to Section 12 of the Playbook.",
                "deliverables": "reports/PolicyPilot_Final_Presentation.pptx and recorded demo timing log.",
                "viva": "How do you coordinate the live demonstration transition between the UI demo and technical viva defense?"
            }
        },
        {
            "day": "Day 8",
            "title": "Final Presentation, Live Demonstration, Individual Viva & Project Handover",
            "milestone": "14-minute presentation delivered to mentors, viva defended, and 100-point rubric scored.",
            "ijas": {
                "morning": "Deliver Part 1 (Minutes 0:00 - 2:00): Problem statement, enterprise hallucination liability, user journey, and scope.",
                "afternoon": "Defend Viva Subsystem: Document parsing, chunking boundary preservation, and data quality validation.",
                "deliverables": "Part 1 presentation delivery and individual viva completion.",
                "viva": "Explain how data preprocessing prevents token fragmentation at sentence boundaries."
            },
            "mano": {
                "morning": "Co-present Part 3 (Minutes 5:00 - 8:00): Vector search architecture, sublinear TF-IDF, and chunk size ablation results.",
                "afternoon": "Defend Viva Subsystem: Vector retrieval, cosine similarity, Recall@k formulas, and threshold tuning.",
                "deliverables": "Part 3 presentation delivery and individual viva completion.",
                "viva": "Why is Recall@3 at 100% sufficient for feeding an extractive grounded RAG prompt?"
            },
            "rahul": {
                "morning": "Deliver Part 4 (Minutes 8:00 - 11:00): Benchmark metrics, MLP neural network vs baseline comparison, and failure analysis.",
                "afternoon": "Defend Viva Subsystem: Multi-Layer Perceptron architecture, backpropagation, and per-class confusion matrices.",
                "deliverables": "Part 4 presentation delivery and individual viva completion.",
                "viva": "Walk through your confusion matrix and explain which class had the highest misclassification rate and why."
            },
            "rohith": {
                "morning": "Lead Part 2 (Minutes 2:00 - 5:00) Live End-to-End Demo: Demonstrate answerable query with citations, and unanswerable query with clean abstention.",
                "afternoon": "Defend Viva Subsystem: Grounded RAG synthesis, abstention gating, FastAPI REST server, and automated test suite.",
                "deliverables": "Live demo execution, presentation conclusion, and individual viva completion.",
                "viva": "How does PolicyPilot guarantee that unanswerable queries abstain with zero hallucination?"
            }
        }
    ]

    for day_info in days_data:
        h = doc.add_heading(f"{day_info['day']}: {day_info['title']}", level=2)
        h.runs[0].font.color.rgb = PRIMARY

        p_m = doc.add_paragraph()
        r_m_label = p_m.add_run("Day Milestone: ")
        r_m_label.bold = True
        r_m_label.font.color.rgb = SECONDARY
        p_m.add_run(day_info["milestone"])

        # Create Day Table for 4 Persons
        table = doc.add_table(rows=5, cols=5)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cols = ["Team Member", "Morning Focus (9 AM - 1 PM)", "Afternoon Focus (2 PM - 5:30 PM)", "Daily Deliverable Artifact", "Viva Question Focus"]
        for ci, ctitle in enumerate(cols):
            cell = table.cell(0, ci)
            cell.text = ctitle
            set_cell_background(cell, "1E3A8A")
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)

        members = [("Ijas (Data)", day_info["ijas"]), ("Mano (Retrieval)", day_info["mano"]), ("Rahul (Intent/Eval)", day_info["rahul"]), ("Rohith (RAG/API)", day_info["rohith"])]
        for ri, (mname, mdata) in enumerate(members, start=1):
            row_cells = table.rows[ri].cells
            row_cells[0].text = mname
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[0].paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_background(row_cells[0], "E2E8F0")

            row_cells[1].text = mdata["morning"]
            row_cells[1].paragraphs[0].runs[0].font.size = Pt(8.5)

            row_cells[2].text = mdata["afternoon"]
            row_cells[2].paragraphs[0].runs[0].font.size = Pt(8.5)

            row_cells[3].text = mdata["deliverables"]
            row_cells[3].paragraphs[0].runs[0].font.size = Pt(8.5)
            row_cells[3].paragraphs[0].runs[0].font.bold = True

            row_cells[4].text = mdata["viva"]
            row_cells[4].paragraphs[0].runs[0].font.size = Pt(8.5)
            row_cells[4].paragraphs[0].runs[0].font.italic = True

            if ri % 2 == 0:
                for c in row_cells[1:]:
                    set_cell_background(c, "F8FAFC")

        doc.add_paragraph() # Spacing

    # -------------------------------------------------------------
    # STANDUP TEMPLATE & VIVA GUIDE
    # -------------------------------------------------------------
    h_sync = doc.add_heading("3. Daily Standup Update Template (For Mentor Tracking)", level=1)
    h_sync.runs[0].font.color.rgb = PRIMARY

    p_sync_desc = doc.add_paragraph(
        "Each intern must post this 3-line asynchronous update to the team board at the end of each working day:"
    )
    p_sync_desc.runs[0].font.size = Pt(10.5)

    code_box = doc.add_paragraph(
        "----------------------------------------------------------------------\n"
        "[Daily Standup Update]\n"
        "Name: <Ijas / Mano / Rahul / Rohith>\n"
        "Date: Day <1 to 8>\n"
        "Subsystem: <Assigned Role>\n"
        "• Completed Today (with evidence link): e.g. Ingested HR-001 to HR-008, committed in src/data/ingestion.py\n"
        "• Next for Tomorrow: e.g. Implement sentence chunking boundary offsets\n"
        "• Blockers / Risks: None\n"
        "----------------------------------------------------------------------"
    )
    code_box.runs[0].font.name = "Courier New"
    code_box.runs[0].font.size = Pt(9.5)
    code_box.runs[0].font.color.rgb = DARK_TEXT

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"DOCX Plan successfully created at: {output_path}")


if __name__ == "__main__":
    out_docx = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "docs", "PolicyPilot_Day_by_Day_Per_Person_Plan.docx")
    )
    create_plan_docx(out_docx)
