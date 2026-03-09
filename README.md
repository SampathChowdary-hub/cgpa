# GradeScope — CGPA Calculator

A Python Flask web application for calculating CGPA across subjects, with interactive breakdowns, charts, grade descriptions, and support for both 10-point (Indian) and 4.0 (US) grading scales.

## Features
- 🎓 10-Point Scale (Anna University / India) & 4.0 GPA (US) support
- 📚 Add unlimited subjects with name, description, credits, and grade
- 📊 Visual bar chart breakdown per subject
- 🏆 Performance tier with detailed CGPA description
- 💡 Preset templates for CSE, Mechanical, and Civil Engineering
- 📱 Fully responsive design

## Run Locally

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Deploy to Render.com

### Option A — Blueprint (render.yaml)
1. Push this folder to a GitHub repository
2. Go to https://dashboard.render.com → **New → Blueprint**
3. Connect your GitHub repo — Render reads `render.yaml` automatically
4. Click **Apply** — your app goes live!

### Option B — Manual Web Service
1. Push to GitHub
2. Go to https://dashboard.render.com → **New → Web Service**
3. Connect your repo and configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Click **Create Web Service**

Live at: `https://gradescope-cgpa-calculator.onrender.com`

## Project Structure
```
cgpa/
├── app.py              # Flask app + CGPA logic + grade scales
├── templates/
│   └── index.html      # Full UI with charts and interactivity
├── requirements.txt    # Flask + Gunicorn
├── render.yaml         # Render blueprint
├── Procfile
└── README.md
```
