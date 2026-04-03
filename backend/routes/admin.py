from flask import Blueprint, render_template_string, request, jsonify, session, redirect, url_for
from extensions import mongo
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
    total_contacts = mongo.db.contacts.count_documents({})
    unread_contacts = mongo.db.contacts.count_documents({"read": False})
    recent_apps = list(mongo.db.applications.find().sort("created_at", -1).limit(10))
    for a in recent_apps:
        a["_id"] = str(a["_id"])
    jobs = list(mongo.db.jobs.find())
    for j in jobs:
        j["_id"] = str(j["_id"])
    stories = list(mongo.db.success_stories.find().sort("year", -1))
    for s in stories:
        s["_id"] = str(s["_id"])
    contact_messages = list(mongo.db.contacts.find().sort("created_at", -1))
    for c in contact_messages:
        c["_id"] = str(c["_id"])
    return render_dashboard(total_jobs, total_apps, pending, accepted, recent_apps, jobs, stories,
                            contact_messages, total_contacts, unread_contacts)


@admin_bp.route("/jobs/add", methods=["POST"])
@require_admin
def add_job():
    from datetime import datetime
    requirements_raw = request.form.get("requirements", "")
    requirements = [r.strip() for r in requirements_raw.split(",") if r.strip()]
    job = {
        "title": request.form.get("title", "").strip(),
        "country": request.form.get("country", "").strip(),
        "flag": request.form.get("flag", "").strip(),
        "salary": request.form.get("salary", "").strip(),
        "salary_bdt": request.form.get("salary_bdt", "").strip(),
        "type": request.form.get("type", "").strip(),
        "requirements": requirements,
        "visa": request.form.get("visa", "").strip(),
        "deadline": request.form.get("deadline", "").strip(),
        "seats": int(request.form.get("seats", 0) or 0),
        "status": "open",
    }
    mongo.db.jobs.insert_one(job)
    return redirect(url_for("admin.dashboard") + "#jobs")


@admin_bp.route("/jobs/delete/<job_id>", methods=["POST"])
@require_admin
def delete_job(job_id):
    mongo.db.jobs.delete_one({"_id": ObjectId(job_id)})
    return redirect(url_for("admin.dashboard") + "#jobs")


@admin_bp.route("/applications/<app_id>/status", methods=["POST"])
@require_admin
def change_status(app_id):
    new_status = request.form.get("status")
    mongo.db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": new_status}})
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/success-stories/add", methods=["POST"])
@require_admin
def add_story():
    story = {
        "name": request.form.get("name", "").strip(),
        "country": request.form.get("country", "").strip(),
        "job": request.form.get("job", "").strip(),
        "salary": request.form.get("salary", "").strip(),
        "story": request.form.get("story", "").strip(),
        "year": int(request.form.get("year", 2024)),
    }
    mongo.db.success_stories.insert_one(story)
    return redirect(url_for("admin.dashboard") + "#stories")


@admin_bp.route("/success-stories/delete/<story_id>", methods=["POST"])
@require_admin
def delete_story(story_id):
    mongo.db.success_stories.delete_one({"_id": ObjectId(story_id)})
    return redirect(url_for("admin.dashboard") + "#stories")


@admin_bp.route("/contact-messages/delete/<msg_id>", methods=["POST"])
@require_admin
def delete_contact_message(msg_id):
    mongo.db.contacts.delete_one({"_id": ObjectId(msg_id)})
    return redirect(url_for("admin.dashboard") + "#contacts")


@admin_bp.route("/contact-messages/<msg_id>/read", methods=["POST"])
@require_admin
def mark_contact_read(msg_id):
    mongo.db.contacts.update_one({"_id": ObjectId(msg_id)}, {"$set": {"read": True}})
    return redirect(url_for("admin.dashboard") + "#contacts")


(error=None):
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


def render_dashboard(total_jobs, total_apps, pending, accepted, recent_apps, jobs, stories,
                     contact_messages=None, total_contacts=0, unread_contacts=0):
    if contact_messages is None:
        contact_messages = []
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
  <div class="d-flex gap-2 align-items-center">
    <a href="#contacts" class="btn btn-outline-light btn-sm position-relative">
      📩 Messages
      {% if unread_contacts > 0 %}
      <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark">{{ unread_contacts }}</span>
      {% endif %}
    </a>
    <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
  </div>
