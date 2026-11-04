"""
Neural Network Intent Classifier for PolicyPilot
Owner: Rahul (Intent Classifier & Evaluation)

Implements:
1. Multi-class dataset covering 6 core policy intents + unknown/out-of-scope (140 samples).
2. Baseline classifier (Logistic Regression).
3. Neural Network MLP Classifier (sklearn.neural_network.MLPClassifier).
4. Evaluation with per-class F1, classification report, and confusion matrix.
"""

import os
import json
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split


INTENT_DATA_RAW = {
    "leave": [
        "How early should planned leave be submitted?",
        "Submit vacation request 3 days in advance",
        "How to apply for emergency leave?",
        "Report emergency absence to manager as soon as practical",
        "Attendance record correction procedure within 2 days",
        "Who do I contact for attendance corrections?",
        "Can I take annual leave next week?",
        "Planned leave approval depends on team coverage",
        "Sick leave reporting guidelines",
        "Procedure for notifying manager of unplanned absence",
        "How many days before must I request vacation time off?",
        "I need to correct my attendance sheet from yesterday",
        "Who approves leave requests for team members?",
        "Emergency leave protocol when unable to contact supervisor",
        "Planned time off request lead time",
        "Correcting timesheet and attendance discrepancies",
        "Manager review for planned leave applications",
        "Taking leave during project deployment",
        "Submitting time off notice 3 days early",
        "Attendance coordinator reporting timeline",
    ],
    "remote_work": [
        "What are the rules for working from home?",
        "Agree working hours and availability with manager",
        "Can I work remotely full time?",
        "Use company-approved devices for work",
        "Secure network access required for remote work",
        "Confidential files must not be copied to personal storage",
        "Requests for remote work exceptions reviewed by manager",
        "Can I use my personal laptop for remote tasks?",
        "Do I need manager approval to work from another location?",
        "Guidelines for telecommuting and working hours",
        "Can I copy sensitive files to my USB drive while working from home?",
        "Connecting through secure VPN or company network",
        "Remote work schedule agreement with manager",
        "Documenting remote work exception requests",
        "Personal device policy during remote employment",
        "Working from home core hours agreement",
        "Is personal cloud storage allowed for work files?",
        "Exception process for full time remote working",
        "Hardware requirements for remote team members",
        "Policy regarding copying company data to private hard drive",
    ],
    "credentials": [
        "What should I do if an API key was exposed?",
        "Use multi-factor authentication wherever available",
        "Never share passwords recovery codes or API keys",
        "Store secrets in approved secrets manager or environment variables",
        "Do not commit credentials or passwords to Git",
        "Report suspected credential exposure to IT contact",
        "Rotate affected credentials according to incident response",
        "MFA requirement for corporate accounts",
        "How to handle a leaked token or secret key?",
        "Where should environment secrets be stored?",
        "I accidentally pushed my API key to GitHub repo",
        "Who do I alert when a password is compromised?",
        "Rotating database credentials and access tokens",
        "Sharing system passwords with teammates is prohibited",
        "How often should credentials be rotated?",
        "Secret manager tools approved for developer credentials",
        "Recovery code storage and security policy",
        "Reporting exposed tokens to IT security officer",
        "Best practices for Git commit credential scanning",
        "Two factor authentication setup instructions",
    ],
    "device_security": [
        "What should I do if I lose a device?",
        "Lock devices when left unattended",
        "Install updates through approved processes",
        "Use approved storage locations for company files",
        "Do not upload confidential information to public AI tools",
        "Report lost devices or suspected data exposure promptly",
        "Stolen laptop notification procedure",
        "Is screen lock required when stepping away from desk?",
        "Can I use public AI tools like ChatGPT with company code?",
        "Operating system patch and update guidelines",
        "Leaving company laptop unattended in public areas",
        "Approved enterprise cloud storage for project documents",
        "Lost mobile phone with company email access",
        "Security update installation requirements",
        "Pasting internal customer data into online AI chatbots",
        "Automatic screen lock timeout configuration",
        "Reporting misplaced hardware to security desk",
        "Bypassing company software update mechanisms",
        "Physical laptop security and cable locks",
        "Prohibition on third-party generative AI with sensitive data",
    ],
    "incidents": [
        "What details should be included in an incident report?",
        "Report time observed affected system and business impact",
        "Avoid guessing root cause before evidence is available",
        "Preserve relevant logs while respecting access controls",
        "Escalate urgent interruptions to designated support lead",
        "Document corrective and preventive actions after resolution",
        "System outage reporting procedure",
        "Critical production service downtime escalation",
        "Should I speculate on cause during an IT outage?",
        "Incident post-mortem and preventive measures",
        "Log preservation guidelines during security investigations",
        "Contacting the support lead for urgent system crash",
        "Documenting actions already taken in incident ticket",
        "Root cause analysis evidence collection",
        "Incident severity levels and notification tree",
        "Post incident review and corrective action documentation",
        "Production outage timeline and impact reporting",
        "Who to notify for critical infrastructure failures",
        "Preserving audit logs for incident post-mortem",
        "Steps to take immediately upon discovering an IT incident",
    ],
    "expenses": [
        "Can I purchase equipment before approval?",
        "Requests should include business purpose and estimated amount",
        "Approval must be obtained before purchase commitment is made",
        "Reimbursement is subject to review of complete documentation",
        "Cost center and supporting documents required for expenses",
        "Can I buy hardware and submit receipts later?",
        "Who approves purchase orders and invoices?",
        "Submitting expense claims for business travel or equipment",
        "Documentation needed for corporate reimbursement",
        "Unapproved purchase commitments are not permitted",
        "Invoice submission process with cost center coding",
        "Receipt verification and reimbursement approval",
        "Buying software tools without prior manager sign-off",
        "Estimated budget approval for department purchases",
        "Reviewing supporting receipts for reimbursement",
        "Routing expense queries to human approvers",
        "Procurement policy before signing vendor contracts",
        "Required attachments for expense claim submission",
        "Manager authorization for department expense requests",
        "Expense limits and documentation standards",
    ],
    "unknown": [
        "What is the company maternity leave entitlement?",
        "What is the annual reimbursement cap?",
        "What is the exact legal notice period for resignation?",
        "How many weeks of paternity leave do fathers receive?",
        "What are the stock option vesting schedules?",
        "Can I bring pets to the office on weekends?",
        "What is the free lunch cafeteria budget?",
        "Who is the chief executive officer of the company?",
        "What is the weather in Bangalore today?",
        "How do I claim flight ticket business class upgrades?",
        "What health insurance plans cover dental treatment?",
        "Severance package policy for contract staff",
        "Can I trade company stock during blackout periods?",
        "Company holiday calendar for next year",
        "Parking spot reservation policy in office garage",
        "Referral bonus payout schedule for hiring friends",
        "Pension fund matching contribution percentage",
        "Gym membership discount program details",
        "Office dress code guidelines on casual Fridays",
        "Relocation assistance stipend calculation",
    ],
}

