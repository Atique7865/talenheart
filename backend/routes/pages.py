from flask import Blueprint, send_from_directory
import os

pages_bp = Blueprint("pages", __name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")


@pages_bp.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@pages_bp.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)
