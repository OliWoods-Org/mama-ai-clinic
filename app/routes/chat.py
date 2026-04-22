"""Chat routes -- General medical Q&A."""

from flask import Blueprint, render_template, request, jsonify, Response
from ..services import llm_client, prompt_templates

bp = Blueprint("chat", __name__, url_prefix="/chat")


@bp.route("/")
def chat_page():
    return render_template("chat.html")


@bp.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    messages = data.get("messages", [])

    full_messages = [
        {"role": "system", "content": prompt_templates.CHAT_SYSTEM},
    ] + messages

    if data.get("stream"):
        def generate():
            for chunk in llm_client.query(full_messages, stream=True):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        return Response(generate(), mimetype="text/event-stream")

    response = llm_client.query(full_messages)
    return jsonify({"response": response})
