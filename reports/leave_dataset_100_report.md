# PolicyPilot: 100-Question Leave QA Benchmark Report

**Total Queries Evaluated:** 100
- **Answerable Queries:** 55
- **Unanswerable Queries:** 45

## 1. Executive Summary Metrics

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Overall Accuracy** | **84.0%** | > 80.0% | ✅ Met |
| **Mean Reciprocal Rank (MRR)** | **90.1%** | > 80.0% | ✅ Met |
| **Recall@1 (Top 1)** | **85.5%** | > 75.0% | ✅ Met |
| **Recall@3 (Top 3)** | **94.5%** | > 85.0% | ✅ Met |
| **Abstention F1 Score** | **85.1%** | > 80.0% | ✅ Met |
| **Citation Accuracy** | **85.5%** | > 80.0% | ✅ Met |

## 2. Abstention Confusion Breakdown

- **True Positives (Correctly Abstained on Unanswerable):** 37
- **True Negatives (Correctly Answered Answerable):** 50
- **False Positives (Mistakenly Abstained):** 5
- **False Negatives (Mistakenly Answered):** 8

## 3. Sample Evaluation Details (First 20 Questions)

| ID | Question | Expected Type | Expected Policy | Actual Status | Citation Match |
|---|---|---|---|---|---|
| LQ001 | How many annual leave days do full-time employees receive? | answerable | HR-004 | `ANSWERED` | ✅ |
| LQ002 | How is annual leave credited? | answerable | HR-004 | `ANSWERED` | ✅ |
| LQ003 | How many sick leave days are provided each year? | answerable | HR-005 | `ANSWERED` | ✅ |
| LQ004 | When can I use sick leave? | answerable | HR-005 | `ANSWERED` | ✅ |
| LQ005 | How many days of casual leave do employees get? | unanswerable | None | `ABSTAINED` | ✅ |
| LQ006 | How early should I apply for one day of planned leave? | answerable | HR-001 | `ANSWERED` | ✅ |
| LQ007 | How much notice is needed for two days of leave? | answerable | HR-001 | `ANSWERED` | ✅ |
| LQ008 | I need three consecutive days off. How early should I apply? | unanswerable | None | `ABSTAINED` | ✅ |
| LQ009 | What should I do if I need leave because of an emergency? | answerable | HR-003 | `ANSWERED` | ✅ |
| LQ010 | Can I take leave first and enter it later in the HR portal? | answerable | HR-003 | `ANSWERED` | ✅ |
| LQ011 | What happens if I am sick for more than two consecutive working days? | answerable | HR-006 | `ANSWERED` | ✅ |
| LQ012 | When should I submit my medical certificate after sick leave? | answerable | HR-006 | `ANSWERED` | ✅ |
| LQ013 | Can unused annual leave be carried forward? | answerable | HR-007 | `ANSWERED` | ✅ |
| LQ014 | What happens to annual leave above five days at year-end? | answerable | HR-007 | `ANSWERED` | ✅ |
| LQ015 | Can I carry forward unused sick leave? | unanswerable | None | `ABSTAINED` | ✅ |
| LQ016 | Can I take unpaid leave if my paid leave balance is zero? | answerable | HR-008 | `ANSWERED` | ✅ |
| LQ017 | Who needs to approve unpaid leave? | answerable | HR-008 | `ANSWERED` | ✅ |
| LQ018 | Is unpaid leave automatically approved when I have no leave balance? | answerable | HR-008 | `ANSWERED` | ✅ |
| LQ019 | Does the policy provide maternity leave? | unanswerable | None | `ABSTAINED` | ✅ |
| LQ020 | How many paternity leave days can I take? | unanswerable | None | `ABSTAINED` | ✅ |
