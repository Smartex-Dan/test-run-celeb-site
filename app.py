from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

# ================= HOME / LANDING =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= SIGNUP =================
@app.route("/signup")
def signup():
    return render_template("signup.html")

# ================= VIP APPLICATION =================
@app.route("/vip_page")
def vip():
    return render_template("vip_page.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        if not email or not email.strip():
            return "Please enter an Email Address", 400

        email = email.strip().lower()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (email) VALUES (?)", (email,))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        session["user_id"] = user["id"]
        session["email"] = user["email"]

        return redirect(url_for("dashboard"))

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["email"])

# ================= CHAT PAGE =================
@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    users = conn.execute(
        "SELECT id, email FROM users WHERE id != ?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("chat.html",
                           users=users,
                           current_user=session["user_id"],
                           current_email=session["email"])

# ================= GET MESSAGES =================
@app.route("/get_messages/<int:user_id>")
def get_messages(user_id):
    if "user_id" not in session:
        return jsonify([])

    conn = get_db()
    messages = conn.execute("""
        SELECT * FROM messages
        WHERE (sender_id=? AND receiver_id=?)
           OR (sender_id=? AND receiver_id=?)
        ORDER BY timestamp ASC
    """, (session["user_id"], user_id, user_id, session["user_id"])).fetchall()
    conn.close()

    return jsonify([dict(m) for m in messages])

# ================= SEND MESSAGE =================
@app.route("/send_message", methods=["POST"])
def send_message():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 403

    data = request.get_json()
    receiver_id = data.get("receiver_id")
    message = data.get("message", "").strip()

    if not receiver_id or not message:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
        (session["user_id"], receiver_id, message)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ================= PAYMENT =================
@app.route ("/payment")
def payment():
    selected_plan = request.args.get ("plan")
    return render_template ("payment.html", plan=selected_plan)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ================= EXTRA PAGES =================
@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/reset")
def reset():
    return render_template("reset.html")

@app.route("/pricing")
def pricing():
    return render_template ("pricing.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
