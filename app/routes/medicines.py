"""Medicines routes -- Essential medicines search and dosing calculator."""

from flask import Blueprint, render_template, request, jsonify
from ..services import dosing_engine, llm_client, prompt_templates

bp = Blueprint("medicines", __name__, url_prefix="/medicines")


@bp.route("/")
def search_page():
    return render_template("medicines/search.html")


@bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    if not query or len(query) < 2:
        return jsonify({"results": []})
    results = dosing_engine.search_medicine(query)
    return jsonify({"results": results})


@bp.route("/dose", methods=["POST"])
def calculate():
    data = request.get_json()
    medicine_id = data.get("medicine_id")
    formulation = data.get("formulation")
    weight_kg = data.get("weight_kg")
    age_years = data.get("age_years")

    if not medicine_id or not formulation:
        return jsonify({"error": "medicine_id and formulation are required"}), 400

    # Deterministic dose calculation
    dose_result = dosing_engine.calculate_dose(
        medicine_id=medicine_id,
        formulation=formulation,
        weight_kg=float(weight_kg) if weight_kg else None,
        age_years=float(age_years) if age_years else None,
    )

    if "error" in dose_result:
        return jsonify(dose_result), 400

    # LLM explains the dose in plain language
    explanation = llm_client.query([
        {"role": "system", "content": prompt_templates.DOSING_SYSTEM},
        {"role": "user", "content": (
            f"Medicine: {dose_result['medicine']}\n"
            f"Formulation: {dose_result['formulation']}\n"
            f"Calculated dose: {dose_result['dose']}\n"
            f"Frequency: {dose_result['frequency']}\n"
            f"Duration: {dose_result['duration']}\n"
            f"Warnings: {dose_result['warnings']}\n"
            "Explain how to give this medication in simple, clear language."
        )},
    ])

    dose_result["explanation"] = explanation
    return jsonify(dose_result)
