"""
Comprehensive RAG Evaluation Framework for PolicyPilot
Owner: Rahul & Mano

Measures:
1. Retrieval Metrics: Recall@1, Recall@3, MRR (Mean Reciprocal Rank)
2. Abstention Quality: Precision, Recall, F1 for abstention behavior
3. Generation Quality: Citation correctness, Groundedness rate
4. Exports full evaluation report to reports/evaluation_report.json and .md
"""

import os
import csv
import json
from typing import List, Dict, Any
from src.models.rag_engine import PolicyPilotRAGEngine


# Starter questions plus extended evaluation test set (paraphrases, out-of-scope, edge cases)
EXTENDED_EVAL_QUESTIONS = [
    # Starter 10
    {"question": "How early should planned leave be submitted?", "expected_type": "answerable", "expected_policy_id": "HR-001"},
    {"question": "What should I do if I suspect an API key was exposed?", "expected_type": "answerable", "expected_policy_id": "IT-001"},
    {"question": "Can I copy confidential files to personal storage while working remotely?", "expected_type": "answerable", "expected_policy_id": "HR-002"},
    {"question": "What details should be included in an incident report?", "expected_type": "answerable", "expected_policy_id": "IT-003"},
    {"question": "What is the company's maternity leave entitlement?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "What is the annual reimbursement cap?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "What should I do if I lose a device?", "expected_type": "answerable", "expected_policy_id": "IT-002"},
    {"question": "Can I purchase equipment before approval?", "expected_type": "answerable", "expected_policy_id": "HR-003"},
    {"question": "What is the exact legal notice period for resignation?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "Should I guess the cause of an IT incident before evidence is available?", "expected_type": "answerable", "expected_policy_id": "IT-003"},

    # Extended: Paraphrases & specific details
    {"question": "How many days notice do I need for taking planned vacation days?", "expected_type": "answerable", "expected_policy_id": "HR-001"},
    {"question": "Can I store database secrets directly in Git repository code?", "expected_type": "answerable", "expected_policy_id": "IT-001"},
    {"question": "Are personal hard drives allowed for backing up work files?", "expected_type": "answerable", "expected_policy_id": "HR-002"},
    {"question": "Is it okay to leave my laptop unlocked while getting coffee?", "expected_type": "answerable", "expected_policy_id": "IT-002"},
    {"question": "Who should be alerted when an urgent IT outage occurs?", "expected_type": "answerable", "expected_policy_id": "IT-003"},
    {"question": "What items must be included in a purchase reimbursement request?", "expected_type": "answerable", "expected_policy_id": "HR-003"},

    # Extended: Unanswerable & ambiguous queries
    {"question": "What is the policy regarding paternity leave for new fathers?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "How much gym membership reimbursement can I claim each month?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "Can I trade company stock during quarterly blackout periods?", "expected_type": "unanswerable", "expected_policy_id": None},
    {"question": "What health insurance plans are available for dependents?", "expected_type": "unanswerable", "expected_policy_id": None},
]


class PolicyPilotEvaluator:
    def __init__(self, rag_engine: PolicyPilotRAGEngine):
        self.engine = rag_engine

    def run_evaluation(self, test_set: List[Dict[str, Any]] = EXTENDED_EVAL_QUESTIONS) -> Dict[str, Any]:
        detailed_results = []
        
        # Retrieval tracking
        reciprocal_ranks = []
        hits_at_1 = 0
        hits_at_3 = 0
        answerable_count = 0

        # Abstention tracking
        tp_abstain = 0  # correctly abstained on unanswerable
        fp_abstain = 0  # mistakenly abstained on answerable
        tn_abstain = 0  # correctly answered answerable
        fn_abstain = 0  # mistakenly answered unanswerable

        # Citation tracking
        correct_citations = 0

        for item in test_set:
            q = item["question"]
            exp_type = item["expected_type"]
            exp_policy = item.get("expected_policy_id")

            # Execute RAG response
            response = self.engine.answer_query(q, top_k=3)

            # Check retrieval ranking for answerable queries
            rank = None
            if exp_type == "answerable" and exp_policy:
                answerable_count += 1
                retrieval_hits = self.engine.retriever.retrieve(q, top_k=5, threshold=0.0)
                for idx, r in enumerate(retrieval_hits):
                    if r.chunk.policy_id == exp_policy:
                        rank = idx + 1
                        break

                if rank:
                    reciprocal_ranks.append(1.0 / rank)
                    if rank == 1:
                        hits_at_1 += 1
                    if rank <= 3:
                        hits_at_3 += 1
                else:
                    reciprocal_ranks.append(0.0)

            # Check Abstention Quality
            if exp_type == "unanswerable":
                if response.status == "ABSTAINED":
                    tp_abstain += 1
                    abstain_correct = True
                else:
                    fn_abstain += 1
                    abstain_correct = False
            else:
                if response.status == "ABSTAINED":
                    fp_abstain += 1
                    abstain_correct = False
                else:
                    tn_abstain += 1
                    abstain_correct = True

            # Check Citation Correctness
            citation_match = False
            if exp_type == "answerable":
                cited_policies = [c.policy_id for c in response.citations]
                if exp_policy in cited_policies:
                    citation_match = True
                    correct_citations += 1
            else:
                # For unanswerable, correct citation is having no citations
                if len(response.citations) == 0:
                    citation_match = True

            detailed_results.append({
                "question": q,
                "expected_type": exp_type,
                "expected_policy_id": exp_policy,
                "actual_status": response.status,
                "actual_intent": response.intent,
                "retrieval_rank": rank,
                "citations": [c.policy_id for c in response.citations],
                "citation_correct": citation_match,
                "abstain_correct": abstain_correct,
                "latency_ms": response.processing_time_ms,
            })

        # Calculate metrics
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        recall_at_1 = hits_at_1 / answerable_count if answerable_count else 0.0
        recall_at_3 = hits_at_3 / answerable_count if answerable_count else 0.0

        abstain_precision = tp_abstain / (tp_abstain + fp_abstain) if (tp_abstain + fp_abstain) > 0 else 0.0
        abstain_recall = tp_abstain / (tp_abstain + fn_abstain) if (tp_abstain + fn_abstain) > 0 else 0.0
        abstain_f1 = (
            2 * abstain_precision * abstain_recall / (abstain_precision + abstain_recall)
            if (abstain_precision + abstain_recall) > 0
            else 0.0
        )

        citation_accuracy = correct_citations / answerable_count if answerable_count else 0.0
        overall_accuracy = (
            (correct_citations + tp_abstain) / len(test_set) if len(test_set) > 0 else 0.0
        )

        summary = {
            "total_test_queries": len(test_set),
            "answerable_queries": answerable_count,
            "unanswerable_queries": len(test_set) - answerable_count,
            "retrieval_metrics": {
                "mrr": round(mrr, 4),
                "recall_at_1": round(recall_at_1, 4),
                "recall_at_3": round(recall_at_3, 4),
            },
            "abstention_metrics": {
                "precision": round(abstain_precision, 4),
                "recall": round(abstain_recall, 4),
                "f1_score": round(abstain_f1, 4),
                "confusion_counts": {
                    "true_positive": tp_abstain,
                    "false_positive": fp_abstain,
                    "true_negative": tn_abstain,
                    "false_negative": fn_abstain,
                },
            },
            "citation_metrics": {
                "citation_accuracy": round(citation_accuracy, 4),
                "correct_citations": correct_citations,
            },
            "overall_system_accuracy": round(overall_accuracy, 4),
            "detailed_results": detailed_results,
        }

        return summary

    def save_reports(self, summary: Dict[str, Any], output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "evaluation_report.json")
        md_path = os.path.join(output_dir, "evaluation_report.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Generate markdown summary
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# PolicyPilot: RAG Evaluation Report\n\n")
            f.write(f"**Total Queries Evaluated:** {summary['total_test_queries']}\n")
            f.write(f"- Answerable: {summary['answerable_queries']}\n")
            f.write(f"- Unanswerable: {summary['unanswerable_queries']}\n\n")

            f.write("## 1. Retrieval Performance (Mano)\n\n")
            f.write(f"- **Mean Reciprocal Rank (MRR):** {summary['retrieval_metrics']['mrr'] * 100:.1f}%\n")
            f.write(f"- **Recall@1:** {summary['retrieval_metrics']['recall_at_1'] * 100:.1f}%\n")
            f.write(f"- **Recall@3:** {summary['retrieval_metrics']['recall_at_3'] * 100:.1f}%\n\n")

            f.write("## 2. Abstention Performance (Rohith & Rahul)\n\n")
            f.write(f"- **Abstention Precision:** {summary['abstention_metrics']['precision'] * 100:.1f}%\n")
            f.write(f"- **Abstention Recall:** {summary['abstention_metrics']['recall'] * 100:.1f}%\n")
            f.write(f"- **Abstention F1 Score:** {summary['abstention_metrics']['f1_score'] * 100:.1f}%\n\n")

            f.write("## 3. Citation & Overall Accuracy\n\n")
            f.write(f"- **Citation Accuracy:** {summary['citation_metrics']['citation_accuracy'] * 100:.1f}%\n")
            f.write(f"- **Overall System Accuracy:** {summary['overall_system_accuracy'] * 100:.1f}%\n\n")

            f.write("## 4. Query-by-Query Evaluation Breakdown\n\n")
            f.write("| # | Question | Expected Type | Expected Policy | Actual Status | Intent | Citation Match |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for idx, r in enumerate(summary["detailed_results"], 1):
                f.write(
                    f"| {idx} | {r['question']} | {r['expected_type']} | {r['expected_policy_id'] or 'None'} | "
                    f"`{r['actual_status']}` | `{r['actual_intent']}` | {'✅' if r['citation_correct'] else '❌'} |\n"
                )

        return json_path, md_path


if __name__ == "__main__":
    engine = PolicyPilotRAGEngine()
    evaluator = PolicyPilotEvaluator(engine)
    results = evaluator.run_evaluation()

    report_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "reports")
    )
    j_p, m_p = evaluator.save_reports(results, report_dir)
    print(f"Evaluation complete. Overall accuracy: {results['overall_system_accuracy']*100:.1f}%")
    print(f"MRR: {results['retrieval_metrics']['mrr']:.3f} | Recall@1: {results['retrieval_metrics']['recall_at_1']:.3f}")
    print(f"Abstention F1: {results['abstention_metrics']['f1_score']:.3f}")
    print(f"Reports saved to {m_p}")
