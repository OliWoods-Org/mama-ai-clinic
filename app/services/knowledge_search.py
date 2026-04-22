"""Search pre-loaded medical knowledge bases."""

import json
import os
from flask import current_app


def search_knowledge(query: str, category: str = None) -> list[dict]:
    """Search across all knowledge bases for relevant content.

    Args:
        query: Search terms.
        category: Optional filter -- "imnci", "medicines", "first_aid", "training".

    Returns:
        List of matching knowledge entries with source attribution.
    """
    kb_dir = current_app.config["KNOWLEDGE_DIR"]
    results = []
    query_lower = query.lower()

    categories = [category] if category else ["imnci", "essential_medicines", "first_aid", "training"]

    for cat in categories:
        cat_dir = os.path.join(kb_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for filename in os.listdir(cat_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(cat_dir, filename)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                matches = _search_in_data(data, query_lower, source=f"{cat}/{filename}")
                results.extend(matches)
            except (json.JSONDecodeError, IOError):
                continue

    return sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)[:10]


def _search_in_data(data, query: str, source: str) -> list[dict]:
    """Simple keyword search within a JSON knowledge structure."""
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and query in value.lower():
                results.append({
                    "source": source,
                    "key": key,
                    "content": value[:500],
                    "relevance": _score(query, value.lower()),
                })
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        text = json.dumps(item).lower()
                        if query in text:
                            results.append({
                                "source": source,
                                "key": key,
                                "content": json.dumps(item)[:500],
                                "relevance": _score(query, text),
                            })
    return results


def _score(query: str, text: str) -> float:
    """Simple relevance score based on term frequency."""
    terms = query.split()
    if not terms:
        return 0.0
    matches = sum(1 for t in terms if t in text)
    return matches / len(terms)
