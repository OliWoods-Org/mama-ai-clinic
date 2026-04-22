"""IMNCI Triage Engine -- deterministic decision trees from WHO guidelines.

This is the safety-critical core. NO LLM involvement in classification.
Every classification maps exactly to the WHO IMNCI chart booklet.
"""

import json
import os
from flask import current_app

_imnci_data = None


def _load_data():
    global _imnci_data
    if _imnci_data is None:
        kb_dir = current_app.config["KNOWLEDGE_DIR"]
        chart_path = os.path.join(kb_dir, "imnci", "chart_booklet.json")
        with open(chart_path) as f:
            _imnci_data = json.load(f)
    return _imnci_data


# --- General Danger Signs (any age) ---
# If ANY of these are present: classify RED, refer urgently.

GENERAL_DANGER_SIGNS = [
    "not_able_to_drink_or_breastfeed",
    "vomits_everything",
    "convulsions",
    "lethargic_or_unconscious",
]


def check_danger_signs(signs_present: list[str]) -> dict:
    """Check for general danger signs.

    Args:
        signs_present: List of danger sign codes from GENERAL_DANGER_SIGNS.

    Returns:
        {"has_danger_signs": bool, "signs": [...], "action": str}
    """
    found = [s for s in signs_present if s in GENERAL_DANGER_SIGNS]
    if found:
        return {
            "has_danger_signs": True,
            "signs": found,
            "classification": "RED",
            "action": "REFER URGENTLY to hospital. Give pre-referral treatment.",
        }
    return {"has_danger_signs": False, "signs": [], "classification": None, "action": None}


# --- Diarrhea Assessment (2 months - 5 years) ---

def classify_diarrhea(
    duration_days: int,
    blood_in_stool: bool,
    sunken_eyes: bool,
    skin_pinch: str,  # "instant", "slow", "very_slow"
    drinking: str,  # "normal", "eager", "not_able"
    restless_irritable: bool,
    lethargic: bool,
) -> dict:
    """Classify diarrhea per IMNCI guidelines.

    Returns classification dict with severity, color, and treatment actions.
    """
    # Severe dehydration (RED) -- 2 or more of these signs
    severe_signs = []
    if lethargic:
        severe_signs.append("lethargic_or_unconscious")
    if sunken_eyes:
        severe_signs.append("sunken_eyes")
    if drinking == "not_able":
        severe_signs.append("not_able_to_drink")
    if skin_pinch == "very_slow":
        severe_signs.append("skin_pinch_very_slow")

    if len(severe_signs) >= 2:
        return {
            "classification": "SEVERE DEHYDRATION",
            "color": "RED",
            "signs": severe_signs,
            "actions": [
                "If no other severe classification: give IV fluids (Plan C)",
                "If other severe classification present: REFER URGENTLY with mother giving frequent sips of ORS",
                "Advise mother to continue breastfeeding",
            ],
        }

    # Some dehydration (YELLOW) -- 2 or more of these signs
    some_signs = []
    if restless_irritable:
        some_signs.append("restless_irritable")
    if sunken_eyes:
        some_signs.append("sunken_eyes")
    if drinking == "eager":
        some_signs.append("drinks_eagerly_thirsty")
    if skin_pinch == "slow":
        some_signs.append("skin_pinch_slow")

    if len(some_signs) >= 2:
        return {
            "classification": "SOME DEHYDRATION",
            "color": "YELLOW",
            "signs": some_signs,
            "actions": [
                "Give ORS (Plan B): treat in facility for 4 hours",
                "Advise mother to continue breastfeeding",
                "If also classified for another illness: reassess and treat accordingly",
                "Follow up in 5 days if not improving",
            ],
        }

    # No dehydration (GREEN)
    result = {
        "classification": "NO DEHYDRATION",
        "color": "GREEN",
        "signs": [],
        "actions": [
            "Give ORS to take home (Plan A)",
            "Advise mother when to return immediately",
            "Follow up in 5 days if not improving",
        ],
    }

    # Persistent diarrhea overlay
    if duration_days >= 14:
        if any(s in severe_signs + some_signs for s in ["sunken_eyes", "skin_pinch_very_slow", "skin_pinch_slow"]):
            result["classification"] = "SEVERE PERSISTENT DIARRHEA"
            result["color"] = "RED"
            result["actions"] = ["REFER to hospital for management"]
        else:
            result["classification"] = "PERSISTENT DIARRHEA"
            result["color"] = "YELLOW"
            result["actions"].insert(0, "Advise on feeding for persistent diarrhea")

    # Dysentery overlay
    if blood_in_stool:
        result["classification"] = "DYSENTERY"
        result["color"] = "YELLOW"
        result["actions"] = [
            "Treat with oral antibiotic recommended for Shigella",
            "Follow up in 2 days",
        ]

    return result


