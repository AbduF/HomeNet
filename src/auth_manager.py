import sqlite3
import os
import hashlib
import secrets
from passlib.hash import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "homenet.db")

class AuthManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT
                )
            """)
            # Default admin: admin / 123456
            if not self.conn.execute("SELECT id FROM users WHERE username='admin'").fetchone():
                pwd_hash = bcrypt.hash("123456")
                self.conn.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                                  ("admin", pwd_hash, ""))
                self.conn.commit()

    def login(self, username, password):
        user = self.conn.execute("SELECT password_hash FROM users WHERE username=?", (username,)).fetchone()
        if user and bcrypt.verify(password, user[0]):
            return True
        return False

    def change_password(self, username, new_pass):
        pwd_hash = bcrypt.hash(new_pass)
        self.conn.execute("UPDATE users SET password_hash=? WHERE username=?", (pwd_hash, username))
        self.conn.commit()

    def set_email(self, username, email):
        self.conn.execute("UPDATE users SET email=? WHERE username=?", (email, username))
        self.conn.commit()