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

    def list_ablations(self) -> List[Dict]:
        """Return all ablation records as a list sorted by created_at desc."""
        ablations = self.get("ablations") or {}
        # Flatten to list and sort (newest first)
        return sorted(
            ablations.values(),
            key=lambda a: a.get("created_at", ""),
            reverse=True,
        )

    # ------------------------------------------------------------------
    # Ablation utilities
    # ------------------------------------------------------------------

    def create_ablation(self, user_name: str, domain: str, prompts: List[str]) -> str:
        """Create a new ablation experiment and return its ID"""
        ablation_id = str(uuid.uuid4())
        ablation_record = {
            "id": ablation_id,
            "user_name": user_name,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            # Which variant the user is currently on (0-indexed)
            "variant_index": 0,
            # Which prompt inside the current variant (0-indexed)
            "prompt_index": 0,
            "prompts": prompts,
            # History of generations: list of {variant, prompt, generations, design_space}
            "history": [],
            "current_design_space": None,
        }
        self.set(f"ablations/{ablation_id}", ablation_record)
        return ablation_id

    def get_ablation(self, ablation_id: str) -> Optional[Dict]:
        """Fetch an ablation record by ID"""
        ablation = self.get(f"ablations/{ablation_id}")
        return ablation

    def update_ablation_generation(
        self,
        ablation_id: str,
        variant_index: int,
        prompt_index: int,
        design_space: Any,
        generations: List[Any],
    ) -> None:
        """Append a generation result for a particular prompt inside the ablation"""
        ablation = self.get_ablation(ablation_id)
        if not ablation:
            return

        # Append to history
        ablation.setdefault("history", []).append(
            {
                "timestamp": datetime.now().isoformat(),
                "variant_index": variant_index,
                "prompt_index": prompt_index,
                "design_space": design_space.model_dump_json(),
                "generations": [g.model_dump_json() for g in generations],
            }
        )

        # Persist current design space for quick reloads
        ablation["current_design_space"] = design_space.model_dump_json()
        self.set(f"ablations/{ablation_id}", ablation)

    def advance_ablation(
        self, ablation_id: str, total_variants: int, total_prompts: int
    ) -> None:
        """Advance the ablation progress to the next prompt / variant."""
        ablation = self.get_ablation(ablation_id)
        if not ablation:
            return

        prompt_index = ablation.get("prompt_index", 0) + 1
        variant_index = ablation.get("variant_index", 0)

        # Move to next variant if all prompts completed
        if prompt_index >= total_prompts:
            prompt_index = 0
            variant_index += 1

        # Cap variant index at total_variants
        if variant_index >= total_variants:
            variant_index = total_variants  # indicates completion

        ablation["prompt_index"] = prompt_index
        ablation["variant_index"] = variant_index
        # Reset current design space so that a fresh one is created on next request
        ablation["current_design_space"] = None
        self.set(f"ablations/{ablation_id}", ablation)


database = Database()
