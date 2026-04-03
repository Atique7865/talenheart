from flask import Blueprint, render_template_string, request, jsonify, session, redirect, url_for
from app import mongo
from bson import ObjectId
import os

admin_bp = Blueprint("admin", __name__)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        return render_admin_login("Invalid password")
    return render_admin_login()


@admin_bp.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin.login"))


def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@require_admin
def dashboard():
    total_jobs = mongo.db.jobs.count_documents({})
    total_apps = mongo.db.applications.count_documents({})
    pending = mongo.db.applications.count_documents({"status": "pending"})
    accepted = mongo.db.applications.count_documents({"status": "accepted"})
    recent_apps = list(mongo.db.applications.find().sort("created_at", -1).limit(10))
    for a in recent_apps:
        a["_id"] = str(a["_id"])
    jobs = list(mongo.db.jobs.find())
    for j in jobs:
        j["_id"] = str(j["_id"])
    return render_dashboard(total_jobs, total_apps, pending, accepted, recent_apps, jobs)


@admin_bp.route("/jobs/delete/<job_id>", methods=["POST"])
@require_admin
def delete_job(job_id):
    mongo.db.jobs.delete_one({"_id": ObjectId(job_id)})
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/applications/<app_id>/status", methods=["POST"])
@require_admin
def change_status(app_id):
    new_status = request.form.get("status")
    mongo.db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": new_status}})
    return redirect(url_for("admin.dashboard"))


def render_admin_login(error=None):
    html = """
<!DOCTYPE html>
<html>
<head><title>Admin Login – TalentHeart</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark d-flex align-items-center" style="min-height:100vh">
<div class="container" style="max-width:400px">
  <div class="card shadow-lg border-0 rounded-4 p-4">
    <div class="text-center mb-4">
      <h2 class="fw-bold text-danger">🏢 TalentHeart</h2>
      <p class="text-muted">Admin Panel</p>
    </div>
    {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
    <form method="POST">
      <div class="mb-3">
        <label class="form-label fw-semibold">Admin Password</label>
        <input type="password" name="password" class="form-control form-control-lg" placeholder="Enter password" required>
      </div>
      <button type="submit" class="btn btn-danger btn-lg w-100">Login</button>
    </form>
  </div>
</div>
</body></html>"""
    from flask import render_template_string
    return render_template_string(html, error=error)


def render_dashboard(total_jobs, total_apps, pending, accepted, recent_apps, jobs):
    html = """
<!DOCTYPE html>
<html>
<head>
<title>Admin Dashboard – TalentHeart</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-danger px-4">
  <span class="navbar-brand fw-bold fs-4">🏢 TalentHeart Admin</span>
  <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
</nav>
<div class="container-fluid py-4 px-4">

  <!-- Stats -->
  <div class="row g-3 mb-4">
    <div class="col-md-3"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-danger">{{ total_jobs }}</h2><p class="mb-0 text-muted">Active Jobs</p></div></div>
    <div class="col-md-3"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-primary">{{ total_apps }}</h2><p class="mb-0 text-muted">Total Applications</p></div></div>
    <div class="col-md-3"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-warning">{{ pending }}</h2><p class="mb-0 text-muted">Pending</p></div></div>
    <div class="col-md-3"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-success">{{ accepted }}</h2><p class="mb-0 text-muted">Accepted</p></div></div>
  </div>

  <!-- Applications Table -->
  <div class="card border-0 shadow-sm rounded-4 mb-4">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">📋 Recent Applications</div>
    <div class="card-body p-0">
      <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light"><tr>
          <th>Name</th><th>Email</th><th>Phone</th><th>Job</th><th>Country</th><th>Status</th><th>Action</th>
        </tr></thead>
        <tbody>
        {% for app in recent_apps %}
        <tr>
          <td>{{ app.name }}</td>
          <td>{{ app.email }}</td>
          <td>{{ app.phone }}</td>
          <td>{{ app.job_title or '-' }}</td>
          <td>{{ app.country or '-' }}</td>
          <td>
            <span class="badge {% if app.status == 'accepted' %}bg-success{% elif app.status == 'rejected' %}bg-danger{% elif app.status == 'reviewing' %}bg-warning text-dark{% else %}bg-secondary{% endif %}">
              {{ app.status }}
            </span>
          </td>
          <td>
            <form method="POST" action="/admin/applications/{{ app._id }}/status" class="d-flex gap-1">
              <select name="status" class="form-select form-select-sm" style="width:130px">
                <option value="pending">Pending</option>
                <option value="reviewing">Reviewing</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
              </select>
              <button class="btn btn-sm btn-primary">Update</button>
            </form>
          </td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- Jobs Table -->
  <div class="card border-0 shadow-sm rounded-4">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">💼 Job Listings</div>
    <div class="card-body p-0">
      <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light"><tr>
          <th>Title</th><th>Country</th><th>Type</th><th>Salary</th><th>Deadline</th><th>Action</th>
        </tr></thead>
        <tbody>
        {% for job in jobs %}
        <tr>
          <td>{{ job.title }}</td>
          <td>{{ job.flag }} {{ job.country }}</td>
          <td>{{ job.type }}</td>
          <td>{{ job.salary }}</td>
          <td>{{ job.deadline or '-' }}</td>
          <td>
            <form method="POST" action="/admin/jobs/delete/{{ job._id }}" onsubmit="return confirm('Delete this job?')">
              <button class="btn btn-sm btn-outline-danger">Delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>
    </div>
  </div>

</div>
</body></html>"""
    from flask import render_template_string
    return render_template_string(html, total_jobs=total_jobs, total_apps=total_apps,
                                  pending=pending, accepted=accepted,
                                  recent_apps=recent_apps, jobs=jobs)
