from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, make_response
from werkzeug.utils import secure_filename
from pathlib import Path
import sqlite3, os, uuid

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "uploads"
DB = BASE / "patients.db"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "change-me-123")
SITE_URL = "https://web-production-01e26.up.railway.app"

ALLOWED = {"pdf", "jpg", "jpeg", "png", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
WA1, WA2 = "916000812544", "918448739809"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT NOT NULL, age INTEGER,
        gender TEXT, diagnosis TEXT NOT NULL, country TEXT NOT NULL, phone TEXT NOT NULL,
        email TEXT, message TEXT, language TEXT DEFAULT 'en', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.execute("""CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL,
        original_name TEXT NOT NULL, stored_name TEXT NOT NULL,
        FOREIGN KEY(patient_id) REFERENCES patients(id))""")
    con.commit(); con.close()

def allowed(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED

def get_lang():
    value = request.args.get("lang") or session.get("lang") or "en"
    if value not in {"en", "ar"}: value = "en"
    session["lang"] = value
    return value

@app.context_processor
def globals():
    return {"wa1": WA1, "wa2": WA2, "site_url": SITE_URL, "current_lang": session.get("lang","en")}

@app.route("/", methods=["GET","POST"])
def home():
    language = get_lang()
    if request.method == "POST":
        name = request.form.get("patient_name","").strip()
        age = request.form.get("age","").strip()
        gender = request.form.get("gender","").strip()
        diagnosis = request.form.get("diagnosis","").strip()
        country = request.form.get("country","").strip()
        phone = request.form.get("phone","").strip()
        email = request.form.get("email","").strip()
        message = request.form.get("message","").strip()
        uploads = request.files.getlist("reports")
        if not name or not diagnosis or not country or not phone:
            flash("Please fill all required fields." if language=="en" else "يرجى تعبئة جميع الحقول المطلوبة.","error")
            return redirect(url_for("home",lang=language)+"#enquiry")
        valid = [f for f in uploads if f and f.filename]
        if not valid:
            flash("Please upload at least one medical report or prescription." if language=="en" else "يرجى رفع تقرير طبي أو وصفة طبية واحدة على الأقل.","error")
            return redirect(url_for("home",lang=language)+"#enquiry")
        if any(not allowed(f.filename) for f in valid):
            flash("Only PDF, JPG, JPEG, PNG and WEBP files are allowed." if language=="en" else "يسمح فقط بملفات PDF وJPG وJPEG وPNG وWEBP.","error")
            return redirect(url_for("home",lang=language)+"#enquiry")
        con = db()
        cur = con.execute("""INSERT INTO patients
            (patient_name,age,gender,diagnosis,country,phone,email,message,language)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (name, int(age) if age.isdigit() else None, gender, diagnosis, country, phone, email, message, language))
        pid = cur.lastrowid
        patient_dir = UPLOAD_DIR / str(pid); patient_dir.mkdir(exist_ok=True)
        for f in valid:
            clean = secure_filename(f.filename); ext = Path(clean).suffix.lower()
            stored = f"{uuid.uuid4().hex}{ext}"; f.save(patient_dir / stored)
            con.execute("INSERT INTO documents(patient_id,original_name,stored_name) VALUES(?,?,?)",(pid,f.filename,stored))
        con.commit(); con.close()
        return render_template("success.html", name=name, lang=language)
    return render_template("home.html", lang=language)
@app.route("/medical-treatment-in-india")
def medical_treatment_india():
    language = get_lang()
    return render_template("medical_treatment_india.html", lang=language)

@app.route("/admin/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("username")==ADMIN_USER and request.form.get("password")==ADMIN_PASS:
            session["admin"]=True; return redirect(url_for("dashboard"))
        flash("Invalid username or password.","error")
    return render_template("login.html")

@app.route("/admin/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/admin")
def dashboard():
    if not session.get("admin"): return redirect(url_for("login"))
    q=request.args.get("q","").strip(); con=db()
    if q:
        rows=con.execute("""SELECT * FROM patients WHERE patient_name LIKE ? OR phone LIKE ? OR country LIKE ? ORDER BY id DESC""",(f"%{q}%",f"%{q}%",f"%{q}%")).fetchall()
    else: rows=con.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    con.close(); return render_template("dashboard.html",patients=rows,q=q)

@app.route("/admin/patient/<int:pid>")
def patient(pid):
    if not session.get("admin"): return redirect(url_for("login"))
    con=db(); p=con.execute("SELECT * FROM patients WHERE id=?",(pid,)).fetchone()
    docs=con.execute("SELECT * FROM documents WHERE patient_id=?",(pid,)).fetchall(); con.close()
    if not p: return "Patient not found",404
    return render_template("patient.html",p=p,docs=docs)

@app.route("/admin/file/<int:pid>/<path:filename>")
def file(pid,filename):
    if not session.get("admin"): return redirect(url_for("login"))
    return send_from_directory(UPLOAD_DIR/str(pid),secure_filename(filename),as_attachment=False)

@app.route("/google4a4df61860a1960.html")
def google_verification():
    return "google-site-verification: google4a4df61860a1960.html", 200, {"Content-Type": "text/plain"}

@app.route("/sitemap.xml")
def sitemap():
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f"<url><loc>{SITE_URL}/?lang=en</loc></url>"
    xml += f"<url><loc>{SITE_URL}/?lang=ar</loc></url>"
    xml += f"<url><loc>{SITE_URL}/medical-treatment-in-india?lang=en</loc></url>"
    xml += f"<url><loc>{SITE_URL}/medical-treatment-in-india?lang=ar</loc></url>"
    xml += "</urlset>"
    return make_response(xml,200,{"Content-Type":"application/xml"})

@app.errorhandler(413)
def too_large(e):
    return render_template("error.html",message="File upload is too large. Maximum total request size is 25 MB."),413

init_db()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
