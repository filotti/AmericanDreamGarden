import os
from flask import Flask
from dotenv import load_dotenv
from plant_routes import plants_bp
from photo_routes import photos_bp
from log_routes import logs_bp
from template_filters import format_datetime_filter, nl2br_filter
from context_processors import inject_now

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_default_secret_key")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.register_blueprint(plants_bp)
app.register_blueprint(photos_bp)
app.register_blueprint(logs_bp)

app.add_template_filter(format_datetime_filter, "format_datetime")
app.add_template_filter(nl2br_filter, "nl2br")

app.context_processor(inject_now)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