INTENT_TO_POLICY = {
    "leave": "HR-001",
    "remote_work": "HR-002",
    "credentials": "IT-001",
    "device_security": "IT-002",
    "incidents": "IT-003",
    "expenses": "HR-003",
    "unknown": None,
}


def build_dataset() -> Tuple[List[str], List[str]]:
    texts = []
    labels = []
    for intent, items in INTENT_DATA_RAW.items():
        for t in items:
            texts.append(t)
            labels.append(intent)
    return texts, labels


class IntentClassifierService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.baseline_model = LogisticRegression(C=5.0, max_iter=1000, random_state=42)
        self.mlp_model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="lbfgs",
            max_iter=1000,
            random_state=42,
        )
        self.classes_: List[str] = []
        self.evaluation_results: Dict[str, Any] = {}
        self.is_trained = False

    def train_and_evaluate(self, test_size: float = 0.25) -> Dict[str, Any]:
        texts, labels = build_dataset()

        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )

        X_train = self.vectorizer.fit_transform(X_train_raw)
        X_test = self.vectorizer.transform(X_test_raw)

        # 1. Baseline Model
        self.baseline_model.fit(X_train, y_train)
        y_pred_baseline = self.baseline_model.predict(X_test)
        f1_baseline = f1_score(y_test, y_pred_baseline, average="weighted")
        baseline_report = classification_report(y_test, y_pred_baseline, output_dict=True, zero_division=0)

        # 2. Neural Network (MLP) Model
        self.mlp_model.fit(X_train, y_train)
        y_pred_mlp = self.mlp_model.predict(X_test)
        f1_mlp = f1_score(y_test, y_pred_mlp, average="weighted")
        mlp_report = classification_report(y_test, y_pred_mlp, output_dict=True, zero_division=0)
        mlp_matrix = confusion_matrix(y_test, y_pred_mlp, labels=self.mlp_model.classes_).tolist()

        self.classes_ = list(self.mlp_model.classes_)
        self.is_trained = True

        self.evaluation_results = {
            "total_samples": len(texts),
            "test_sample_count": len(y_test),
            "classes": self.classes_,
            "baseline": {
                "model_name": "Logistic Regression Baseline",
                "weighted_f1": round(f1_baseline, 4),
                "classification_report": baseline_report,
            },
            "mlp_neural_network": {
                "model_name": "Multi-Layer Perceptron (ANN)",
                "hidden_layers": [64, 32],
                "weighted_f1": round(f1_mlp, 4),
                "classification_report": mlp_report,
                "confusion_matrix": mlp_matrix,
            },
        }

        # Train on full data for production inference
        X_full = self.vectorizer.fit_transform(texts)
        self.mlp_model.fit(X_full, labels)

        return self.evaluation_results

    def predict(self, text: str) -> Dict[str, Any]:
        """Classify user query intent using the trained MLP neural network."""
        if not self.is_trained:
            self.train_and_evaluate()

        vec = self.vectorizer.transform([text])
        probs = self.mlp_model.predict_proba(vec)[0]
        max_idx = int(np.argmax(probs))
        predicted_class = self.classes_[max_idx]
        confidence = float(probs[max_idx])

        # If highest confidence is low, categorize as unknown
        if confidence < 0.20:
            predicted_class = "unknown"

        expected_policy_id = INTENT_TO_POLICY.get(predicted_class)

        return {
            "intent": predicted_class,
            "confidence": round(confidence, 4),
            "mapped_policy_id": expected_policy_id,
            "is_out_of_scope": (predicted_class == "unknown"),
        }


if __name__ == "__main__":
    service = IntentClassifierService()
    results = service.train_and_evaluate()
    print("Total Samples:", results["total_samples"])
    print("Baseline Weighted F1:", results["baseline"]["weighted_f1"])
    print("Neural Net (MLP) Weighted F1:", results["mlp_neural_network"]["weighted_f1"])
