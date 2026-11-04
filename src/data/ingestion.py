"""
Data Ingestion Module for PolicyPilot
Owner: Ijas (Data & Text Pipeline)

Loads raw policy files, extracts policy IDs and titles, validates schemas,
normalizes text, and provides structured document models.
"""

import os
import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class PolicyDocument(BaseModel):
    policy_id: str = Field(..., description="Unique policy identifier (e.g., HR-001, IT-001)")
    title: str = Field(..., description="Official title of the policy")
    raw_content: str = Field(..., description="Complete original text of the policy")
    normalized_content: str = Field(..., description="Normalized clean content without metadata headers")
    source_file: str = Field(..., description="File name from which policy was ingested")
    category: str = Field(..., description="High-level category: HR or IT")


def parse_policy_file(file_path: str) -> Optional[PolicyDocument]:
    """Parse a single policy text file into a PolicyDocument model."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return None

    policy_id = ""
    title = ""
    body_lines = []

    for line in lines:
        if line.lower().startswith("policy id:"):
            policy_id = line.split(":", 1)[1].strip()
        elif line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
        else:
            body_lines.append(line)

    body_text = " ".join(body_lines)
    # Clean up multi-space
    normalized_text = re.sub(r"\s+", " ", body_text).strip()

    category = "HR" if policy_id.startswith("HR") else "IT"

    return PolicyDocument(
        policy_id=policy_id,
        title=title,
        raw_content=content,
        normalized_content=normalized_text,
        source_file=os.path.basename(file_path),
        category=category,
    )


def load_all_policies(data_dir: str) -> List[PolicyDocument]:
    """Load and validate all raw policy documents in a directory."""
    policies = []
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    files = sorted([f for f in os.listdir(data_dir) if f.endswith(".txt") and f != "README.txt"])
    for f in files:
        full_path = os.path.join(data_dir, f)
        doc = parse_policy_file(full_path)
        if doc:
            policies.append(doc)

    return policies


if __name__ == "__main__":
    default_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    docs = load_all_policies(os.path.abspath(default_dir))
    print(f"Loaded {len(docs)} policies successfully:")
    for d in docs:
        print(f" - [{d.policy_id}] {d.title} ({d.category}) from {d.source_file}")
