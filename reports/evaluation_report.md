# PolicyPilot: RAG Evaluation Report

**Total Queries Evaluated:** 20
- Answerable: 13
- Unanswerable: 7

## 1. Retrieval Performance (Mano)

- **Mean Reciprocal Rank (MRR):** 92.3%
- **Recall@1:** 92.3%
- **Recall@3:** 92.3%

## 2. Abstention Performance (Rohith & Rahul)

- **Abstention Precision:** 100.0%
- **Abstention Recall:** 100.0%
- **Abstention F1 Score:** 100.0%

## 3. Citation & Overall Accuracy

- **Citation Accuracy:** 92.3%
- **Overall System Accuracy:** 95.0%

## 4. Query-by-Query Evaluation Breakdown

| # | Question | Expected Type | Expected Policy | Actual Status | Intent | Citation Match |
|---|---|---|---|---|---|---|
| 1 | How early should planned leave be submitted? | answerable | HR-001 | `ANSWERED` | `leave` | ✅ |
| 2 | What should I do if I suspect an API key was exposed? | answerable | IT-001 | `ANSWERED` | `credentials` | ✅ |
| 3 | Can I copy confidential files to personal storage while working remotely? | answerable | HR-002 | `ANSWERED` | `remote_work` | ✅ |
| 4 | What details should be included in an incident report? | answerable | IT-003 | `ANSWERED` | `incidents` | ✅ |
| 5 | What is the company's maternity leave entitlement? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 6 | What is the annual reimbursement cap? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 7 | What should I do if I lose a device? | answerable | IT-002 | `ANSWERED` | `device_security` | ✅ |
| 8 | Can I purchase equipment before approval? | answerable | HR-003 | `ANSWERED` | `expenses` | ✅ |
| 9 | What is the exact legal notice period for resignation? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 10 | Should I guess the cause of an IT incident before evidence is available? | answerable | IT-003 | `ANSWERED` | `incidents` | ✅ |
| 11 | How many days notice do I need for taking planned vacation days? | answerable | HR-001 | `ANSWERED` | `leave` | ✅ |
| 12 | Can I store database secrets directly in Git repository code? | answerable | IT-001 | `ANSWERED` | `credentials` | ✅ |
| 13 | Are personal hard drives allowed for backing up work files? | answerable | HR-002 | `ANSWERED` | `remote_work` | ✅ |
| 14 | Is it okay to leave my laptop unlocked while getting coffee? | answerable | IT-002 | `ANSWERED` | `leave` | ❌ |
| 15 | Who should be alerted when an urgent IT outage occurs? | answerable | IT-003 | `ANSWERED` | `incidents` | ✅ |
| 16 | What items must be included in a purchase reimbursement request? | answerable | HR-003 | `ANSWERED` | `expenses` | ✅ |
| 17 | What is the policy regarding paternity leave for new fathers? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 18 | How much gym membership reimbursement can I claim each month? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 19 | Can I trade company stock during quarterly blackout periods? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
| 20 | What health insurance plans are available for dependents? | unanswerable | None | `ABSTAINED` | `unknown` | ✅ |
