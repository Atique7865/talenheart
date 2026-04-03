# ❤️ TalentHeart Limited – Website

> **Bangladesh's trusted overseas recruitment agency** – Full-stack website with job listings, online applications, admin panel, salary calculator, and eligibility quiz.

![TalentHeart](https://img.shields.io/badge/TalentHeart-Recruitment-red) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green) ![Docker](https://img.shields.io/badge/Docker-Ready-blue) ![NGINX](https://img.shields.io/badge/NGINX-Alpine-brightgreen)

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Project Structure](#-project-structure)
4. [Local Development](#-local-development)
5. [Docker Build & Run](#-docker-build--run)
6. [Deploy on AWS EC2](#-deploy-on-aws-ec2-step-by-step)
7. [Admin Panel](#-admin-panel)
8. [Customization Guide](#-customization-guide)
9. [API Reference](#-api-reference)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏠 **Home Page** | Hero, stats, country cards, featured jobs, how-it-works |
| 💼 **Job Listings** | Dynamic jobs from MongoDB, filter by country & type |
| 📝 **Apply Form** | CV upload, auto-fill from job link, confirmation message |
| 🌍 **Work Abroad** | Detailed pages for Japan, Middle East, Europe |
| ⭐ **Success Stories** | Testimonials + video testimonial placeholders |
| 📞 **Contact Page** | Form, map, WhatsApp, phone, email |
| 🧮 **Salary Calculator** | Estimate salary by country/job/experience |
| 🎯 **Eligibility Quiz** | 5-question interactive eligibility checker |
| 🔐 **Admin Panel** | Dashboard, manage jobs, view & update applications |
| 💚 **WhatsApp Button** | Floating animated button on all pages |
| 📱 **Fully Responsive** | Mobile-first Bootstrap 5 design |

---

## 🔧 Tech Stack

```
Frontend  →  HTML5 + Bootstrap 5 + Vanilla JS
Backend   →  Python Flask 3.0
Database  →  MongoDB 7.0
Server    →  NGINX (Alpine)
Container →  Docker + Docker Compose
Cloud     →  AWS EC2
```

---

## 📂 Project Structure

```
talentheart/
├── frontend/
│   ├── index.html           ← Home page
│   ├── about.html           ← About Us
│   ├── work-abroad.html     ← Japan / Middle East / Europe
│   ├── jobs.html            ← Job listings (dynamic)
│   ├── apply.html           ← Application form
│   ├── success-stories.html ← Testimonials
│   ├── contact.html         ← Contact + map
│   ├── css/style.css        ← All custom styles
│   └── js/main.js           ← All JavaScript (jobs, quiz, calc)
│
├── backend/
│   ├── app.py               ← Flask app factory + data seed
│   ├── requirements.txt     ← Python dependencies
│   ├── .env.example         ← Environment variables template
│   ├── routes/
│   │   ├── jobs.py          ← CRUD API for jobs
│   │   ├── applications.py  ← Application submit & list
│   │   ├── admin.py         ← Admin login + dashboard
│   │   └── pages.py         ← Serve HTML pages
│   └── static/uploads/      ← CV file uploads
│
├── nginx/
│   └── nginx.conf           ← NGINX reverse proxy config
│
├── Dockerfile               ← Flask container build
├── docker-compose.yml       ← All services (mongo+flask+nginx)
└── .gitignore
```

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- MongoDB (local or Docker)
- Git

### Step 1 – Clone / Enter project
```bash
cd C:\talenheart
# or on Linux/Mac:
cd ~/talenheart
```

### Step 2 – Create virtual environment
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3 – Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 4 – Set environment variables
```bash
# Copy and edit the example
cp .env.example .env
# Edit .env with your values
```

### Step 5 – Start MongoDB locally
```bash
# Using Docker (easiest):
docker run -d -p 27017:27017 --name mongo mongo:7.0

# Or install MongoDB locally from mongodb.com
```

### Step 6 – Run Flask
```bash
python app.py
```

### Step 7 – Open browser
```
http://localhost:5000
```

---

## 🐳 Docker Build & Run

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Step 1 – Build images
```bash
cd C:\talenheart
docker compose build
```

### Step 2 – Start all services
```bash
docker compose up -d
```

### Step 3 – Check running containers
```bash
docker compose ps
```
You should see 3 containers running:
- `talentheart_mongo` – MongoDB
- `talentheart_flask` – Flask API
- `talentheart_nginx` – NGINX (port 80)

### Step 4 – Open browser
```
http://localhost
```

### Useful Docker Commands
```bash
# View logs
docker compose logs -f

# View Flask logs only
docker compose logs -f flask

# Stop everything
docker compose down

# Stop and delete data volumes
docker compose down -v

# Rebuild after code changes
docker compose build flask
docker compose up -d flask
```

---

## ☁️ Deploy on AWS EC2 (Step-by-Step)

### 🔑 STEP 1 – Create EC2 Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**
2. Choose:
   - **Name**: `talentheart-server`
   - **AMI**: `Ubuntu Server 22.04 LTS` (Free Tier eligible ✅)
   - **Instance type**: `t2.micro` (free tier) or `t3.small` (recommended)
   - **Key pair**: Create new → download `.pem` file → **SAVE IT SAFELY**
3. **Security Group** – Add these inbound rules:

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | My IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |

4. **Storage**: Minimum 20 GB
5. Click **Launch Instance**
6. Wait ~2 minutes for it to start

---

### 🔌 STEP 2 – Connect to EC2

```bash
# On your local machine (Linux/Mac/WSL):
chmod 400 your-key.pem

ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**Windows users** – Use PuTTY or Windows Terminal:
```powershell
ssh -i "C:\path\to\your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

---

### 🔧 STEP 3 – Install Docker on EC2

Run these commands on your EC2 instance:

```bash
# Update packages
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io

# Install Docker Compose
sudo apt-get install -y docker-compose-plugin

# Add ubuntu user to docker group (no sudo needed)
sudo usermod -aG docker ubuntu

# Apply group change
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

### 📦 STEP 4 – Upload Your Project to EC2

**Option A – Using Git (Recommended)**
```bash
# On EC2:
sudo apt-get install -y git

# Push to GitHub first, then:
git clone https://github.com/YOUR_USERNAME/talentheart.git
cd talentheart
```

**Option B – Using SCP (direct file copy)**
```bash
# On your local machine:
scp -i your-key.pem -r C:\talenheart ubuntu@YOUR_EC2_IP:~/talentheart
```

**Option C – Using rsync**
```bash
rsync -avz -e "ssh -i your-key.pem" C:/talenheart/ ubuntu@YOUR_EC2_IP:~/talentheart/
```

---

### 🔐 STEP 5 – Set Production Environment Variables

```bash
# On EC2, inside project directory:
cd ~/talentheart

# Create .env file
nano backend/.env
```

Add this content (replace values):
```env
MONGO_URI=mongodb://mongo:27017/talentheart
SECRET_KEY=your-very-long-random-secret-key-here
ADMIN_PASSWORD=your-strong-admin-password
FLASK_ENV=production
```

Save: `Ctrl+X` → `Y` → `Enter`

---

### 🚀 STEP 6 – Build and Start with Docker

```bash
cd ~/talentheart

# Build Docker images
docker compose build

# Start all services in background
docker compose up -d

# Check status
docker compose ps

# Watch logs (optional)
docker compose logs -f
```

---

### ✅ STEP 7 – Verify It's Running

```bash
# Test from EC2 itself
curl http://localhost

# Test from browser
# Open: http://YOUR_EC2_PUBLIC_IP
```

You should see the TalentHeart homepage! 🎉

---

### 🌐 STEP 8 – (Optional) Add Domain + HTTPS

#### A. Point your domain to EC2

1. Buy domain from Namecheap / GoDaddy / Cloudflare
2. Add **A Record**: `@` → `YOUR_EC2_IP`
3. Add **A Record**: `www` → `YOUR_EC2_IP`

#### B. Install Certbot for free SSL

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx container first
docker compose stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificate will be at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### C. Update nginx.conf for HTTPS

```nginx
# Replace contents of nginx/nginx.conf:

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /api/ {
        proxy_pass http://flask:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin {
        proxy_pass http://flask:5000;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://flask:5000;
        proxy_set_header Host $host;
    }
}
```

#### D. Update docker-compose.yml to mount certificates

```yaml
# In nginx service, add volume:
volumes:
  - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
  - ./frontend:/usr/share/nginx/html:ro
  - /etc/letsencrypt:/etc/letsencrypt:ro
# And add port 443:
ports:
  - "80:80"
  - "443:443"
```

#### E. Restart nginx

```bash
docker compose up -d nginx
```

---

### 🔄 STEP 9 – Auto-restart on Reboot

Docker Compose already uses `restart: unless-stopped`, but enable Docker to start on boot:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

### 📊 STEP 10 – Monitoring & Maintenance

```bash
# View all logs
docker compose logs -f

# Check disk space
df -h

# Check memory
free -m

# Check running containers
docker ps

# Update code and redeploy
git pull
docker compose build
docker compose up -d

# Backup MongoDB data
docker exec talentheart_mongo mongodump --out /data/backup
docker cp talentheart_mongo:/data/backup ./mongo-backup-$(date +%Y%m%d)
```

---

## 🔐 Admin Panel

Access the admin panel at:
```
http://YOUR_DOMAIN_OR_IP/admin
```

**Default password**: `admin123`  
⚠️ **Change this in your `.env` file before going live!**

### Admin Features:
- 📊 Dashboard with stats (total jobs, applications, pending, accepted)
- 📋 View all applications with status management
- 💼 View and delete job listings
- 🔍 Filter applications by status

### Change Admin Password:
```bash
# Edit .env file
nano backend/.env
# Change: ADMIN_PASSWORD=your-new-password
# Restart Flask:
docker compose restart flask
```

---

## 🎨 Customization Guide

### Update Company Info
Edit these files and replace placeholder content:

| What to Change | File | Find & Replace |
|---|---|---|
| Phone number | All HTML files | `+880 1XXX-XXXXXX` |
| WhatsApp number | All HTML files | `8801XXXXXXXXX` |
| Email | All HTML files | `info@talentheart.com.bd` |
| Address | `contact.html`, `index.html` | `Banani, Dhaka` |
| BOESL License | `index.html`, `about.html` | `#XXXX` |
| Social media links | `index.html`, `about.html` | `href="#"` |
| Google Maps | `contact.html` | Update iframe `src` |

### Add New Jobs (Admin Panel)
1. Go to `/admin`
2. Jobs can be deleted from the table
3. To ADD jobs via API:

```bash
curl -X POST http://localhost/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Welder",
    "country": "Germany",
    "flag": "🇩🇪",
    "salary": "€2,500/month",
    "salary_bdt": "৳2,98,000",
    "type": "Technical",
    "requirements": ["Welding certificate", "2+ years experience"],
    "visa": "EU Work Visa",
    "deadline": "2025-10-15",
    "seats": 5,
    "status": "open"
  }'
```

### Change Color Theme
Edit `frontend/css/style.css`:
```css
:root {
  --primary: #c0392b;      /* Main red color */
  --primary-dark: #96281b; /* Darker red */
  --primary-light: #e74c3c;/* Lighter red */
}
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/` | List all open jobs |
| GET | `/api/jobs/?country=Japan` | Filter by country |
| GET | `/api/jobs/?type=Manufacturing` | Filter by type |
| GET | `/api/jobs/<id>` | Get single job |
| POST | `/api/jobs/` | Create job |
| PUT | `/api/jobs/<id>` | Update job |
| DELETE | `/api/jobs/<id>` | Delete job |
| POST | `/api/applications/` | Submit application (multipart) |
| GET | `/api/applications/` | List applications |
| PUT | `/api/applications/<id>/status` | Update status |
| GET | `/admin` | Admin dashboard |
| POST | `/admin/login` | Admin login |

---

## 🛠️ Troubleshooting

### Port 80 already in use
```bash
sudo fuser -k 80/tcp
docker compose up -d
```

### MongoDB connection refused
```bash
docker compose logs mongo
docker compose restart mongo
```

### Flask container crashing
```bash
docker compose logs flask
# Look for Python errors
```

### Static files not loading
```bash
# Check nginx is running
docker compose ps nginx
docker compose logs nginx
```

### Permission denied on uploads
```bash
docker exec talentheart_flask chmod -R 755 /app/backend/static/uploads
```

---

## 📞 Support

- **WhatsApp**: +880 1XXX-XXXXXX
- **Email**: info@talentheart.com.bd
- **Website**: www.talentheart.com.bd

---

## 📄 License

© 2024 TalentHeart Limited. All rights reserved.

---

*Built with ❤️ for TalentHeart Limited*
