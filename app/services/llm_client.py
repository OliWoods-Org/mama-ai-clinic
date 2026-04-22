"""Client for the local llama-server REST API (OpenAI-compatible)."""

import requests
from flask import current_app


def query(messages, max_tokens=None, temperature=None, stream=False):
    """Send a chat completion request to the local llama-server.

    Args:
        messages: List of {"role": str, "content": str} dicts.
        max_tokens: Override max tokens (default from config).
        temperature: Override temperature (default from config).
        stream: If True, return a generator of streamed chunks.

    Returns:
        The assistant's response text, or a generator if streaming.
    """
    url = f"{current_app.config['LLAMA_API_URL']}/v1/chat/completions"
    payload = {
        "model": "local",
        "messages": messages,
        "max_tokens": max_tokens or current_app.config["MAX_TOKENS"],
        "temperature": temperature or current_app.config["TEMPERATURE"],
        "top_p": current_app.config["TOP_P"],
        "stream": stream,
    }

    if stream:
        return _stream_response(url, payload)

    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _stream_response(url, payload):
    """Generator that yields text chunks from a streaming response."""
    with requests.post(url, json=payload, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break
            import json
            chunk = json.loads(data_str)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content


def health_check():
    """Check if llama-server is responding."""
    try:
        url = f"{current_app.config['LLAMA_API_URL']}/health"
        resp = requests.get(url, timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False
