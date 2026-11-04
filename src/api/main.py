"""
FastAPI Server & Web Dashboard for PolicyPilot
Owner: Rohith (LLM / App Integration)

Provides:
- POST /ask : Grounded RAG query endpoint with citations & abstention
- POST /classify-intent : Dedicated intent classification endpoint
- GET /policies : Ingested policy repository metadata
- GET /metrics : Comprehensive retrieval, intent, and abstention metrics
- GET / : Clean interactive web UI for live demonstration
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.models.rag_engine import PolicyPilotRAGEngine, RAGResponse
from src.models.evaluation import PolicyPilotEvaluator

_engine: Optional[PolicyPilotRAGEngine] = None
_cached_metrics: Optional[Dict[str, Any]] = None


def get_engine() -> PolicyPilotRAGEngine:
    global _engine
    if _engine is None:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))
        _engine = PolicyPilotRAGEngine(data_dir=data_dir)
    return _engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup initialization
    eng = get_engine()
    global _cached_metrics
    evaluator = PolicyPilotEvaluator(eng)
    _cached_metrics = evaluator.run_evaluation()
    yield


app = FastAPI(
    title="PolicyPilot RAG API",
    description="Enterprise HR/IT Policy Assistant with Grounded Citations, Abstention & Intent Classification",
    version="1.0.0",
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "How early should planned leave be submitted?"})
    top_k: int = Field(default=3, ge=1, le=5)


class IntentRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "What are the rules for working from home?"})


@app.get("/health")
def health_check():
    eng = get_engine()
    return {
        "status": "healthy",
        "service": "PolicyPilot RAG",
        "policies_loaded": len(eng.documents),
        "chunks_indexed": len(eng.chunks),
    }


@app.get("/policies")
def list_policies():
    eng = get_engine()
    return [
        {
            "policy_id": doc.policy_id,
            "title": doc.title,
            "category": doc.category,
            "source_file": doc.source_file,
            "snippet": doc.normalized_content[:120] + "...",
        }
        for doc in eng.documents
    ]


@app.post("/ask", response_model=RAGResponse)
def ask_policy(request: QueryRequest):
    eng = get_engine()
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    return eng.answer_query(request.query, top_k=request.top_k)


@app.post("/classify-intent")
def classify_intent(request: IntentRequest):
    eng = get_engine()
    return eng.intent_service.predict(request.text)


@app.get("/metrics")
def get_metrics():
    global _cached_metrics
    if not _cached_metrics:
        eng = get_engine()
        evaluator = PolicyPilotEvaluator(eng)
        _cached_metrics = evaluator.run_evaluation()
    return _cached_metrics


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PolicyPilot — Enterprise HR/IT Policy Assistant</title>
        <style>
            :root {
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #1e293b;
                --text-muted: #64748b;
                --border: #e2e8f0;
                --success: #059669;
                --warning: #d97706;
                --danger: #dc2626;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            body { background: var(--bg); color: var(--text); padding: 2rem 1rem; }
            .container { max-width: 1000px; margin: 0 auto; }
            header { text-align: center; margin-bottom: 2rem; }
            header h1 { font-size: 2.2rem; color: #0f172a; margin-bottom: 0.5rem; }
            header p { color: var(--text-muted); font-size: 1.05rem; }
            .badge-team { display: inline-block; background: #dbeafe; color: var(--primary); padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; margin-top: 0.5rem; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
            @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
            .card { background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .card h2 { font-size: 1.25rem; margin-bottom: 1rem; color: #0f172a; }
            .input-group { margin-bottom: 1rem; }
            input[type="text"] { width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 1rem; outline: none; }
            input[type="text"]:focus { border-color: var(--primary); ring: 2px solid #bfdbfe; }
            button { background: var(--primary); color: white; border: none; padding: 0.75rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            button:hover { background: var(--primary-dark); }
            .presets { margin-top: 1rem; font-size: 0.9rem; }
            .presets span { font-weight: 600; color: var(--text-muted); }
            .preset-btn { background: #f1f5f9; color: #334155; border: 1px solid var(--border); padding: 0.25rem 0.6rem; border-radius: 6px; margin: 0.25rem 0.25rem 0 0; cursor: pointer; display: inline-block; }
            .preset-btn:hover { background: #e2e8f0; }
            .result-box { display: none; margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }
            .status-pill { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }
            .status-answered { background: #dcfce7; color: var(--success); }
            .status-abstained { background: #fee2e2; color: var(--danger); }
            .citations-list { margin-top: 0.75rem; }
            .citation-item { background: #f8fafc; border-left: 3px solid var(--primary); padding: 0.5rem 0.75rem; border-radius: 4px; margin-bottom: 0.5rem; font-size: 0.9rem; }
            .metrics-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.9rem; }
            .metrics-table th, .metrics-table td { text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border); }
            .team-roles { margin-top: 1rem; font-size: 0.85rem; color: var(--text-muted); }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🛡️ PolicyPilot Assistant</h1>
                <p>Enterprise RAG-Based HR & IT Policy Assistant with Grounded Citations & Abstention</p>
                <div class="badge-team">Team 2: Ijas, Mano, Rahul, Rohith</div>
            </header>

            <div class="grid">
                <!-- Query Console -->
                <div class="card">
                    <h2>Ask Policy Question</h2>
                    <div class="input-group">
                        <input type="text" id="queryInput" placeholder="e.g. How early should planned leave be submitted?">
                    </div>
                    <button onclick="submitQuery()">Ask PolicyPilot</button>

                    <div class="presets">
                        <span>Starter Benchmark:</span><br>
                        <span class="preset-btn" onclick="setQuery('How early should planned leave be submitted?')">Leave Notice</span>
                        <span class="preset-btn" onclick="setQuery('What should I do if an API key was exposed?')">Leaked API Key</span>
                        <span class="preset-btn" onclick="setQuery('Can I purchase equipment before approval?')">Purchase Policy</span>
                        <span class="preset-btn" onclick="setQuery('What is the company\'s maternity leave entitlement?')">Unanswerable: Maternity</span><br>
                        <span style="display:inline-block; margin-top:0.4rem;"><strong>100-Leave QA Benchmark:</strong></span><br>
                        <span class="preset-btn" onclick="setQuery('How many annual leave days do full-time employees receive?')">18 Days Annual (LQ001)</span>
                        <span class="preset-btn" onclick="setQuery('What happens if I am sick for more than two consecutive working days?')">Sick Cert (LQ011)</span>
                        <span class="preset-btn" onclick="setQuery('Can unused annual leave be carried forward?')">Carry Forward (LQ013)</span>
                        <span class="preset-btn" onclick="setQuery('Can I encash my unused annual leave?')">Unanswerable: Encash (LQ021)</span>
                        <span class="preset-btn" onclick="setQuery('Does the company offer half-day leave?')">Unanswerable: Half-Day (LQ029)</span>
                    </div>

                    <div id="resultBox" class="result-box">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                            <span id="statusBadge" class="status-pill"></span>
                            <span style="font-size:0.85rem; color:var(--text-muted);" id="latencyBadge"></span>
                        </div>
                        <div style="margin-bottom:0.75rem;">
                            <strong>Detected Intent:</strong> <span id="intentText"></span>
                        </div>
                        <div style="margin-bottom:0.75rem;">
                            <strong>Answer:</strong>
                            <p id="answerText" style="margin-top:0.25rem; line-height:1.5; color:#0f172a;"></p>
                        </div>
                        <div id="citationsContainer">
                            <strong>Grounded Citations:</strong>
                            <div id="citationsList" class="citations-list"></div>
                        </div>
                    </div>
                </div>

                <!-- Live Metrics & Evaluation -->
                <div class="card">
                    <h2>Live Evaluation Dashboard</h2>
                    <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">
                        Rigorous metrics evaluated across answerable, unanswerable, and paraphrased test sets.
                    </p>
                    <table class="metrics-table" id="metricsTable">
                        <tr><td>Loading benchmarks...</td></tr>
                    </table>

                    <div class="team-roles">
                        <strong>Team Ownership:</strong><br>
                        • <strong>Ijas:</strong> Ingestion & Chunking Pipeline<br>
                        • <strong>Mano:</strong> Vector Retrieval & Cosine Index<br>
                        • <strong>Rahul:</strong> Neural Net Intent Classifier & Evaluation<br>
                        • <strong>Rohith:</strong> Grounded RAG, Abstention & API/UI
                    </div>
                </div>
            </div>
        </div>

        <script>
            function setQuery(text) {
                document.getElementById('queryInput').value = text;
                submitQuery();
            }

            async function submitQuery() {
                const q = document.getElementById('queryInput').value.trim();
                if (!q) return;

                const resBox = document.getElementById('resultBox');
                resBox.style.display = 'block';
                document.getElementById('answerText').innerText = "Processing through retriever & intent classifier...";

                try {
                    const resp = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: q, top_k: 3 })
                    });
                    const data = await resp.json();

                    const statusBadge = document.getElementById('statusBadge');
                    statusBadge.innerText = data.status;
                    statusBadge.className = 'status-pill ' + (data.status === 'ANSWERED' ? 'status-answered' : 'status-abstained');

                    document.getElementById('latencyBadge').innerText = data.processing_time_ms + ' ms';
                    document.getElementById('intentText').innerText = data.intent + ' (' + (data.intent_confidence * 100).toFixed(1) + '%)';
                    document.getElementById('answerText').innerText = data.answer;

                    const citContainer = document.getElementById('citationsContainer');
                    const citList = document.getElementById('citationsList');
                    citList.innerHTML = '';

                    if (data.citations && data.citations.length > 0) {
                        citContainer.style.display = 'block';
                        data.citations.forEach(c => {
                            const div = document.createElement('div');
                            div.className = 'citation-item';
                            div.innerHTML = '<strong>[' + c.policy_id + '] ' + c.title + '</strong> (Score: ' + c.relevance_score.toFixed(3) + ')<br>' + c.snippet;
                            citList.appendChild(div);
                        });
                    } else {
                        citContainer.style.display = 'none';
                    }
                } catch(e) {
                    document.getElementById('answerText').innerText = "Error contacting API: " + e.message;
                }
            }

            async function loadMetrics() {
                try {
                    const resp = await fetch('/metrics');
                    const m = await resp.json();
                    const table = document.getElementById('metricsTable');
                    table.innerHTML = `
                        <tr><th>Metric</th><th>Score</th><th>Target</th></tr>
                        <tr><td>Overall System Accuracy</td><td><strong>${(m.overall_system_accuracy * 100).toFixed(1)}%</strong></td><td>> 85%</td></tr>
                        <tr><td>Retrieval MRR</td><td><strong>${(m.retrieval_metrics.mrr * 100).toFixed(1)}%</strong></td><td>> 80%</td></tr>
                        <tr><td>Recall@1 (Top 1)</td><td><strong>${(m.retrieval_metrics.recall_at_1 * 100).toFixed(1)}%</strong></td><td>> 75%</td></tr>
                        <tr><td>Recall@3 (Top 3)</td><td><strong>${(m.retrieval_metrics.recall_at_3 * 100).toFixed(1)}%</strong></td><td>> 90%</td></tr>
                        <tr><td>Abstention F1 Score</td><td><strong>${(m.abstention_metrics.f1_score * 100).toFixed(1)}%</strong></td><td>> 90%</td></tr>
                        <tr><td>Citation Accuracy</td><td><strong>${(m.citation_metrics.citation_accuracy * 100).toFixed(1)}%</strong></td><td>100%</td></tr>
                    `;
                } catch(e) {
                    console.error(e);
                }
            }

            window.onload = loadMetrics;
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
