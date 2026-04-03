from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import mongo
import os

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://mongo:27017/talentheart")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

    CORS(app)
    mongo.init_app(app)

    from routes.jobs import jobs_bp
    from routes.applications import applications_bp
    from routes.admin import admin_bp
    from routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(applications_bp, url_prefix="/api/applications")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Seed sample data on first run
    with app.app_context():
        seed_data()

    return app


def seed_data():
    if mongo.db.jobs.count_documents({}) == 0:
        sample_jobs = [
            {
                "title": "Factory Worker",
                "country": "Japan",
                "flag": "🇯🇵",
                "salary": "¥160,000 – ¥200,000/month",
                "salary_bdt": "৳1,10,000 – ৳1,40,000",
                "type": "Manufacturing",
                "requirements": ["Age 18-35", "Basic fitness", "6-month training provided"],
                "visa": "Specified Skilled Worker (SSW)",
                "deadline": "2025-09-30",
                "seats": 20,
                "status": "open",
            },
            {
                "title": "Construction Worker",
                "country": "Japan",
                "flag": "🇯🇵",
                "salary": "¥170,000 – ¥220,000/month",
                "salary_bdt": "৳1,20,000 – ৳1,55,000",
                "type": "Construction",
                "requirements": ["Age 20-38", "Physical fitness", "Experience preferred"],
                "visa": "Specified Skilled Worker (SSW)",
                "deadline": "2025-08-15",
                "seats": 15,
                "status": "open",
            },
            {
                "title": "Care Worker (Caregiver)",
                "country": "Japan",
                "flag": "🇯🇵",
                "salary": "¥180,000 – ¥230,000/month",
                "salary_bdt": "৳1,27,000 – ৳1,62,000",
                "type": "Healthcare",
                "requirements": ["Age 18-40", "Japanese N4 preferred", "Training provided"],
                "visa": "Specified Skilled Worker (SSW)",
                "deadline": "2025-10-01",
                "seats": 10,
                "status": "open",
            },
            {
                "title": "General Labor",
                "country": "Saudi Arabia",
                "flag": "🇸🇦",
                "salary": "SAR 1,200 – 1,800/month",
                "salary_bdt": "৳35,000 – ৳52,000",
                "type": "General Labor",
                "requirements": ["Age 20-45", "Good health", "Willing to relocate"],
                "visa": "Work Visa",
                "deadline": "2025-07-31",
                "seats": 30,
                "status": "open",
            },
            {
                "title": "Civil Engineer",
                "country": "UAE",
                "flag": "🇦🇪",
                "salary": "AED 5,000 – 8,000/month",
                "salary_bdt": "৳1,48,000 – ৳2,37,000",
                "type": "Engineering",
                "requirements": ["B.Sc. in Civil Engineering", "3+ years experience", "English fluency"],
                "visa": "Employment Visa",
                "deadline": "2025-08-31",
                "seats": 5,
                "status": "open",
            },
            {
                "title": "Electrician",
                "country": "Qatar",
                "flag": "🇶🇦",
                "salary": "QAR 2,500 – 3,500/month",
                "salary_bdt": "৳72,000 – ৳1,01,000",
                "type": "Technical",
                "requirements": ["Electrical diploma/certificate", "2+ years experience"],
                "visa": "Work Visa",
                "deadline": "2025-09-15",
                "seats": 12,
                "status": "open",
            },
            {
                "title": "Warehouse Operator",
                "country": "Germany",
                "flag": "🇩🇪",
                "salary": "€2,200 – 2,800/month",
                "salary_bdt": "৳2,62,000 – ৳3,34,000",
                "type": "Logistics",
                "requirements": ["Age 22-40", "Basic German or English", "Forklift license a plus"],
                "visa": "EU Work Visa",
                "deadline": "2025-10-30",
                "seats": 8,
                "status": "open",
            },
            {
                "title": "Truck Driver",
                "country": "Poland",
                "flag": "🇵🇱",
                "salary": "PLN 6,000 – 8,500/month",
                "salary_bdt": "৳1,68,000 – ৳2,38,000",
                "type": "Transport",
                "requirements": ["Valid driving license (C/CE)", "2+ years experience", "Clean record"],
                "visa": "EU Work Visa",
                "deadline": "2025-08-20",
                "seats": 10,
                "status": "open",
            },
        ]
        mongo.db.jobs.insert_many(sample_jobs)

    if mongo.db.success_stories.count_documents({}) == 0:
        stories = [
            {
                "name": "Md. Rahim Uddin",
                "country": "Japan 🇯🇵",
                "job": "Factory Worker",
                "salary": "¥185,000/month",
                "story": "TalentHeart helped me get my dream job in Japan. The process was smooth and transparent. I'm now sending money home regularly.",
                "year": 2024,
                "image": "person1.jpg",
            },
            {
                "name": "Karim Hossain",
                "country": "UAE 🇦🇪",
                "job": "Civil Engineer",
                "salary": "AED 6,500/month",
                "story": "Professional team, honest guidance. Within 4 months I was working in Dubai. Best decision of my life!",
                "year": 2024,
                "image": "person2.jpg",
            },
            {
                "name": "Nusrat Jahan",
                "country": "Germany 🇩🇪",
                "job": "Warehouse Operator",
                "salary": "€2,500/month",
                "story": "As a woman, I was worried about working abroad. TalentHeart guided me every step and I feel safe and happy here.",
                "year": 2023,
                "image": "person3.jpg",
            },
        ]
        mongo.db.success_stories.insert_many(stories)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
