"""Canonical disease names and aliases for PoultryGuardAI.

This keeps folder names Windows-safe while still accepting the display names
used in documents and UI text, such as "Salmonellosis/Pullorum".
"""

from __future__ import annotations

from typing import Dict


CANONICAL_DISEASES = [
    "Newcastle-Disease",
    "Avian-Influenza",
    "Infectious-Bursal-Disease",
    "Marek-Disease",
    "Fowl-Pox",
    "Infectious-Bronchitis",
    "Salmonellosis-Pullorum",
    "Fowl-Cholera",
    "Mycoplasmosis-CRD",
    "Infectious-Coryza",
    "Coccidiosis",
    "Healthy",
]


DISPLAY_LABELS: Dict[str, str] = {
    "Newcastle-Disease": "Newcastle disease",
    "Avian-Influenza": "Avian Influenza",
    "Infectious-Bursal-Disease": "Infectious Bursal Disease",
    "Marek-Disease": "Marek's Disease",
    "Fowl-Pox": "Fowl Pox",
    "Infectious-Bronchitis": "Infectious Bronchitis",
    "Salmonellosis-Pullorum": "Salmonellosis/Pullorum",
    "Fowl-Cholera": "Fowl Cholera",
    "Mycoplasmosis-CRD": "Mycoplasmosis (CRD)",
    "Infectious-Coryza": "Infectious Coryza",
    "Coccidiosis": "Coccidiosis",
    "Healthy": "Healthy",
}


ALIASES: Dict[str, str] = {
    "newcastle": "Newcastle-Disease",
    "newcastle disease": "Newcastle-Disease",
    "newcastle-disease": "Newcastle-Disease",
    "avian influenza": "Avian-Influenza",
    "bird flu": "Avian-Influenza",
    "avian-influenza": "Avian-Influenza",
    "infectious bursal disease": "Infectious-Bursal-Disease",
    "infectious-bursal-disease": "Infectious-Bursal-Disease",
    "ibd": "Infectious-Bursal-Disease",
    "gumboro": "Infectious-Bursal-Disease",
    "marek's disease": "Marek-Disease",
    "mareks disease": "Marek-Disease",
    "marek disease": "Marek-Disease",
    "marek-disease": "Marek-Disease",
    "fowl pox": "Fowl-Pox",
    "fowlpox": "Fowl-Pox",
    "fowl-pox": "Fowl-Pox",
    "infectious bronchitis": "Infectious-Bronchitis",
    "infectious-bronchitis": "Infectious-Bronchitis",
    "salmonellosis": "Salmonellosis-Pullorum",
    "salmonellosis pullorum": "Salmonellosis-Pullorum",
    "salmonellosis/pullorum": "Salmonellosis-Pullorum",
    "salmonellosis-pullorum": "Salmonellosis-Pullorum",
    "pullorum": "Salmonellosis-Pullorum",
    "salmonella": "Salmonellosis-Pullorum",
    "fowl cholera": "Fowl-Cholera",
    "fowl-cholera": "Fowl-Cholera",
    "mycoplasmosis": "Mycoplasmosis-CRD",
    "mycoplasmosis crd": "Mycoplasmosis-CRD",
    "mycoplasmosis/crd": "Mycoplasmosis-CRD",
    "mycoplasmosis-crd": "Mycoplasmosis-CRD",
    "mycoplasmosis (crd)": "Mycoplasmosis-CRD",
    "crd": "Mycoplasmosis-CRD",
    "chronic respiratory disease": "Mycoplasmosis-CRD",
    "infectious coryza": "Infectious-Coryza",
    "infectious-coryza": "Infectious-Coryza",
    "coccidiosis": "Coccidiosis",
    "healthy": "Healthy",
    "healty": "Healthy",
    "normal": "Healthy",
    "control": "Healthy",
}


def normalize_disease_name(name: str) -> str:
    """Return the canonical folder name for a disease label."""

    cleaned = (
        name.strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace(":", " ")
    )
    cleaned = " ".join(cleaned.split())
    return ALIASES.get(cleaned, name.strip())


def display_label(name: str) -> str:
    """Return the human-readable label for a canonical disease folder name."""

    return DISPLAY_LABELS.get(name, name)