</nav>
<div class="container-fluid py-4 px-4">

  <!-- Stats -->
  <div class="row g-3 mb-4">
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-danger">{{ total_jobs }}</h2><p class="mb-0 text-muted small">Active Jobs</p></div></div>
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-primary">{{ total_apps }}</h2><p class="mb-0 text-muted small">Applications</p></div></div>
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-warning">{{ pending }}</h2><p class="mb-0 text-muted small">Pending</p></div></div>
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-success">{{ accepted }}</h2><p class="mb-0 text-muted small">Accepted</p></div></div>
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-info">{{ total_contacts }}</h2><p class="mb-0 text-muted small">Messages</p></div></div>
    <div class="col-md-2"><div class="card border-0 shadow-sm rounded-4 p-3 text-center">
      <h2 class="fw-bold text-orange" style="color:#fd7e14">{{ unread_contacts }}</h2><p class="mb-0 text-muted small">Unread Msgs</p></div></div>
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

  <!-- Add Job Listing -->
  <div class="card border-0 shadow-sm rounded-4 mb-4" id="jobs">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">➕ Add New Job Listing</div>
    <div class="card-body">
      <form method="POST" action="/admin/jobs/add">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label fw-semibold small">Job Title *</label>
            <input type="text" name="title" class="form-control" placeholder="e.g. Factory Worker" required>
          </div>
          <div class="col-md-3">
            <label class="form-label fw-semibold small">Country *</label>
            <input type="text" name="country" class="form-control" placeholder="e.g. Japan" required>
          </div>
          <div class="col-md-2">
            <label class="form-label fw-semibold small">Flag Emoji</label>
            <input type="text" name="flag" class="form-control" placeholder="🇯🇵">
          </div>
          <div class="col-md-3">
            <label class="form-label fw-semibold small">Job Type *</label>
            <input type="text" name="type" class="form-control" placeholder="e.g. Manufacturing" required>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold small">Salary *</label>
            <input type="text" name="salary" class="form-control" placeholder="e.g. ¥160,000–¥200,000/month" required>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold small">Salary (BDT equivalent)</label>
            <input type="text" name="salary_bdt" class="form-control" placeholder="e.g. ৳1,10,000–৳1,40,000">
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold small">Visa Type</label>
            <input type="text" name="visa" class="form-control" placeholder="e.g. Work Visa">
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold small">Application Deadline</label>
            <input type="date" name="deadline" class="form-control">
          </div>
          <div class="col-md-2">
            <label class="form-label fw-semibold small">Seats Available</label>
            <input type="number" name="seats" class="form-control" placeholder="10" min="1">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-semibold small">Requirements <span class="text-muted">(comma-separated)</span></label>
            <input type="text" name="requirements" class="form-control" placeholder="Age 18-35, Basic fitness, Training provided">
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-danger px-4">➕ Add Job Listing</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <!-- Jobs Table -->
  <div class="card border-0 shadow-sm rounded-4 mb-4">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">💼 Job Listings ({{ jobs|length }})</div>
    <div class="card-body p-0">
      <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light"><tr>
          <th>Title</th><th>Country</th><th>Type</th><th>Salary</th><th>Deadline</th><th>Seats</th><th>Action</th>
        </tr></thead>
        <tbody>
        {% for job in jobs %}
        <tr>
          <td class="fw-semibold">{{ job.title }}</td>
          <td>{{ job.flag }} {{ job.country }}</td>
          <td>{{ job.type }}</td>
          <td>{{ job.salary }}</td>
          <td>{{ job.deadline or '-' }}</td>
          <td>{{ job.seats or '-' }}</td>
          <td>
            <form method="POST" action="/admin/jobs/delete/{{ job._id }}" onsubmit="return confirm('Delete this job?')">
              <button class="btn btn-sm btn-outline-danger">🗑 Delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>
    </div>
  </div>

  <!-- Contact Messages -->
  <div class="card border-0 shadow-sm rounded-4 mb-4" id="contacts">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4 d-flex justify-content-between align-items-center">
      <span>📩 Contact Messages ({{ contact_messages|length }})</span>
      {% if unread_contacts > 0 %}
      <span class="badge bg-warning text-dark">{{ unread_contacts }} Unread</span>
      {% endif %}
    </div>
    <div class="card-body p-0">
      {% if contact_messages %}
      <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light"><tr>
          <th>Name</th><th>Phone</th><th>Email</th><th>Subject</th><th>Message</th><th>Date</th><th>Actions</th>
        </tr></thead>
        <tbody>
        {% for msg in contact_messages %}
        <tr class="{% if not msg.read %}table-warning{% endif %}">
          <td class="fw-semibold">{{ msg.name }}{% if not msg.read %} <span class="badge bg-warning text-dark ms-1 small">New</span>{% endif %}</td>
          <td>{{ msg.phone }}</td>
          <td>{{ msg.email or '-' }}</td>
          <td>{{ msg.subject or '-' }}</td>
          <td style="max-width:250px">
            <span class="text-wrap small">{{ msg.message[:120] }}{% if msg.message|length > 120 %}…{% endif %}</span>
          </td>
          <td class="text-muted small">{{ msg.created_at[:10] if msg.created_at else '-' }}</td>
          <td>
            <div class="d-flex gap-1 flex-wrap">
              {% if not msg.read %}
              <form method="POST" action="/admin/contact-messages/{{ msg._id }}/read">
                <button class="btn btn-sm btn-outline-success" title="Mark as read">✓ Read</button>
              </form>
              {% endif %}
              <form method="POST" action="/admin/contact-messages/delete/{{ msg._id }}" onsubmit="return confirm('Delete this message?')">
                <button class="btn btn-sm btn-outline-danger">🗑</button>
              </form>
            </div>
          </td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>
      {% else %}
      <div class="p-4 text-muted">No contact messages yet.</div>
      {% endif %}
    </div>
  </div>

  <!-- Add Success Story -->
  <div class="card border-0 shadow-sm rounded-4 mt-4" id="stories">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">⭐ Add Success Story</div>
    <div class="card-body">
      <form method="POST" action="/admin/success-stories/add">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label fw-semibold">Full Name</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Md. Rahim Uddin" required>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-semibold">Country (with emoji flag)</label>
            <input type="text" name="country" class="form-control" placeholder="e.g. Japan 🇯🇵" required>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold">Job Title</label>
            <input type="text" name="job" class="form-control" placeholder="e.g. Factory Worker" required>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold">Monthly Salary</label>
            <input type="text" name="salary" class="form-control" placeholder="e.g. ¥185,000/month" required>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-semibold">Year Placed</label>
            <input type="number" name="year" class="form-control" placeholder="2024" min="2000" max="2099" required>
          </div>
          <div class="col-12">
            <label class="form-label fw-semibold">Story / Testimonial</label>
            <textarea name="story" class="form-control" rows="3" placeholder="Write the worker's testimonial here..." required></textarea>
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-danger px-4">➕ Add Story</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <!-- Success Stories List -->
  <div class="card border-0 shadow-sm rounded-4 mt-4 mb-4">
    <div class="card-header bg-white fw-bold fs-5 rounded-top-4">⭐ Published Stories ({{ stories|length }})</div>
    <div class="card-body p-0">
      {% if stories %}
      <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light"><tr>
          <th>Name</th><th>Country</th><th>Job</th><th>Salary</th><th>Year</th><th>Story Preview</th><th>Action</th>
        </tr></thead>
        <tbody>
        {% for s in stories %}
        <tr>
          <td class="fw-semibold">{{ s.name }}</td>
          <td>{{ s.country }}</td>
          <td>{{ s.job }}</td>
          <td>{{ s.salary }}</td>
          <td>{{ s.year }}</td>
          <td><span class="text-muted small">{{ s.story | truncate(70) }}</span></td>
          <td>
            <form method="POST" action="/admin/success-stories/delete/{{ s._id }}" onsubmit="return confirm('Delete this story?')">
              <button class="btn btn-sm btn-outline-danger">🗑 Delete</button>
            </form>
          </td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
      </div>
      {% else %}
      <div class="p-4 text-muted">No success stories yet. Add one above.</div>
      {% endif %}
    </div>
  </div>

</div>
</body></html>"""
    from flask import render_template_string
    return render_template_string(html, total_jobs=total_jobs, total_apps=total_apps,
                                  pending=pending, accepted=accepted,
                                  recent_apps=recent_apps, jobs=jobs, stories=stories,
                                  contact_messages=contact_messages,
                                  total_contacts=total_contacts,
                                  unread_contacts=unread_contacts)
