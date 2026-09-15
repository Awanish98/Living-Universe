"""Save game and checkpoint manager for simulation snapshots."""

import json
import os
from typing import Dict, Any, Optional
from .serializer import UniverseSerializer


class SaveManager:
    """Manages file persistence, autosaves, and save slots in the saves/ directory."""

    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def save_state(self, file_name: str, payload: Dict[str, Any]) -> str:
        if not file_name.endswith(".json"):
            file_name += ".json"
        path = os.path.join(self.save_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return path

    def load_state(self, file_name: str) -> Dict[str, Any]:
        if not file_name.endswith(".json"):
            file_name += ".json"
        path = os.path.join(self.save_dir, file_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Save file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return UniverseSerializer.deserialize(data)

    def list_saves(self) -> list[str]:
        if not os.path.exists(self.save_dir):
            return []
        return [f for f in os.listdir(self.save_dir) if f.endswith(".json")]
