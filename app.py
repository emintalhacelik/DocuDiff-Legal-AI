import os
import pdfplumber
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, flash, session)
from flask_login import (LoginManager, login_user, logout_user,
                          login_required, current_user)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from config import GEMINI_API_KEY, SECRET_KEY, DATABASE_URL
from models import db, User, Analysis
from legal_ai import analyze_clause

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"]                     = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"]        = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"]             = 16 * 1024 * 1024   # 16 MB max upload
app.config["UPLOAD_FOLDER"]                  = os.path.join(os.path.dirname(__file__), "static", "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

bcrypt    = Bcrypt(app)
login_mgr = LoginManager(app)
login_mgr.login_view                 = "login"
login_mgr.login_message              = "Please sign in to access this page."
login_mgr.login_message_category     = "info"


@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ── Auth routes ────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm",  "")

        error = None
        if not username or not email or not password:
            error = "All fields are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.query.filter_by(email=email).first():
            error = "This email is already registered."
        elif User.query.filter_by(username=username).first():
            error = "This username is already taken."

        if error:
            return render_template("register.html", error=error,
                                   username=username, email=email)

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login", registered="1"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    registered = request.args.get("registered")

    if request.method == "POST":
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        return render_template("login.html", error="Invalid email address or password.",
                               email=email)

    return render_template("login.html", registered=registered)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ── Main app ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    history = []
    if current_user.is_authenticated:
        history = [a.to_dict() for a in current_user.analyses]
    return render_template("index.html", history=history)


# ── Analyze ────────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)

    clause_id    = (data.get("clause_id")    or "").strip() or "Clause_1"
    clause_title = (data.get("clause_title") or "").strip() or "Contract Clause"
    clause_text  = (data.get("clause_text")  or "").strip()
    language     = (data.get("language")     or "en").strip().lower()
    stance       = (data.get("stance")       or "balanced").strip().lower()

    if not clause_text:
        return jsonify({"error": "Clause text is required."}), 400

    try:
        result = analyze_clause(clause_id, clause_title, clause_text, language=language, stance=stance)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    # Save to DB if user is logged in
    if current_user.is_authenticated:
        analysis = Analysis(
            user_id               = current_user.id,
            clause_id             = clause_id,
            clause_title          = clause_title,
            clause_text           = clause_text,
            risk_level            = result.get("risk_level"),
            risk_score            = result.get("risk_score"),
            risk_category         = result.get("risk_category"),
            key_issue             = result.get("key_issue"),
            plain_english_summary = result.get("plain_english_summary"),
            actionable_advice     = result.get("actionable_advice"),
            suggested_revision    = result.get("suggested_revision"),
        )
        db.session.add(analysis)
        db.session.commit()
        result["analysis_id"] = analysis.id
        result["saved"]       = True
    else:
        result["saved"] = False

    return jsonify(result)


# ── PDF upload ─────────────────────────────────────────────────────────────
@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t.strip())
        extracted = "\n\n".join(text_parts).strip()
    except Exception as e:
        return jsonify({"error": f"Could not read PDF: {str(e)}"}), 500
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass

    if not extracted:
        return jsonify({"error": "PDF appears to be empty or image-only (no extractable text)."}), 400

    return jsonify({"text": extracted, "pages": len(text_parts)})


# ── History API ────────────────────────────────────────────────────────────
@app.route("/api/history")
@login_required
def api_history():
    analyses = [a.to_dict() for a in current_user.analyses]
    return jsonify(analyses)


@app.route("/api/analysis/<int:analysis_id>")
@login_required
def api_analysis(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first_or_404()
    return jsonify(analysis.to_dict())


@app.route("/api/analysis/<int:analysis_id>", methods=["DELETE"])
@login_required
def delete_analysis(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({"deleted": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
