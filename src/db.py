import json
import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

DB_FILE_PATH = "../.data/db.json"


class Database:
    def __init__(self, db_file_path: str = DB_FILE_PATH):
        self.db_file_path = db_file_path
        self.db = {}
        if not os.path.exists(db_file_path):
            os.makedirs(os.path.dirname(db_file_path), exist_ok=True)
            with open(db_file_path, "w") as f:
                json.dump({}, f)
        with open(db_file_path, "r") as f:
            self.db = json.load(f)

    def get(self, key: str) -> Any:
        return self.db.get(key, None)

    def set(self, key: str, value: Any) -> None:
        self.db[key] = value
        with open(self.db_file_path, "w") as f:
            json.dump(self.db, f, indent=2)

    def delete(self, key: str) -> None:
        del self.db[key]
        with open(self.db_file_path, "w") as f:
            json.dump(self.db, f, indent=2)

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
        return self.get(f"sessions/{session_id}")

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
