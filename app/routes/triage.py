"""Triage routes -- WHO IMNCI symptom assessment."""

from flask import Blueprint, render_template, request, jsonify
from ..services import triage_engine, llm_client, prompt_templates

bp = Blueprint("triage", __name__, url_prefix="/triage")


@bp.route("/")
def start():
    return render_template("triage/start.html")


@bp.route("/assess", methods=["POST"])
def assess():
    data = request.get_json()
    age_group = data.get("age_group")
    symptoms = data.get("symptoms", {})

    # Step 1: Always check danger signs first (deterministic)
    danger_signs = data.get("danger_signs", [])
    danger_result = triage_engine.check_danger_signs(danger_signs)

    if danger_result["has_danger_signs"]:
        # Generate plain-language explanation via LLM
        explanation = llm_client.query([
            {"role": "system", "content": prompt_templates.TRIAGE_SYSTEM},
            {"role": "user", "content": (
                f"The patient has these general danger signs: {', '.join(danger_result['signs'])}. "
                "Explain why this requires urgent referral, in simple language for a community health worker."
            )},
        ])
        return jsonify({
            "classification": danger_result,
            "explanation": explanation,
        })

    # Step 2: Assess by complaint type (deterministic)
    complaint = data.get("chief_complaint")
    classification = None

    if complaint == "diarrhea":
        classification = triage_engine.classify_diarrhea(
            duration_days=symptoms.get("duration_days", 1),
            blood_in_stool=symptoms.get("blood_in_stool", False),
            sunken_eyes=symptoms.get("sunken_eyes", False),
            skin_pinch=symptoms.get("skin_pinch", "instant"),
            drinking=symptoms.get("drinking", "normal"),
            restless_irritable=symptoms.get("restless_irritable", False),
            lethargic=symptoms.get("lethargic", False),
        )
    elif complaint == "cough":
        classification = triage_engine.classify_cough(
            age_group=age_group,
            cough_days=symptoms.get("duration_days", 1),
            breathing_rate=symptoms.get("breathing_rate", 30),
            chest_indrawing=symptoms.get("chest_indrawing", False),
            stridor_at_rest=symptoms.get("stridor_at_rest", False),
            has_danger_signs=False,
        )
    elif complaint == "fever":
        classification = triage_engine.classify_fever(
            temperature_c=symptoms.get("temperature_c", 37.0),
            fever_days=symptoms.get("duration_days", 1),
            stiff_neck=symptoms.get("stiff_neck", False),
            malaria_risk=symptoms.get("malaria_risk", False),
            rdt_result=symptoms.get("rdt_result"),
            measles_signs=symptoms.get("measles_signs", False),
            has_danger_signs=False,
        )

    if classification is None:
        return jsonify({"error": "Unsupported complaint type"}), 400

    # Step 3: LLM explains the classification in plain language
    explanation = llm_client.query([
        {"role": "system", "content": prompt_templates.TRIAGE_SYSTEM},
        {"role": "user", "content": (
            f"IMNCI classification result: {classification['classification']} ({classification['color']}). "
            f"Signs found: {classification.get('signs', [])}. "
            f"Recommended actions: {classification.get('actions', [])}. "
            "Explain this classification and the next steps in simple language "
            "for a community health worker."
        )},
    ])

    return jsonify({
        "classification": classification,
        "explanation": explanation,
    })


@bp.route("/interpret", methods=["POST"])
def interpret_symptoms():
    """Use LLM to interpret free-text symptom description into structured input."""
    data = request.get_json()
    description = data.get("description", "")

    result = llm_client.query([
        {"role": "system", "content": prompt_templates.TRIAGE_INTERPRET},
        {"role": "user", "content": description},
    ])

    return jsonify({"interpretation": result})
