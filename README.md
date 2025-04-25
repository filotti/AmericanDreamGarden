# American Dream Garden

A simple web application for managing your garden plants with photo uploads and care logs.

## Overview

American Dream Garden is a Flask-based web application designed to help gardeners track information about their plants, including:

- Basic plant information
- Photo galleries for each plant
- Care logs to track watering, fertilizing, and other maintenance activities

The application uses Google Cloud Storage (GCS) for data persistence instead of a traditional database. This design choice makes the application simpler to deploy and maintain for small to medium collections of plants, avoiding the need to provision and manage a database server.

## Features

- **Plant Management**: Add, edit, and delete plants with unique IDs
- **Photo Management**: Upload, view, and delete photos for each plant
- **Care Logging**: Track all care activities with timestamped entries
- **Responsive Design**: Works on desktop and mobile devices

## Technical Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, Bootstrap 5
- **Storage**: Google Cloud Storage (GCS)
- **Containerization**: Docker
- **Deployment**: Google Cloud Run

## Prerequisites

- Google Cloud Platform account
- Google Cloud SDK installed locally
- Python 3.12+ for local development

## Setup and Deployment

### Setting Up Google Cloud Storage

1. Create a new GCS bucket:
   ```bash
   gsutil mb gs://your-garden-bucket-name
   ```

### Docker Build and Deploy to Google Cloud Run

1. Create a repository in Google Artifact Registry:
   ```bash
   gcloud artifacts repositories create garden-repo \
     --repository-format=docker \
     --location=us-central1 \
     --description="Repository for American Dream Garden"
   ```

2. Configure Docker to use Google Artifact Registry:
   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

3. Build and tag your Docker image for Artifact Registry:
   ```bash
   docker build -t us-central1-docker.pkg.dev/your-project-id/garden-repo/american-dream-garden:latest .
   ```

4. Push the image to Artifact Registry:
   ```bash
   docker push us-central1-docker.pkg.dev/your-project-id/garden-repo/american-dream-garden:latest
   ```

5. Deploy to Cloud Run:
   ```bash
   gcloud run deploy american-dream-garden \
     --image us-central1-docker.pkg.dev/your-project-id/garden-repo/american-dream-garden:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GCS_BUCKET_NAME=your-garden-bucket-name,FLASK_SECRET_KEY=your-secret-key"
   ```

## Data Structure

The application stores data in Google Cloud Storage using the following structure:

- **Plant Data**: JSON files stored in the `data/` prefix
  - Format: `data/plant_{id}.json`
  - Contains plant metadata (species, care logs, etc.)

- **Photos**: Image files stored in the `photos/` prefix
  - Format: `photos/{plant_id}/{filename}`
  - Each plant has its own folder of photos

This approach avoids the need for a database while still providing structured data storage. For small to medium-sized personal gardens (typically with dozens, not thousands, of plants), this storage method is efficient and simplifies the application architecture.

## Why GCS Instead of a Database?

For this application, a traditional database is likely overkill for several reasons:

1. **Scale**: Most home gardeners have tens or hundreds of plants, not thousands or millions
2. **Simplicity**: No need to maintain a database server or connection pool
3. **Cost-Effective**: GCS pricing is very economical for this usage pattern
4. **Built-in File Storage**: Natively handles both structured data (JSON) and binary data (photos)
5. **Serverless Compatible**: Works well with stateless services like Cloud Run

## Usage Guide

### Adding a Plant

1. Click "Add Plant" in the navigation bar
2. Enter a unique ID for your plant (e.g., "monstera-living-room")
3. Optionally enter species information
4. Optionally upload initial photos
5. Click "Add Plant" to save

### Managing Photos

From a plant's detail page:
1. Scroll to the Photos section
2. Use the "Upload Photo" button to add new photos
3. Click the "X" button on any photo to delete it

### Recording Care Activities

From a plant's detail page:
1. Scroll to the Care Log section
2. Enter your log entry in the text area
3. Click "Add Entry" to save
4. Previous entries are displayed in reverse chronological order
5. Delete any entry by clicking the "X" button next to it

## Development and Customization

The application follows a simple Blueprint-based Flask structure:

- `app.py`: Main application entry point
- `plant_routes.py`: Routes for plant management
- `photo_routes.py`: Routes for photo uploads and management
- `log_routes.py`: Routes for care log management
- `gcs_utils.py`: Utilities for interacting with Google Cloud Storage

To customize the application, you can modify the HTML templates in the `templates/` directory or the styling in `static/style.css`.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
