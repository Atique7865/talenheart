from flask import Blueprint, jsonify
from extensions import mongo

stories_bp = Blueprint("success_stories", __name__)


@stories_bp.route("/")
def get_stories():
    stories = list(mongo.db.success_stories.find().sort("year", -1))
    for s in stories:
        s["_id"] = str(s["_id"])
    return jsonify(stories)
