from flask import Flask, render_template, request
import bcrypt
import mysql.connector
from mysql.connector import errorcode
from cryptography.fernet import Fernet

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mhmd2005@",
    database="security_demo"
)
cursor = db.cursor(buffered=True)

# ---------------- ENCRYPTION KEY (DEMO PURPOSE) ----------------
FERNET_KEY = b'L0Td9dl8HBVWCpRQ55NgMQqSX4mgquGkb6dYk-Mt-2k='
fernet = Fernet(FERNET_KEY)

# ---------------- SETUP: DEMO TABLE FOR SQL INJECTION LESSON ----------------
def ensure_injection_demo_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS injection_demo_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_plain VARCHAR(100) NOT NULL
        )
    """)
    # Insert a demo user only if not already there
    cursor.execute("""
        INSERT IGNORE INTO injection_demo_users (username, password_plain)
        VALUES ('demo', 'demo123')
    """)
    db.commit()

ensure_injection_demo_table()

# ---------------- ROUTE: SIGNUP (HASH / ENCRYPT) ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    success = False

    if request.method == "POST":
        username = request.form["username"].strip()
        password_text = request.form["password"]
        storage = request.form.get("storage", "hash")  # hash or encrypt

        if not username or not password_text:
            message = "Please fill all fields."
            return render_template("index.html", message=message, success=False)

        password_bytes = password_text.encode()

        try:
            if storage == "encrypt":
                encrypted = fernet.encrypt(password_bytes)

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, password_encrypted, storage_method)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (username, None, encrypted, "encrypt")
                )
                db.commit()
                success = True
                message = "Password saved using ENCRYPTION (demo)."

            else:
                hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, password_encrypted, storage_method)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (username, hashed, None, "hash")
                )
                db.commit()
                success = True
                message = "Password saved using HASHING (recommended)."

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                message = "Username already exists!"
            else:
                message = f"Database error: {err.msg}"

    return render_template("index.html", message=message, success=success)

# ---------------- ROUTE: SQL INJECTION DEMO (SAFE EXECUTION) ----------------
@app.route("/sql-injection-demo", methods=["GET", "POST"])
def sql_injection_demo():
    """
    Educational demo:
    - We SHOW what an unsafe concatenated SQL query would look like
    - But we DO NOT execute it
    - We execute the safe parameterized query instead
    """
    message = ""
    unsafe_query_preview = ""
    safe_query_used = "SELECT id, username FROM injection_demo_users WHERE username=%s AND password_plain=%s"
    success = False

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        # Unsafe preview (DO NOT EXECUTE THIS IN REAL CODE)
        unsafe_query_preview = (
            "SELECT id, username FROM injection_demo_users "
            f"WHERE username = '{u}' AND password_plain = '{p}'"
        )

        # Safe query (this is what we actually run)
        try:
            cursor.execute(safe_query_used, (u, p))
            row = cursor.fetchone()
            if row:
                success = True
                message = "Login SUCCESS (safe query)."
            else:
                message = "Login FAILED (safe query)."
        except mysql.connector.Error as err:
            message = f"Database error: {err.msg}"

    return render_template(
        "sql_injection_demo.html",
        message=message,
        success=success,
        unsafe_query_preview=unsafe_query_preview,
        safe_query_used=safe_query_used
    )

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    # Print URLs in terminal at startup (so you always see them)
    print("\n========== DATABASE SECURITY DEMO ==========")
    print("Main Signup Page:")
    print("  http://127.0.0.1:5000/")
    print("SQL Injection Demo Page:")
    print("  http://127.0.0.1:5000/sql-injection-demo")
    print("Wi-Fi Access (replace with your IP shown by Flask):")
    print("  http://<YOUR-IP>:5000/")
    print("  http://<YOUR-IP>:5000/sql-injection-demo")
    print("===========================================\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
