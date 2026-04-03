from flask import Blueprint, jsonify, request
from app import mongo
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from datetime import datetime

applications_bp = Blueprint("applications", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@applications_bp.route("/", methods=["POST"])
def submit_application():
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        passport = request.form.get("passport", "").strip()
        skills = request.form.get("skills", "").strip()
        job_id = request.form.get("job_id", "").strip()
        job_title = request.form.get("job_title", "").strip()
        country = request.form.get("country", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, phone]):
            return jsonify({"error": "Name, email and phone are required"}), 400

        cv_filename = None
        if "cv" in request.files:
            file = request.files["cv"]
            if file and file.filename and allowed_file(file.filename):
                cv_filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, cv_filename))

        application = {
            "name": name,
            "email": email,
            "phone": phone,
            "passport": passport,
            "skills": skills,
            "job_id": job_id,
            "job_title": job_title,
            "country": country,
            "message": message,
            "cv": cv_filename,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        result = mongo.db.applications.insert_one(application)
        return jsonify({"message": "Application submitted successfully!", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@applications_bp.route("/", methods=["GET"])
def get_applications():
    country = request.args.get("country", "")
    status = request.args.get("status", "")
    query = {}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    if status:
        query["status"] = status
    apps = list(mongo.db.applications.find(query).sort("created_at", -1))
    for a in apps:
        a["_id"] = str(a["_id"])
    return jsonify(apps)


@applications_bp.route("/<app_id>/status", methods=["PUT"])
def update_status(app_id):
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ["pending", "reviewing", "accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400
    try:
        mongo.db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": new_status}})
        return jsonify({"message": "Status updated"})
    except Exception:
        return jsonify({"error": "Invalid ID"}), 400
