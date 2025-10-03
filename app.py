# app.py
import os
import shutil
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from organizer import organize_directory, ALLOWED_EXTENSIONS, CATEGORY_MAP

BASE_UPLOAD_DIR = Path.cwd() / "user_files"  # sandboxed root for all operations
BASE_UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB per request

def safe_path(resolve_path: str) -> Path:
    p = (BASE_UPLOAD_DIR / resolve_path).resolve()
    if not str(p).startswith(str(BASE_UPLOAD_DIR.resolve())):
        raise ValueError("Invalid path")
    return p

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/upload", methods=["POST"])
def upload_files():
    target = request.form.get("target_dir", "").strip()
    try:
        target_path = safe_path(target) if target else BASE_UPLOAD_DIR
    except ValueError:
        return jsonify({"error": "Invalid target directory"}), 400
    target_path.mkdir(parents=True, exist_ok=True)

    files = request.files.getlist("files[]")
    saved = []
    for f in files:
        filename = secure_filename(f.filename)
        if not filename:
            continue
        # optional: limit by extension
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext and ext not in ALLOWED_EXTENSIONS:
            # allow unknown extensions but warn
            pass
        dest = target_path / f"{uuid.uuid4().hex}_{filename}"
        f.save(dest)
        saved.append(str(dest.relative_to(BASE_UPLOAD_DIR)))

    return jsonify({"saved": saved}), 200

@app.route("/api/list_dirs", methods=["GET"])
def list_dirs():
    # returns list of directories under BASE_UPLOAD_DIR (one level)
    items = []
    for d in BASE_UPLOAD_DIR.iterdir():
        if d.is_dir():
            items.append(str(d.relative_to(BASE_UPLOAD_DIR)))
    return jsonify({"dirs": items})

@app.route("/api/organize", methods=["POST"])
def organize():
    data = request.get_json() or {}
    src = data.get("source", "")
    dry = bool(data.get("dry", False))
    try:
        src_path = safe_path(src) if src else BASE_UPLOAD_DIR
    except ValueError:
        return jsonify({"error": "Invalid source path"}), 400
    if not src_path.exists() or not src_path.is_dir():
        return jsonify({"error": "Source directory does not exist"}), 400

    result = organize_directory(src_path, dry_run=dry)
    return jsonify(result)

@app.route("/api/download/<path:relpath>", methods=["GET"])
def download(relpath):
    try:
        p = safe_path(relpath)
    except ValueError:
        abort(404)
    if p.is_file():
        return send_from_directory(p.parent, p.name, as_attachment=True)
    abort(404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)