"""Essential Medicines Dosing Engine.

All calculations are deterministic from WHO EML dosing tables.
The LLM is NEVER used for dose calculation -- only for explanation.
"""

import json
import os
from flask import current_app

_dosing_data = None
_medicines_data = None


def _load_data():
    global _dosing_data, _medicines_data
    if _dosing_data is None:
        kb_dir = current_app.config["KNOWLEDGE_DIR"]
        dosing_path = os.path.join(kb_dir, "essential_medicines", "dosing_tables.json")
        eml_path = os.path.join(kb_dir, "essential_medicines", "eml_24.json")
        with open(dosing_path) as f:
            _dosing_data = json.load(f)
        with open(eml_path) as f:
            _medicines_data = json.load(f)
    return _dosing_data, _medicines_data


def search_medicine(query: str) -> list[dict]:
    """Fuzzy search for a medicine by name.

    Returns list of matching medicines with basic info.
    """
    _, medicines = _load_data()
    query_lower = query.lower()
    results = []
    for med in medicines.get("medicines", []):
        name = med.get("name", "").lower()
        aliases = [a.lower() for a in med.get("aliases", [])]
        if query_lower in name or any(query_lower in a for a in aliases):
            results.append({
                "id": med.get("id"),
                "name": med.get("name"),
                "category": med.get("category"),
                "formulations": med.get("formulations", []),
            })
    return results


def calculate_dose(
    medicine_id: str,
    formulation: str,
    weight_kg: float | None = None,
    age_years: float | None = None,
) -> dict:
    """Calculate dose from lookup tables.

    Args:
        medicine_id: Medicine identifier from search results.
        formulation: Formulation type (e.g., "tablet_250mg", "syrup_125mg_5ml").
        weight_kg: Patient weight in kg. Preferred for dosing.
        age_years: Patient age in years. Used if weight not available.

    Returns:
        {"medicine": str, "formulation": str, "dose": str, "frequency": str,
         "duration": str, "warnings": [str], "notes": str}
    """
    dosing_data, medicines = _load_data()

    # Find the medicine
    med = None
    for m in medicines.get("medicines", []):
        if m.get("id") == medicine_id:
            med = m
            break

    if med is None:
        return {"error": f"Medicine '{medicine_id}' not found"}

    # Find dosing table entry
    dosing_entry = dosing_data.get(medicine_id, {}).get(formulation)
    if dosing_entry is None:
        return {"error": f"No dosing table for {medicine_id} / {formulation}"}

    # Weight-based dosing (preferred)
    if weight_kg is not None:
        dose_info = _weight_based_dose(dosing_entry, weight_kg)
    elif age_years is not None:
        dose_info = _age_based_dose(dosing_entry, age_years)
    else:
        return {"error": "Either weight_kg or age_years is required"}

    return {
        "medicine": med.get("name"),
        "formulation": formulation,
        "dose": dose_info.get("dose"),
        "frequency": dose_info.get("frequency"),
        "duration": dose_info.get("duration"),
        "max_dose": dose_info.get("max_dose"),
        "warnings": med.get("warnings", []),
        "contraindications": med.get("contraindications", []),
        "notes": dose_info.get("notes", ""),
    }


def _weight_based_dose(entry: dict, weight_kg: float) -> dict:
    """Look up dose by weight band from dosing table."""
    bands = entry.get("weight_bands", [])
    for band in bands:
        min_kg = band.get("min_kg", 0)
        max_kg = band.get("max_kg", 999)
        if min_kg <= weight_kg < max_kg:
            return {
                "dose": band.get("dose"),
                "frequency": entry.get("frequency"),
                "duration": entry.get("duration"),
                "max_dose": entry.get("max_dose"),
                "notes": band.get("notes", ""),
            }

    return {
        "dose": "OUTSIDE DOSING TABLE RANGE - refer to prescriber",
        "frequency": entry.get("frequency"),
        "duration": entry.get("duration"),
    }


def _age_based_dose(entry: dict, age_years: float) -> dict:
    """Look up dose by age band (fallback when weight unavailable)."""
    bands = entry.get("age_bands", [])
    for band in bands:
        min_age = band.get("min_years", 0)
        max_age = band.get("max_years", 999)
        if min_age <= age_years < max_age:
            return {
                "dose": band.get("dose"),
                "frequency": entry.get("frequency"),
                "duration": entry.get("duration"),
                "max_dose": entry.get("max_dose"),
                "notes": band.get("notes", "Weight-based dosing preferred when possible."),
            }

    return {
        "dose": "OUTSIDE DOSING TABLE RANGE - refer to prescriber",
        "frequency": entry.get("frequency"),
        "duration": entry.get("duration"),
    }
