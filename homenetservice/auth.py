"""
HomeNet — Authentication Manager
Handles user authentication, session management, and password operations.
"""

import hashlib
import datetime
from typing import Optional, Dict
from .database import DatabaseManager


class AuthManager:
    """Manages user authentication and sessions."""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.sessions: Dict[str, Dict] = {}

    def login(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and create session. Returns session token."""
        if self.db.authenticate(username, password):
            token = self._generate_token()
            self.sessions[token] = {
                "username": username,
                "created_at": datetime.datetime.now(),
                "expires_at": datetime.datetime.now() + datetime.timedelta(hours=24),
            }
            return token
        return None

    def logout(self, token: str) -> bool:
        """End a user session."""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

    def validate_session(self, token: str) -> Optional[Dict]:
        """Validate a session token."""
        if token in self.sessions:
            session = self.sessions[token]
            if datetime.datetime.now() < session["expires_at"]:
                return session
            else:
                del self.sessions[token]
        return None

    def change_password(self, username: str, current_password: str,
                        new_password: str) -> bool:
        """Change user password."""
        if not self.db.authenticate(username, current_password):
            return False
        return self.db.update_user(username, new_password=new_password)

    def reset_password(self, email: str, new_password: str) -> bool:
        """Reset password using recovery email."""
        return self.db.reset_password(email, new_password)

    def update_profile(self, username: str, new_username: str = None,
                       email: str = None) -> bool:
        """Update user profile."""
        return self.db.update_user(username, new_username=new_username, email=email)

    def _generate_token(self) -> str:
        """Generate a secure session token."""
        import secrets
        return secrets.token_hex(32)

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.datetime.now()
        expired = [t for t, s in self.sessions.items() if now >= s["expires_at"]]
        for token in expired:
            del self.sessions[token]