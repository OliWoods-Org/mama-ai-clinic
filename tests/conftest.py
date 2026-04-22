"""Test configuration for MAMA AI Clinic."""

import pytest
from app.app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    LLAMA_API_URL = "http://127.0.0.1:9999"  # Fake URL for testing


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
