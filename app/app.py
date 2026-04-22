"""Pi AI Clinic -- Flask application factory."""

from flask import Flask
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .routes import triage, medicines, training, chat, status
    app.register_blueprint(triage.bp)
    app.register_blueprint(medicines.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(status.bp)

    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    return app
