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
# In real apps, store this in an environment variable
FERNET_KEY = b'L0Td9dl8HBVWCpRQ55NgMQqSX4mgquGkb6dYk-Mt-2k='
fernet = Fernet(FERNET_KEY)

# ---------------- ROUTE ----------------
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
                # ENCRYPT (demo)
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
                # HASH (recommended)
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

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
