import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    }
)

firebase_admin.initialize_app(cred, {"databaseURL": os.getenv("FIREBASE_DATABASE_URL")})


class Database:
    def __init__(self):
        self.ref = db.reference("/")

    def get(self, key: str) -> Any:
        try:
            return self.ref.child(key).get()
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        self.ref.child(key).set(value)

    def delete(self, key: str) -> None:
        self.ref.child(key).delete()

    def create_session(self, concept: str, domain: str) -> str:
        """Create a new generation session and return its ID"""
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "concept": concept,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "generations": [],
            "current_design_space": None,
        }
        self.set(f"sessions/{session_id}", session)
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a session by ID"""
        session = self.get(f"sessions/{session_id}")
        if not session:
            return None
        # Ensure all required fields exist
        session.setdefault("generations", [])
        session.setdefault("current_design_space", None)
        return session

    def update_session(
        self, session_id: str, design_space: Any, generations: List[Any]
    ) -> None:
        """Update a session with new generations and design space"""
        session = self.get_session(session_id)
        if session:
            if "generations" not in session:
                session["generations"] = []
            session["generations"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "design_space": design_space.model_dump_json(),
                    "generations": [
                        generation.model_dump_json() for generation in generations
                    ],
                }
            )
            session["current_design_space"] = design_space.model_dump_json()
            self.set(f"sessions/{session_id}", session)

    def list_sessions(self) -> List[Dict]:
        """List all sessions"""
        sessions = self.get("sessions") or {}
        return list(sessions.values())


database = Database()
