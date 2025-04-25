import os
import json
import logging
from google.cloud import storage
from google.api_core.exceptions import NotFound
from io import BytesIO

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET_NAME environment variable not set.")

DATA_PREFIX = "data/"
PHOTOS_PREFIX = "photos/"

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

logging.basicConfig(level=logging.INFO)


def _get_blob_path(plant_id, filename=None, is_data=True):
    """Helper to construct GCS blob paths."""
    if is_data:
        return f"{DATA_PREFIX}plant_{plant_id}.json"
    else:
        if not filename:
            raise ValueError("Filename is required for photos.")
        return f"{PHOTOS_PREFIX}{plant_id}/{filename}"


def list_plants_data():
    """Lists all plant JSON data files from GCS and includes the first photo filename."""
    plants = []
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=DATA_PREFIX)
    for blob in blobs:
        if blob.name.endswith(".json"):
            try:
                plant_data = json.loads(blob.download_as_string())
                plant_id = plant_data.get("id")
                if plant_id:
                    photo_filenames = list_plant_photos(plant_id)
                    plant_data["first_photo_filename"] = (
                        photo_filenames[0] if photo_filenames else None
                    )
                else:
                    plant_data["first_photo_filename"] = None
                plants.append(plant_data)
            except json.JSONDecodeError:
                logging.error(f"Could not decode JSON for blob: {blob.name}")
            except Exception as e:
                logging.error(f"Error processing blob {blob.name}: {e}")
    return plants


def get_plant_data(plant_id):
    """Retrieves a specific plant's data from GCS."""
    blob_path = _get_blob_path(plant_id, is_data=True)
    blob = bucket.blob(blob_path)
    try:
        data = json.loads(blob.download_as_string())
        data["photo_filenames"] = list_plant_photos(plant_id)
        data.pop("photo_urls", None)
        return data
    except NotFound:
        logging.warning(f"Plant data not found: {blob_path}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON for blob: {blob_path}")
        return None
    except Exception as e:
        logging.error(f"Error getting plant data {plant_id}: {e}")
        return None


def save_plant_data(plant_data):
    """Saves plant data (as JSON) to GCS."""
    plant_id = plant_data.get("id")
    if not plant_id:
        raise ValueError("Plant data must have an 'id'.")

    blob_path = _get_blob_path(plant_id, is_data=True)
    blob = bucket.blob(blob_path)
    try:
        data_to_save = {
            k: v
            for k, v in plant_data.items()
            if k not in ["photo_urls", "photo_filenames", "first_photo_filename"]
        }
        blob.upload_from_string(
            json.dumps(data_to_save, indent=2), content_type="application/json"
        )
        logging.info(f"Saved plant data to {blob_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving plant data {plant_id}: {e}")
        return False


def delete_plant_data(plant_id):
    """Deletes a plant's JSON data file from GCS."""
    blob_path = _get_blob_path(plant_id, is_data=True)
    blob = bucket.blob(blob_path)
    try:
        blob.delete()
        logging.info(f"Deleted plant data: {blob_path}")
        return True
    except NotFound:
        logging.warning(f"Plant data not found for deletion: {blob_path}")
        return False
    except Exception as e:
        logging.error(f"Error deleting plant data {plant_id}: {e}")
        return False


def upload_photo(plant_id, file_storage):
    """Uploads a photo file (Flask FileStorage object) to GCS."""
    if not file_storage or not file_storage.filename:
        raise ValueError("Invalid file storage object provided.")

    filename = file_storage.filename
    blob_path = _get_blob_path(plant_id, filename=filename, is_data=False)
    blob = bucket.blob(blob_path)

    try:
        file_storage.seek(0)
        blob.upload_from_file(file_storage, content_type=file_storage.content_type)
        logging.info(f"Uploaded photo to {blob_path}")
        return True
    except Exception as e:
        logging.error(f"Error uploading photo for plant {plant_id}: {e}")
        return None


def list_plant_photos(plant_id):
    """Lists filenames of photos for a specific plant."""
    photo_filenames = []
    prefix = f"{PHOTOS_PREFIX}{plant_id}/"
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=prefix)
    for blob in blobs:
        if blob.name != prefix:
            filename = os.path.basename(blob.name)
            photo_filenames.append(filename)
    photo_filenames.sort()
    return photo_filenames


def get_photo_data(plant_id, filename):
    """Downloads photo data as bytes from GCS."""
    blob_path = _get_blob_path(plant_id, filename=filename, is_data=False)
    blob = bucket.blob(blob_path)
    try:
        byte_stream = BytesIO()
        blob.download_to_file(byte_stream)
        byte_stream.seek(0)
        content_type = blob.content_type or "application/octet-stream"
        return byte_stream, content_type
    except NotFound:
        logging.warning(f"Photo not found: {blob_path}")
        return None, None
    except Exception as e:
        logging.error(f"Error downloading photo {filename} for plant {plant_id}: {e}")
        return None, None


def delete_plant_photos(plant_id):
    """Deletes all photos for a specific plant."""
    prefix = f"{PHOTOS_PREFIX}{plant_id}/"
    blobs = storage_client.list_blobs(BUCKET_NAME, prefix=prefix)
    deleted_count = 0
    try:
        blobs_to_delete = list(blobs)
        for blob in blobs_to_delete:
            blob.delete()
            deleted_count += 1
        logging.info(f"Deleted {deleted_count} photos for plant {plant_id}")
        return True
    except Exception as e:
        logging.error(f"Error deleting photos for plant {plant_id}: {e}")
        return False


def delete_single_photo(plant_id, filename):
    """Deletes a specific photo for a plant."""
    try:
        blob_name = f"photos/{plant_id}/{filename}"
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()
            logging.info(
                f"Successfully deleted photo: {blob_name} from bucket {BUCKET_NAME}"
            )
            return True
        else:
            logging.warning(f"Photo not found, cannot delete: {blob_name}")
            return True

    except NotFound:
        logging.warning(f"Photo not found during deletion attempt: {blob_name}")
        return True
    except Exception as e:
        logging.error(
            f"Error deleting photo {filename} for plant {plant_id} from GCS: {e}"
        )
        return False
