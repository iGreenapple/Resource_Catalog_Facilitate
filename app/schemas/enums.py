"""Centrální seznam povolených draft enum hodnot pro MVP validaci."""

RESOURCE_TYPE_VALUES = {
    "Blueprint",
    "Guide",
    "Toolkit",
    "Policy",
    "Case study",
    "Training",
    "Dataset",
    "Platform",
}

AUDIENCE_VALUES = {
    "DMO",
    "SME",
    "Public authority",
    "Data/tech provider",
}

TASK_VALUES = {"T1", "T2", "T3", "T4", "T5"}

STAGE_VALUES = {"Explore", "Prepare", "Pilot", "Scale"}

PERSONA_VALUES = {"DMO", "SME", "Public authority", "Tech provider"}

EFFORT_LEVEL_VALUES = {"quick win", "medium", "deep dive"}

PRACTICALITY_LEVEL_VALUES = {
    "Background",
    "Background (with strong Implementation pointers via links)",
    "Implementation",
    "Mixed",
}

ACCESS_CONDITIONS_VALUES = {"Open", "Registration", "Paid", "Restricted"}

REVIEW_STATUS_VALUES = {"Proposed", "Approved", "Needs update", "Archived"}
