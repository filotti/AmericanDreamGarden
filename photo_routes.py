from flask import Blueprint, request, redirect, url_for, flash, abort, send_file
import gcs_utils
from utils import allowed_file
from werkzeug.utils import secure_filename

photos_bp = Blueprint("photos", __name__)


@photos_bp.route("/plant/<plant_id>/add_photo", methods=["POST"])
def add_photo(plant_id):
    """Adds a new photo to an existing plant."""
    plant = gcs_utils.get_plant_data(plant_id)
    if not plant:
        flash(f"Plant with ID {plant_id} not found.", "error")
        return redirect(url_for("plants.index"))

    if "photo" not in request.files:
        flash("No photo file selected.", "error")
        return redirect(url_for("plants.plant_detail", plant_id=plant_id))

    file = request.files["photo"]

    if file.filename == "":
        flash("No selected file.", "error")
        return redirect(url_for("plants.plant_detail", plant_id=plant_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        result = gcs_utils.upload_photo(plant_id, file)
        if result:
            flash(f"Photo '{filename}' added successfully!", "success")
        else:
            flash(f"Error uploading photo '{filename}'.", "error")
    elif file and not allowed_file(file.filename):
        flash(f"File type not allowed for {file.filename}", "warning")

    return redirect(url_for("plants.plant_detail", plant_id=plant_id))


@photos_bp.route("/plant/<plant_id>/photo/<path:filename>")
def serve_plant_photo(plant_id, filename):
    """Fetches a photo from GCS and serves it to the client."""
    if ".." in filename or "/" in filename:
        abort(404)

    photo_data, content_type = gcs_utils.get_photo_data(plant_id, filename)

    if photo_data:
        return send_file(photo_data, mimetype=content_type, as_attachment=False)
    else:
        abort(404)


@photos_bp.route("/plant/<plant_id>/photo/delete/<path:filename>", methods=["POST"])
def delete_photo_route(plant_id, filename):
    """Handles deleting a specific photo for a plant."""
    if gcs_utils.delete_single_photo(plant_id, filename):
        flash(f"Photo '{filename}' deleted successfully.", "success")
    else:
        flash(f"Error deleting photo '{filename}'. Check logs or GCS.", "error")

    return redirect(url_for("plants.plant_detail", plant_id=plant_id))