# --- Cough/Breathing Assessment (2 months - 5 years) ---

# Fast breathing thresholds per IMNCI
FAST_BREATHING_THRESHOLDS = {
    "2_months_to_12_months": 50,  # >= 50 breaths/min
    "12_months_to_5_years": 40,  # >= 40 breaths/min
}


def classify_cough(
    age_group: str,  # "2_months_to_12_months" or "12_months_to_5_years"
    cough_days: int,
    breathing_rate: int,
    chest_indrawing: bool,
    stridor_at_rest: bool,
    has_danger_signs: bool,
) -> dict:
    """Classify cough/difficulty breathing per IMNCI."""

    # Severe pneumonia (RED)
    if has_danger_signs or stridor_at_rest:
        return {
            "classification": "SEVERE PNEUMONIA OR VERY SEVERE DISEASE",
            "color": "RED",
            "signs": ["danger_sign_present" if has_danger_signs else "stridor_at_rest"],
            "actions": [
                "Give first dose of antibiotic",
                "REFER URGENTLY to hospital",
            ],
        }

    # Pneumonia (YELLOW) -- fast breathing or chest indrawing
    threshold = FAST_BREATHING_THRESHOLDS.get(age_group, 40)
    if breathing_rate >= threshold or chest_indrawing:
        signs = []
        if breathing_rate >= threshold:
            signs.append(f"fast_breathing_{breathing_rate}_per_min")
        if chest_indrawing:
            signs.append("chest_indrawing")
        return {
            "classification": "PNEUMONIA",
            "color": "YELLOW",
            "signs": signs,
            "actions": [
                "Give oral antibiotic for 5 days",
                "Soothe the throat with safe remedy",
                "Advise mother when to return immediately",
                "Follow up in 2 days",
            ],
        }

    # No pneumonia (GREEN)
    result = {
        "classification": "COUGH OR COLD",
        "color": "GREEN",
        "signs": [],
        "actions": [
            "Soothe the throat with safe remedy",
            "Advise mother when to return immediately",
            "Follow up in 5 days if not improving",
        ],
    }

    if cough_days >= 14:
        result["classification"] = "CHRONIC COUGH"
        result["color"] = "YELLOW"
        result["actions"] = ["Refer for TB assessment and further evaluation"]

    return result


# --- Fever Assessment (2 months - 5 years) ---

def classify_fever(
    temperature_c: float,
    fever_days: int,
    stiff_neck: bool,
    malaria_risk: bool,
    rdt_result: str | None,  # "positive", "negative", None
    measles_signs: bool,
    has_danger_signs: bool,
) -> dict:
    """Classify fever per IMNCI guidelines."""

    if has_danger_signs or stiff_neck:
        return {
            "classification": "VERY SEVERE FEBRILE DISEASE",
            "color": "RED",
            "signs": ["stiff_neck" if stiff_neck else "general_danger_sign"],
            "actions": [
                "Give first dose of antibiotic",
                "Give first dose of artesunate (if malaria risk area)",
                "Treat to prevent low blood sugar",
                "REFER URGENTLY to hospital",
            ],
        }

    if malaria_risk and rdt_result == "positive":
        classification = "MALARIA"
        color = "YELLOW"
        actions = [
            "Give first-line antimalarial (ACT) for 3 days",
            "Give paracetamol for fever >= 38.5C",
            "Follow up in 2 days if fever persists",
            "Advise mother when to return immediately",
        ]
        if fever_days >= 7:
            return {
                "classification": "MALARIA WITH PROLONGED FEVER",
                "color": "YELLOW",
                "signs": ["rdt_positive", "fever_7_plus_days"],
                "actions": actions + ["Refer for further evaluation"],
            }
        return {
            "classification": classification,
            "color": color,
            "signs": ["rdt_positive"],
            "actions": actions,
        }

    if fever_days >= 7:
        return {
            "classification": "FEVER - PROLONGED",
            "color": "YELLOW",
            "signs": [f"fever_{fever_days}_days"],
            "actions": ["Refer for further evaluation"],
        }

    return {
        "classification": "FEVER - LIKELY VIRAL",
        "color": "GREEN",
        "signs": [],
        "actions": [
            "Give paracetamol for fever >= 38.5C",
            "Advise mother on home care",
            "Advise mother when to return immediately",
            "Follow up in 2 days if fever persists",
        ],
    }
