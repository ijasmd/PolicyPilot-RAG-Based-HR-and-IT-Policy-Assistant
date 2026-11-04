"""
Evaluation script specifically benchmarked against the 100-Question Leave Dataset (LQ001-LQ100)
Owner: Rahul & Mano
"""

import os
import csv
import json
from src.models.rag_engine import PolicyPilotRAGEngine
from src.models.evaluation import PolicyPilotEvaluator

def run_leave_100_benchmark():
    csv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "raw", "PolicyPilot_Leave_QA_Dataset_100.csv")
    )
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"100-question dataset not found at: {csv_path}")

    test_set = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_set.append({
                "question_id": row["question_id"],
                "question": row["question"],
                "expected_answer": row["expected_answer"],
                "expected_type": row["answerability"].strip().lower(),
                "expected_policy_id": row["source_policy_id"].strip() if row["source_policy_id"].strip() else None
            })

    print(f"Loaded {len(test_set)} leave questions from {os.path.basename(csv_path)}")

    engine = PolicyPilotRAGEngine()
    evaluator = PolicyPilotEvaluator(engine)
    results = evaluator.run_evaluation(test_set)

    # Save dedicated report
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    report_md_path = os.path.join(reports_dir, "leave_dataset_100_report.md")

    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# PolicyPilot: 100-Question Leave QA Benchmark Report\n\n")
        f.write(f"**Total Queries Evaluated:** {len(test_set)}\n")
        f.write(f"- **Answerable Queries:** {results['answerable_queries']}\n")
        f.write(f"- **Unanswerable Queries:** {results['unanswerable_queries']}\n\n")

        f.write("## 1. Executive Summary Metrics\n\n")
        f.write("| Metric | Result | Benchmark Target | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Overall Accuracy** | **{results['overall_system_accuracy']*100:.1f}%** | > 80.0% | {'✅ Met' if results['overall_system_accuracy']>=0.80 else '⚠️ Review'} |\n")
        f.write(f"| **Mean Reciprocal Rank (MRR)** | **{results['retrieval_metrics']['mrr']*100:.1f}%** | > 80.0% | {'✅ Met' if results['retrieval_metrics']['mrr']>=0.80 else '⚠️ Review'} |\n")
        f.write(f"| **Recall@1 (Top 1)** | **{results['retrieval_metrics']['recall_at_1']*100:.1f}%** | > 75.0% | {'✅ Met' if results['retrieval_metrics']['recall_at_1']>=0.75 else '⚠️ Review'} |\n")
        f.write(f"| **Recall@3 (Top 3)** | **{results['retrieval_metrics']['recall_at_3']*100:.1f}%** | > 85.0% | {'✅ Met' if results['retrieval_metrics']['recall_at_3']>=0.85 else '⚠️ Review'} |\n")
        f.write(f"| **Abstention F1 Score** | **{results['abstention_metrics']['f1_score']*100:.1f}%** | > 80.0% | {'✅ Met' if results['abstention_metrics']['f1_score']>=0.80 else '⚠️ Review'} |\n")
        f.write(f"| **Citation Accuracy** | **{results['citation_metrics']['citation_accuracy']*100:.1f}%** | > 80.0% | {'✅ Met' if results['citation_metrics']['citation_accuracy']>=0.80 else '⚠️ Review'} |\n\n")

        f.write("## 2. Abstention Confusion Breakdown\n\n")
        f.write(f"- **True Positives (Correctly Abstained on Unanswerable):** {results['abstention_metrics']['confusion_counts']['true_positive']}\n")
        f.write(f"- **True Negatives (Correctly Answered Answerable):** {results['abstention_metrics']['confusion_counts']['true_negative']}\n")
        f.write(f"- **False Positives (Mistakenly Abstained):** {results['abstention_metrics']['confusion_counts']['false_positive']}\n")
        f.write(f"- **False Negatives (Mistakenly Answered):** {results['abstention_metrics']['confusion_counts']['false_negative']}\n\n")

        f.write("## 3. Sample Evaluation Details (First 20 Questions)\n\n")
        f.write("| ID | Question | Expected Type | Expected Policy | Actual Status | Citation Match |\n")
        f.write("|---|---|---|---|---|---|\n")
        for i, (q_data, r) in enumerate(zip(test_set[:20], results["detailed_results"][:20]), start=1):
            f.write(
                f"| {q_data['question_id']} | {r['question']} | {r['expected_type']} | "
                f"{r['expected_policy_id'] or 'None'} | `{r['actual_status']}` | {'✅' if r['citation_correct'] else '❌'} |\n"
            )

    print(f"Leave QA 100 Report successfully written to: {report_md_path}")
    print(f"Accuracy: {results['overall_system_accuracy']*100:.1f}% | MRR: {results['retrieval_metrics']['mrr']*100:.1f}% | Abstention F1: {results['abstention_metrics']['f1_score']*100:.1f}%")

if __name__ == "__main__":
    run_leave_100_benchmark()
