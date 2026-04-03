from flask import Blueprint, jsonify, request
from app import mongo
from bson import ObjectId
import json

jobs_bp = Blueprint("jobs", __name__)


def job_to_dict(job):
    job["_id"] = str(job["_id"])
    return job


@jobs_bp.route("/", methods=["GET"])
def get_jobs():
    country = request.args.get("country", "")
    job_type = request.args.get("type", "")
    query = {"status": "open"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    if job_type:
        query["type"] = {"$regex": job_type, "$options": "i"}
    jobs = list(mongo.db.jobs.find(query))
    return jsonify([job_to_dict(j) for j in jobs])


@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = mongo.db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job_to_dict(job))
    except Exception:
        return jsonify({"error": "Invalid ID"}), 400


@jobs_bp.route("/", methods=["POST"])
def create_job():
    data = request.get_json()
    required = ["title", "country", "salary", "type"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    data["status"] = "open"
    result = mongo.db.jobs.insert_one(data)
    return jsonify({"message": "Job created", "id": str(result.inserted_id)}), 201


@jobs_bp.route("/<job_id>", methods=["PUT"])
def update_job(job_id):
    data = request.get_json()
    try:
        mongo.db.jobs.update_one({"_id": ObjectId(job_id)}, {"$set": data})
        return jsonify({"message": "Updated"})
    except Exception:
        return jsonify({"error": "Invalid ID"}), 400


@jobs_bp.route("/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        mongo.db.jobs.delete_one({"_id": ObjectId(job_id)})
        return jsonify({"message": "Deleted"})
    except Exception:
        return jsonify({"error": "Invalid ID"}), 400
