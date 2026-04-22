"""Training routes -- Community health worker training modules."""

from flask import Blueprint, render_template, request, jsonify
from ..services import llm_client, prompt_templates

bp = Blueprint("training", __name__, url_prefix="/training")


@bp.route("/")
def modules():
    return render_template("training/modules.html")


@bp.route("/chat", methods=["POST"])
def training_chat():
    """Interactive training conversation with the AI tutor."""
    data = request.get_json()
    messages = data.get("messages", [])
    module = data.get("module", "general")

    # Prepend system prompt
    full_messages = [
        {"role": "system", "content": prompt_templates.TRAINING_SYSTEM},
    ] + messages

    response = llm_client.query(full_messages)
    return jsonify({"response": response})
