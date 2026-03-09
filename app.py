from flask import Flask, render_template, jsonify, request, session
import json, uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cgpa-secret-key-2025"

# ── GRADE SCALES ─────────────────────────────────────────────────────────────
GRADE_SCALES = {
    "10_point": {
        "label": "10-Point Scale (India/Anna University)",
        "grades": {
            "O":  {"points": 10, "range": "91–100", "desc": "Outstanding"},
            "A+": {"points": 9,  "range": "81–90",  "desc": "Excellent"},
            "A":  {"points": 8,  "range": "71–80",  "desc": "Very Good"},
            "B+": {"points": 7,  "range": "61–70",  "desc": "Good"},
            "B":  {"points": 6,  "range": "51–60",  "desc": "Above Average"},
            "C":  {"points": 5,  "range": "41–50",  "desc": "Average"},
            "U":  {"points": 0,  "range": "0–40",   "desc": "Fail"},
        }
    },
    "4_point": {
        "label": "4-Point Scale (US System)",
        "grades": {
            "A":  {"points": 4.0, "range": "90–100", "desc": "Excellent"},
            "A-": {"points": 3.7, "range": "85–89",  "desc": "Very Good"},
            "B+": {"points": 3.3, "range": "80–84",  "desc": "Good"},
            "B":  {"points": 3.0, "range": "75–79",  "desc": "Above Average"},
            "B-": {"points": 2.7, "range": "70–74",  "desc": "Adequate"},
            "C+": {"points": 2.3, "range": "65–69",  "desc": "Fair"},
            "C":  {"points": 2.0, "range": "60–64",  "desc": "Satisfactory"},
            "D":  {"points": 1.0, "range": "50–59",  "desc": "Poor"},
            "F":  {"points": 0.0, "range": "0–49",   "desc": "Fail"},
        }
    }
}

# ── CGPA DESCRIPTIONS ─────────────────────────────────────────────────────────
def cgpa_description(cgpa, scale):
    if scale == "10_point":
        if cgpa >= 9.0:   return ("Outstanding Academic Excellence", "🏆", "#f5c842", "You are among the top academic performers. This CGPA reflects exceptional dedication, deep subject mastery, and consistent performance. Graduate schools and top employers actively seek candidates at this level.")
        if cgpa >= 8.0:   return ("Excellent Performance", "⭐", "#4ade80", "A strong indicator of academic competence and hard work. This CGPA opens doors to premier institutions for higher studies and competitive corporate placements across all sectors.")
        if cgpa >= 7.0:   return ("Good Academic Standing", "✅", "#60a5fa", "You have a solid academic foundation. This CGPA qualifies for most postgraduate programs and is viewed favorably by mid-to-large employers for entry-level positions.")
        if cgpa >= 6.0:   return ("Satisfactory Progress", "📘", "#a78bfa", "You have met the academic requirements adequately. Consider focusing on weaker subjects to push into the Good or Excellent tier for better opportunities ahead.")
        if cgpa >= 5.0:   return ("Needs Improvement", "⚠️", "#fb923c", "You are passing but have significant room to grow. Identify challenging subjects and seek additional support. A consistent improvement plan can make a meaningful difference.")
        return               ("Critical — Requires Immediate Attention", "🚨", "#f87171", "Your CGPA is below the passing threshold in many programs. Please consult your academic advisor immediately and develop a remediation strategy.")
    else:  # 4-point
        if cgpa >= 3.7:   return ("Dean's List — Summa Cum Laude", "🏆", "#f5c842", "An exceptional GPA placing you in the highest academic honor tier. This level of achievement is recognized by all graduate programs and top employers worldwide.")
        if cgpa >= 3.3:   return ("Magna Cum Laude Honors", "⭐", "#4ade80", "A highly competitive GPA that demonstrates consistent excellence. You are well-positioned for selective graduate school admissions and honors program recognition.")
        if cgpa >= 3.0:   return ("Cum Laude — Good Standing", "✅", "#60a5fa", "A solid GPA above the industry-standard 3.0 benchmark. Most competitive employers and graduate programs accept candidates at this level without hesitation.")
        if cgpa >= 2.0:   return ("Satisfactory Standing", "📘", "#a78bfa", "You are meeting minimum academic standards. Focus on strengthening your weaker courses and maintaining consistency to improve competitiveness.")
        return               ("Academic Probation Risk", "🚨", "#f87171", "Your GPA is approaching or below probation thresholds. Please seek tutoring, academic counseling, and develop a clear improvement plan immediately.")

