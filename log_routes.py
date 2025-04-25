import datetime
from flask import Blueprint, request, redirect, url_for, flash
import gcs_utils

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/plant/<plant_id>/add_log", methods=["POST"])
def add_care_log(plant_id):
    """Adds a care log entry to a plant using a single text field."""
    plant = gcs_utils.get_plant_data(plant_id)
    if not plant:
        flash(f"Plant with ID {plant_id} not found.", "error")
        return redirect(url_for("plants.index"))

    log_text = request.form.get("log_text")

    if not log_text:
        flash("Log entry text cannot be empty.", "error")
        return redirect(url_for("plants.plant_detail", plant_id=plant_id))

    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "text": log_text,
    }

    if not isinstance(plant.get("care_log"), list):
        plant["care_log"] = []

    plant["care_log"].append(log_entry)

    if gcs_utils.save_plant_data(plant):
        flash("Care log entry added.", "success")
    else:
        flash("Error saving care log entry.", "error")

    return redirect(url_for("plants.plant_detail", plant_id=plant_id))


@logs_bp.route("/plant/<plant_id>/delete_log/<log_timestamp>", methods=["POST"])
def delete_care_log(plant_id, log_timestamp):
    """Deletes a specific care log entry for a plant."""
    plant = gcs_utils.get_plant_data(plant_id)
    if not plant:
        flash(f"Plant with ID {plant_id} not found.", "error")
        return redirect(url_for("plants.index"))

    care_log = plant.get("care_log", [])
    if not isinstance(care_log, list):
        flash(f"Care log for plant {plant_id} is not in the expected format.", "error")
        return redirect(url_for("plants.plant_detail", plant_id=plant_id))

    original_length = len(care_log)
    plant["care_log"] = [
        entry for entry in care_log if entry.get("timestamp") != log_timestamp
    ]

    if len(plant["care_log"]) == original_length:
        flash(f"Log entry with timestamp {log_timestamp} not found.", "warning")
    else:
        if gcs_utils.save_plant_data(plant):
            flash("Care log entry deleted successfully.", "success")
        else:
            flash("Error saving plant data after deleting log entry.", "error")

    return redirect(url_for("plants.plant_detail", plant_id=plant_id))
