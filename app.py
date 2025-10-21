from flask import Flask, render_template, request, redirect, session, send_file
from utils.db import get_connection
from utils.geoip import get_location
from utils.export_excel import export_to_excel
from datetime import date
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM batches")
    batches = cursor.fetchall()

    message = None

    if request.method == "POST":
        student_name = request.form["student_name"]
        batch_id = request.form["batch"]
        ip_address = request.remote_addr
        location = get_location(ip_address)

        cursor.execute("""
            SELECT * FROM attendance
            WHERE student_name=%s AND batch_id=%s AND date=%s
        """, (student_name, batch_id, date.today()))
        existing = cursor.fetchone()

        if existing:
            message = f"⚠️ {student_name} already checked in today!"
        else:
            cursor.execute("""
                INSERT INTO attendance (student_name, batch_id, ip_address, location)
                VALUES (%s, %s, %s, %s)
            """, (student_name, batch_id, ip_address, location))
            conn.commit()
            message = f"✅ Attendance recorded for {student_name} ({location})"

    conn.close()
    return render_template("index.html", batches=batches, message=message)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/admin")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, b.batch_name FROM attendance a
        JOIN batches b ON a.batch_id = b.id
        ORDER BY a.date DESC, a.checkin_time DESC
    """)
    records = cursor.fetchall()
    cursor.execute("""
        SELECT date, COUNT(DISTINCT student_name) as present_count
        FROM attendance
        GROUP BY date
        ORDER BY date DESC
    """)
    summary = cursor.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", records=records, summary=summary)

@app.route("/export")
def export_excel_route():
    if "admin" not in session:
        return redirect("/admin")

    period = request.args.get("period", "all")  # options: all, weekly, monthly

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.*, b.batch_name 
        FROM attendance a
        JOIN batches b ON a.batch_id = b.id
    """

    today = date.today()

    if period == "weekly":
        # Start of the week (Monday)
        start_week = today - timedelta(days=today.weekday())
        query += " WHERE date >= %s"
        cursor.execute(query, (start_week,))
    elif period == "monthly":
        # Start of the month
        start_month = today.replace(day=1)
        query += " WHERE date >= %s"
        cursor.execute(query, (start_month,))
    else:
        cursor.execute(query)

    records = cursor.fetchall()
    conn.close()

    file = export_to_excel(records, filename=f"attendance_{period}.xlsx")
    return send_file(file, as_attachment=True)

@app.route("/batches", methods=["GET", "POST"])
def manage_batches():
    if "admin" not in session:
        return redirect("/admin")
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        batch_name = request.form["batch_name"]
        cursor.execute("INSERT INTO batches (batch_name) VALUES (%s)", (batch_name,))
        conn.commit()
    cursor.execute("SELECT * FROM batches")
    batches = cursor.fetchall()
    conn.close()
    return render_template("batches.html", batches=batches)

@app.route("/topics", methods=["GET", "POST"])
def manage_topics():
    if "admin" not in session:
        return redirect("/admin")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM batches")
    batches = cursor.fetchall()
    if request.method == "POST":
        batch_id = request.form["batch"]
        teacher_name = request.form["teacher_name"]
        topic = request.form["topic"]
        cursor.execute("""
            INSERT INTO topics (batch_id, teacher_name, topic)
            VALUES (%s, %s, %s)
        """, (batch_id, teacher_name, topic))
        conn.commit()
    cursor.execute("""
        SELECT t.*, b.batch_name FROM topics t
        JOIN batches b ON t.batch_id = b.id
        ORDER BY t.date DESC
    """)
    topics = cursor.fetchall()
    conn.close()
    return render_template("topics.html", batches=batches, topics=topics)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
