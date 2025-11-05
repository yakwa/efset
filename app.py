import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import random

from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash

# PDF and QR code
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "questions.json"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


def create_app():
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    # In-memory verification registry for QR codes
    app.config["VERIFICATION_REGISTRY"] = {}

    @app.context_processor
    def inject_globals():
        return {
            "app_name": "Conseilux English Training",
        }

    def load_questions() -> List[Dict[str, Any]]:
        if not DATA_PATH.exists():
            return []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def questions_by_section(section: str) -> List[Dict[str, Any]]:
        return [q for q in load_questions() if q.get("section") == section]

    def cefr_from_score(score: int) -> str:
        # 0-5 → A1; 6-10 → A2; 11-15 → B1; 16-20 → B2; 21+ → C1/C2
        if score <= 5:
            return "A1"
        if score <= 10:
            return "A2"
        if score <= 15:
            return "B1"
        if score <= 20:
            return "B2"
        return "C1/C2"

    def ensure_session():
        session.setdefault("name", "")
        session.setdefault("settings", {"timer_enabled": False, "niveau1_timer": 15, "niveau2_timer": 15, "niveau3_timer": 15})
        session.setdefault("answers", {"Niveau 1": {}, "Niveau 2": {}, "Niveau 3": {}})

    @app.route("/", methods=["GET", "POST"])
    def index():
        ensure_session()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            timer_enabled = request.form.get("timer_enabled") == "on"
            niveau1_timer = int(request.form.get("niveau1_timer", 15))
            niveau2_timer = int(request.form.get("niveau2_timer", 15))
            niveau3_timer = int(request.form.get("niveau3_timer", 15))

            if not name:
                flash("Veuillez entrer votre nom.", "error")
                return render_template("index.html")

            session["name"] = name
            session["settings"] = {
                "timer_enabled": timer_enabled,
                "niveau1_timer": max(1, niveau1_timer),
                "niveau2_timer": max(1, niveau2_timer),
                "niveau3_timer": max(1, niveau3_timer),
            }
            session["answers"] = {"Niveau 1": {}, "Niveau 2": {}, "Niveau 3": {}}

            # Build sampled set and randomized order per section + shuffled options (simulating AI selection)
            order: Dict[str, List[int]] = {}
            sampled: Dict[str, List[int]] = {}
            options_order: Dict[str, Dict[str, List[str]]] = {"Niveau 1": {}, "Niveau 2": {}, "Niveau 3": {}}
            seen: Dict[str, List[int]] = session.get("seen", {"Niveau 1": [], "Niveau 2": [], "Niveau 3": []})

            for sec in ("Niveau 1", "Niveau 2", "Niveau 3"):
                qs = questions_by_section(sec)
                all_indices = list(range(len(qs)))
                sample_k = min(10, len(all_indices))

                # Prefer sampling from unseen questions; reset if not enough remain
                seen_set = set(seen.get(sec, []))
                remaining = [i for i in all_indices if i not in seen_set]
                if len(remaining) < sample_k:
                    # Reset cycle to allow fresh rotation
                    seen[sec] = []
                    remaining = all_indices

                sampled_indices = random.sample(remaining, sample_k) if sample_k > 0 else []
                # Update seen pool
                seen[sec] = list(set(seen.get(sec, [])) | set(sampled_indices))
                sampled[sec] = sampled_indices
                order_list = list(sampled_indices)
                random.shuffle(order_list)
                order[sec] = order_list

                # Precompute a shuffled options list for each absolute question index
                for idx, q in enumerate(qs):
                    opts = list(q.get("options", []))
                    random.shuffle(opts)
                    options_order[sec][str(idx)] = opts

            session["order"] = order
            session["sampled"] = sampled
            session["options_order"] = options_order
            session["seen"] = seen
            session["started_at"] = datetime.utcnow().isoformat()
            return redirect(url_for("section", section="Niveau 1", q=0))
        return render_template("index.html")

    @app.route("/section/<section>")
    def section(section: str):
        ensure_session()
        if section not in ("Niveau 1", "Niveau 2", "Niveau 3"):
            return redirect(url_for("index"))

        q_index = int(request.args.get("q", 0))
        qs = questions_by_section(section)
        sampled_indices = session.get("sampled", {}).get(section)
        if not sampled_indices:
            sampled_indices = list(range(len(qs)))
        total = len(sampled_indices)
        if total == 0:
            flash(f"Pas de questions pour la section {section}.", "error")
            return redirect(url_for("index"))

        if q_index < 0:
            q_index = 0
        if q_index >= total:
            # Move to next section or results
            if section == "Niveau 1":
                return redirect(url_for("section", section="Niveau 2", q=0))
            elif section == "Niveau 2":
                return redirect(url_for("section", section="Niveau 3", q=0))
            return redirect(url_for("results"))

        # Determine absolute question index based on randomized order (fallback to identity)
        order = session.get("order", {}).get(section)
        if not order or len(order) != total:
            order = list(sampled_indices)
        abs_idx = order[q_index]

        question = qs[abs_idx]
        progress_text = f"Question {q_index + 1} sur {total}"

        # Preselected answer from session if any
        selected = session["answers"].get(section, {}).get(str(abs_idx))

        # Shuffled options for this absolute question index
        options_map = session.get("options_order", {}).get(section, {})
        options_shuffled = options_map.get(str(abs_idx), list(question.get("options", [])))

        # Timer seconds based on section
        sec_settings = session.get("settings", {})
        timer_enabled = sec_settings.get("timer_enabled", False)
        timer_key = "niveau1_timer" if section == "Niveau 1" else ("niveau2_timer" if section == "Niveau 2" else "niveau3_timer")
        timer_seconds = sec_settings.get(timer_key, 15) * 60

        # No audio for new system
        audio_exists = False

        return render_template(
            "section.html",
            section=section,
            question=question,
            q_index=q_index,
            total=total,
            progress_text=progress_text,
            selected=selected,
            options=options_shuffled,
            timer_enabled=timer_enabled,
            timer_seconds=timer_seconds,
            audio_exists=audio_exists,
        )

    @app.post("/answer/<section>/<int:q_index>")
    def submit_answer(section: str, q_index: int):
        ensure_session()
        if section not in ("Niveau 1", "Niveau 2", "Niveau 3"):
            return redirect(url_for("index"))

        choice = request.form.get("choice")
        # Save answer even if None (skipped)
        answers = session.get("answers", {})
        answers.setdefault(section, {})
        # Map to absolute index based on randomized order within sampled set
        qs = questions_by_section(section)
        sampled_indices = session.get("sampled", {}).get(section, list(range(len(qs))))
        order = session.get("order", {}).get(section, list(sampled_indices))
        abs_idx = order[q_index] if 0 <= q_index < len(order) else q_index
        answers[section][str(abs_idx)] = choice
        session["answers"] = answers

        next_idx = q_index + 1
        return redirect(url_for("section", section=section, q=next_idx))

    def compute_score() -> Dict[str, Any]:
        qs_niveau1 = questions_by_section("Niveau 1")
        qs_niveau2 = questions_by_section("Niveau 2")
        qs_niveau3 = questions_by_section("Niveau 3")

        ans = session.get("answers", {"Niveau 1": {}, "Niveau 2": {}, "Niveau 3": {}})
        sampled = session.get("sampled", {})
        sampled_niveau1 = sampled.get("Niveau 1", list(range(len(qs_niveau1))))
        sampled_niveau2 = sampled.get("Niveau 2", list(range(len(qs_niveau2))))
        sampled_niveau3 = sampled.get("Niveau 3", list(range(len(qs_niveau3))))

        score_niveau1 = 0
        score_niveau2 = 0
        score_niveau3 = 0

        for i in sampled_niveau1:
            q = qs_niveau1[i]
            if ans.get("Niveau 1", {}).get(str(i)) == q.get("answer"):
                score_niveau1 += 1
        for i in sampled_niveau2:
            q = qs_niveau2[i]
            if ans.get("Niveau 2", {}).get(str(i)) == q.get("answer"):
                score_niveau2 += 1
        for i in sampled_niveau3:
            q = qs_niveau3[i]
            if ans.get("Niveau 3", {}).get(str(i)) == q.get("answer"):
                score_niveau3 += 1

        total_score = score_niveau1 + score_niveau2 + score_niveau3
        total_questions = len(sampled_niveau1) + len(sampled_niveau2) + len(sampled_niveau3)
        level = cefr_from_score(total_score)
        return {
            "score_niveau1": score_niveau1,
            "score_niveau2": score_niveau2,
            "score_niveau3": score_niveau3,
            "total_score": total_score,
            "total_questions": total_questions,
            "level": level,
        }

    @app.get("/results")
    def results():
        ensure_session()
        summary = compute_score()
        return render_template("results.html", summary=summary)

    @app.post("/certificate")
    def certificate():
        ensure_session()
        name = session.get("name", "Participant")
        summary = compute_score()
        verify_code = str(uuid.uuid4())

        # Register verification
        app.config["VERIFICATION_REGISTRY"][verify_code] = {
            "name": name,
            "summary": summary,
            "issued_at": datetime.utcnow().isoformat(),
        }

        # Create PDF in memory
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        
        # Register standard fonts to avoid KeyError
        try:
            from reportlab.pdfbase.pdfmetrics import registerFont
            from reportlab.pdfbase.ttfonts import TTFont
            # Standard fonts are built-in, just need to ensure they're available
        except:
            pass

        # Background - Orange border
        c.setStrokeColor(colors.HexColor('#ff8c42'))
        c.setLineWidth(8)
        c.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)
        
        # Inner border - Blue
        c.setStrokeColor(colors.HexColor('#1e3a8a'))
        c.setLineWidth(2)
        c.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)

        # Header with logo
        logo_path = STATIC_DIR / "img" / "ChatGPT Image 28 oct. 2025, 13_31_01.png"
        if logo_path.exists():
            try:
                c.drawImage(ImageReader(str(logo_path)), width/2 - 50, height - 140, width=100, height=100, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"Logo error: {e}")

        # Title
        c.setFont("Times-Bold", 32)
        c.setFillColor(colors.HexColor('#ff8c42'))
        c.drawCentredString(width / 2, height - 170, "CERTIFICATE OF ACHIEVEMENT")
        
        # Subtitle
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#1e3a8a'))
        c.drawCentredString(width / 2, height - 195, "Conseilux English Training")

        # Decorative line
        c.setStrokeColor(colors.HexColor('#ff8c42'))
        c.setLineWidth(2)
        c.line(150, height - 210, width - 150, height - 210)

        # "This certifies that"
        c.setFont("Times-Italic", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 240, "This certifies that")

        # Name (large and centered)
        c.setFont("Times-Bold", 28)
        c.setFillColor(colors.HexColor('#1e3a8a'))
        c.drawCentredString(width / 2, height - 280, name)

        # Decorative line under name
        c.setStrokeColor(colors.HexColor('#ff8c42'))
        c.setLineWidth(1)
        c.line(width/2 - 150, height - 290, width/2 + 150, height - 290)

        # Achievement text
        c.setFont("Helvetica", 13)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 320, "has successfully completed the English Proficiency Test")
        c.drawCentredString(width / 2, height - 340, "and achieved the following results:")

        # Results box
        c.setStrokeColor(colors.HexColor('#ff8c42'))
        c.setFillColor(colors.HexColor('#fff3e6'))
        c.roundRect(100, height - 450, width - 200, 80, 10, stroke=1, fill=1)

        # Score and Level
        c.setFont("Times-Bold", 18)
        c.setFillColor(colors.HexColor('#1e3a8a'))
        score_text = f"Score: {summary['total_score']} / {summary['total_questions']}"
        c.drawCentredString(width / 2, height - 390, score_text)
        
        c.setFont("Times-Bold", 22)
        c.setFillColor(colors.HexColor('#ff8c42'))
        level_text = f"CEFR Level: {summary['level']}"
        c.drawCentredString(width / 2, height - 420, level_text)

        # Date and signature section
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        date_str = datetime.now().strftime('%B %d, %Y')
        c.drawString(100, height - 500, f"Date of Issue: {date_str}")
        
        # Signature line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(width - 250, height - 500, width - 100, height - 500)
        c.setFont("Times-Italic", 10)
        c.drawCentredString(width - 175, height - 515, "Authorized Signature")

        # Footer text
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#6c757d'))
        c.drawCentredString(width / 2, 80, "This certificate validates the English language proficiency assessment")
        c.drawCentredString(width / 2, 68, "completed through Conseilux English Training platform")

        # QR code for verification
        verify_url = url_for('verify', code=verify_code, _external=True)
        qr_img = qrcode.make(verify_url)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 50, 50, width=80, height=80)
        c.setFont("Helvetica", 8)
        c.drawString(50, 35, "Scan to verify")

        # Certificate ID
        c.setFont("Helvetica", 8)
        c.drawRightString(width - 50, 50, f"Certificate ID: {verify_code[:8].upper()}")

        # Created by
        c.setFont("Times-Italic", 8)
        c.setFillColor(colors.HexColor('#ff8c42'))
        c.drawRightString(width - 50, 35, "Created by Daven BANKA")

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        filename = f"certificat_{name.replace(' ', '_')}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

    @app.get("/verify/<code>")
    def verify(code: str):
        data = app.config["VERIFICATION_REGISTRY"].get(code)
        if not data:
            return render_template("verify.html", found=False, data=None)
        return render_template("verify.html", found=True, data=data)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/courses")
    def courses():
        return render_template("courses.html")

    @app.route("/blog")
    def blog():
        return render_template("blog.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


# For Render deployment
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
