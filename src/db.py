import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(
    options={
        "databaseURL": "https://svgrl-33939-default-rtdb.firebaseio.com",
        "credential": firebase_admin.credentials.ApplicationDefault(),
    }
)


class Database:
    def __init__(self):
        self.ref = db.reference("/")

    def get(self, key: str) -> Any:
        try:
            return self.ref.child(key).get()
        except Exception as e:
            print(f"Error getting key {key}: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        try:
            self.ref.child(key).set(value)
        except Exception as e:
            print(f"Error setting key {key}: {e}")

    def delete(self, key: str) -> None:
        try:
            self.ref.child(key).delete()
        except Exception as e:
            print(f"Error deleting key {key}: {e}")

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
