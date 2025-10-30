print("✅ THIS IS THE REAL APP FILE")

import os
from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from werkzeug.utils import secure_filename

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ 'python-dotenv' not found. Make sure it's in requirements.txt.")

app = Flask(__name__)

# Environment variables
STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")
IMAGES_CONTAINER = os.getenv("IMAGES_CONTAINER")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Azure Blob setup
try:
    bsc = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    cc = bsc.get_container_client(IMAGES_CONTAINER)
except Exception as e:
    print(f"❌ Azure Blob setup failed: {e}")
    cc = None

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/gif"}
MAX_FILE_SIZE_MB = 10

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/v1/upload", methods=["POST"])
def upload():
    if cc is None:
        return jsonify(ok=False, error="Blob container not initialized"), 500

    f = request.files.get("file")
    if not f:
        return jsonify(ok=False, error="Missing file"), 400
    if f.content_type not in ALLOWED_TYPES:
        return jsonify(ok=False, error="Invalid file type"), 400
    if len(f.read()) > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify(ok=False, error="File too large"), 400
    f.seek(0)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    safe_name = secure_filename(f.filename)
    blob_name = f"{timestamp}-{safe_name}"

    try:
        cc.upload_blob(name=blob_name, data=f, overwrite=True)
        blob_url = f"{cc.url}/{blob_name}"
        return jsonify(ok=True, url=blob_url)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.route("/api/v1/gallery", methods=["GET"])
def gallery():
    if cc is None:
        return jsonify(ok=False, error="Blob container not initialized"), 500

    try:
        blobs = cc.list_blobs()
        urls = [f"{cc.url}/{blob.name}" for blob in blobs]
        return jsonify(ok=True, gallery=urls)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.route("/api/v1/health")
def health():
    return "status: ok", 200

@app.route("/upload", methods=["POST"])
def upload_simple():
    print("/upload route was hit")
    return upload()

if __name__ == "__main__":
    print("✅ THIS IS THE REAL APP FILE")
    print("Registered routes:", [rule.rule for rule in app.url_map.iter_rules()])
    app.run(host="0.0.0.0", port=8000)