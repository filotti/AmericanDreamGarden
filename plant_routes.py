from flask import Blueprint, render_template, request, redirect, url_for, flash
import gcs_utils
from utils import allowed_file

plants_bp = Blueprint("plants", __name__, template_folder="templates")


@plants_bp.route("/")
def index():
    """Displays the list of all plants."""
    plants = gcs_utils.list_plants_data()
    plants.sort(key=lambda p: p.get("id", ""))
    return render_template("index.html", plants=plants)


@plants_bp.route("/plant/<plant_id>")
def plant_detail(plant_id):
    """Displays details for a specific plant."""
    plant = gcs_utils.get_plant_data(plant_id)
    if not plant:
        flash(f"Plant with ID {plant_id} not found.", "error")
        return redirect(url_for("plants.index"))

    care_log = plant.get("care_log", [])
    if isinstance(care_log, list):
        care_log.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        plant["care_log"] = care_log
    else:
        plant["care_log"] = []
        flash(
            f"Warning: Care log for plant {plant_id} was not in the expected format.",
            "warning",
        )
    return render_template("plant_detail.html", plant=plant)


@plants_bp.route("/plant/new", methods=["GET", "POST"])
def add_plant():
    """Handles adding a new plant using a user-provided ID."""
    if request.method == "POST":
        plant_id = request.form.get("plant_id")
        species = request.form.get("species")

        if not plant_id:
            flash("Plant ID is required.", "error")
            return render_template("plant_form.html")

        if gcs_utils.get_plant_data(plant_id):
            flash(f"Plant with ID '{plant_id}' already exists.", "error")
            return render_template(
                "plant_form.html", plant_id=plant_id, species=species
            )

        new_plant_data = {
            "id": plant_id,
            "species": species,
            "care_log": [],
        }

        files = request.files.getlist("photos")
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                result = gcs_utils.upload_photo(plant_id, file)
                if not result:
                    flash(f"Error uploading photo {file.filename}", "warning")
            elif file and file.filename and not allowed_file(file.filename):
                flash(f"File type not allowed for {file.filename}", "warning")

        if gcs_utils.save_plant_data(new_plant_data):
            flash(f"Plant with ID '{plant_id}' added successfully!", "success")
            return redirect(url_for("plants.plant_detail", plant_id=plant_id))
        else:
            flash("Error saving plant data.", "error")
            return render_template(
                "plant_form.html", plant_id=plant_id, species=species
            )

    return render_template("plant_form.html")


@plants_bp.route("/plant/edit/<plant_id>", methods=["GET", "POST"])
def edit_plant(plant_id):
    """Handles editing an existing plant."""
    plant = gcs_utils.get_plant_data(plant_id)
    if not plant:
        flash(f"Plant with ID {plant_id} not found.", "error")
        return redirect(url_for("plants.index"))

    if request.method == "POST":
        plant["species"] = request.form.get("species", plant.get("species", ""))

        if gcs_utils.save_plant_data(plant):
            flash(
                f"Plant '{plant.get('id', plant_id)}' updated successfully!", "success"
            )
            return redirect(url_for("plants.plant_detail", plant_id=plant_id))
        else:
            flash("Error saving updated plant data.", "error")
            return render_template(
                "plant_form.html",
                plant=plant,
                form_action=url_for("plants.edit_plant", plant_id=plant_id),
                is_edit=True,
            )

    plant.setdefault("species", "")
    return render_template(
        "plant_form.html",
        plant=plant,
        form_action=url_for("plants.edit_plant", plant_id=plant_id),
        is_edit=True,
    )


@plants_bp.route("/plant/delete/<plant_id>", methods=["POST"])
def delete_plant(plant_id):
    """Deletes a plant and its associated data/photos."""
    plant = gcs_utils.get_plant_data(plant_id)
    photos_deleted = gcs_utils.delete_plant_photos(plant_id)
    data_deleted = gcs_utils.delete_plant_data(plant_id)

    if data_deleted:
        flash(f"Plant '{plant_id}' and its data deleted.", "success")
        if not photos_deleted:
            flash(
                f"Note: There might have been an issue deleting photos for '{plant_id}'. Check GCS.",
                "warning",
            )
    else:
        flash(f"Error deleting plant data for '{plant_id}'.", "error")
        if photos_deleted:
            flash(
                f"Associated photos for '{plant_id}' were deleted, but data deletion failed.",
                "warning",
            )
        else:
            flash(
                f"Deletion of photos for '{plant_id}' might also have failed.",
                "warning",
            )

    return redirect(url_for("plants.index"))
