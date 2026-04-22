"""Application configuration for Pi AI Clinic."""

import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INFERENCE_CONFIG = os.path.join(os.path.dirname(BASE_DIR), "inference", "config.yaml")


def load_inference_config():
    if os.path.exists(INFERENCE_CONFIG):
        with open(INFERENCE_CONFIG) as f:
            return yaml.safe_load(f)
    return {}


_inf = load_inference_config()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pi-ai-clinic-dev-key")
    LLAMA_API_URL = os.environ.get(
        "LLAMA_API_URL",
        f"http://{_inf.get('server', {}).get('host', '127.0.0.1')}:{_inf.get('server', {}).get('port', 8081)}",
    )
    MAX_TOKENS = _inf.get("safety", {}).get("max_tokens", 512)
    TEMPERATURE = _inf.get("safety", {}).get("temperature", 0.3)
    TOP_P = _inf.get("safety", {}).get("top_p", 0.9)
    KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