# ── SUBJECT PRESETS ──────────────────────────────────────────────────────────
PRESETS = {
    "cse": {
        "name": "Computer Science & Engineering",
        "subjects": [
            {"name": "Data Structures & Algorithms", "credits": 4, "desc": "Core CS: arrays, trees, graphs, sorting, searching algorithms and complexity analysis."},
            {"name": "Database Management Systems", "credits": 3, "desc": "Relational databases, SQL, normalization, transactions, and query optimization."},
            {"name": "Operating Systems",            "credits": 4, "desc": "Process management, memory management, file systems, and synchronization."},
            {"name": "Computer Networks",            "credits": 3, "desc": "OSI model, TCP/IP, routing protocols, network security fundamentals."},
            {"name": "Software Engineering",         "credits": 3, "desc": "SDLC models, requirements engineering, design patterns, and testing strategies."},
            {"name": "Artificial Intelligence",      "credits": 4, "desc": "Search algorithms, knowledge representation, machine learning basics, neural networks."},
            {"name": "Web Technologies",             "credits": 3, "desc": "HTML/CSS/JS, REST APIs, frameworks, and modern web development practices."},
            {"name": "Mathematics for CS",           "credits": 4, "desc": "Discrete mathematics, probability, linear algebra, and calculus for computing."},
        ]
    },
    "mech": {
        "name": "Mechanical Engineering",
        "subjects": [
            {"name": "Engineering Mechanics",        "credits": 4, "desc": "Statics and dynamics: forces, moments, equilibrium, kinematics and Newton's laws."},
            {"name": "Thermodynamics",               "credits": 4, "desc": "Laws of thermodynamics, heat engines, refrigeration, and entropy."},
            {"name": "Fluid Mechanics",              "credits": 3, "desc": "Fluid statics, Bernoulli's equation, viscous flow, and turbomachinery basics."},
            {"name": "Strength of Materials",        "credits": 4, "desc": "Stress, strain, beams, columns, torsion, and failure theories."},
            {"name": "Machine Design",               "credits": 3, "desc": "Design of shafts, gears, bearings, springs, and pressure vessels."},
            {"name": "Manufacturing Processes",      "credits": 3, "desc": "Casting, welding, machining, forming processes, and CNC fundamentals."},
            {"name": "Heat Transfer",                "credits": 3, "desc": "Conduction, convection, radiation, and heat exchangers."},
            {"name": "Control Systems",              "credits": 3, "desc": "Open/closed loop systems, Laplace transforms, PID controllers, stability analysis."},
        ]
    },
    "civil": {
        "name": "Civil Engineering",
        "subjects": [
            {"name": "Structural Analysis",          "credits": 4, "desc": "Determinate and indeterminate structures, trusses, frames, and influence lines."},
            {"name": "Concrete Technology",          "credits": 3, "desc": "Mix design, properties of concrete, admixtures, and durability."},
            {"name": "Geotechnical Engineering",     "credits": 4, "desc": "Soil classification, compaction, consolidation, shear strength, and foundations."},
            {"name": "Hydraulics & Hydrology",       "credits": 3, "desc": "Open channel flow, pipe networks, rainfall-runoff analysis."},
            {"name": "Transportation Engineering",   "credits": 3, "desc": "Highway design, traffic engineering, pavement materials and design."},
            {"name": "Environmental Engineering",    "credits": 3, "desc": "Water treatment, sewage treatment, solid waste management, air pollution."},
            {"name": "Surveying",                    "credits": 3, "desc": "Plane surveying, GPS, remote sensing, GIS applications."},
            {"name": "Construction Management",      "credits": 3, "desc": "Project planning, scheduling (CPM/PERT), cost estimation, and contracts."},
        ]
    }
}

@app.route("/")
def index():
    return render_template("index.html", grade_scales=GRADE_SCALES, presets=PRESETS)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    subjects = data.get("subjects", [])
    scale = data.get("scale", "10_point")
    grade_map = GRADE_SCALES[scale]["grades"]

    results = []
    total_credits = 0
    total_points = 0

    for s in subjects:
        grade = s.get("grade", "")
        credits = float(s.get("credits", 0))
        gp = grade_map.get(grade, {}).get("points", 0)
        weighted = gp * credits
        total_credits += credits
        total_points += weighted
        results.append({
            "name": s.get("name", "Subject"),
            "credits": credits,
            "grade": grade,
            "grade_points": gp,
            "weighted_points": weighted,
            "desc": s.get("desc", ""),
            "grade_desc": grade_map.get(grade, {}).get("desc", ""),
        })

    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    title, icon, color, description = cgpa_description(cgpa, scale)

    return jsonify({
        "cgpa": cgpa,
        "total_credits": total_credits,
        "total_points": round(total_points, 2),
        "title": title,
        "icon": icon,
        "color": color,
        "description": description,
        "subjects": results,
        "scale": GRADE_SCALES[scale]["label"],
        "percentage": round((cgpa / (10 if scale == "10_point" else 4)) * 100, 1),
    })

@app.route("/api/presets")
def get_presets():
    return jsonify(PRESETS)

@app.route("/api/grade_scales")
def get_scales():
    return jsonify(GRADE_SCALES)

if __name__ == "__main__":
    print("\n" + "═"*50)
    print("  🎓  GradeScope — CGPA Calculator")
    print("═"*50)
    print("  🌐  http://localhost:5000")
    print("  🛑  Ctrl+C to stop")
    print("═"*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
