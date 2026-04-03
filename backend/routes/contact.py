from flask import Blueprint, jsonify, request
from extensions import mongo
from datetime import datetime

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/", methods=["POST"])
def submit_contact():
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        if not name or not phone or not message:
            return jsonify({"error": "Name, phone and message are required"}), 400

        contact_msg = {
            "name": name,
            "phone": phone,
            "email": email,
            "subject": subject,
            "message": message,
            "created_at": datetime.utcnow().isoformat(),
            "read": False,
        }
        result = mongo.db.contacts.insert_one(contact_msg)
        return jsonify({"message": "Message sent successfully!", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
