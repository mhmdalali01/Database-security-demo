import mysql.connector
from cryptography.fernet import Fernet

# SAME key used in app.py
FERNET_KEY = b'L0Td9dl8HBVWCpRQ55NgMQqSX4mgquGkb6dYk-Mt-2k='
fernet = Fernet(FERNET_KEY)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mhmd2005@",
    database="security_demo"
)

cursor = db.cursor()

cursor.execute("""
    SELECT username, password_encrypted
    FROM users
    WHERE storage_method = 'encrypt'
""")

for username, encrypted in cursor.fetchall():
    decrypted = fernet.decrypt(encrypted).decode()
    print(f"Username: {username} | Password: {decrypted}")
