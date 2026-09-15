"""Data export utilities for CSV and JSON telemetry analysis."""

import json
import csv
from typing import Dict, List, Any
import os


class TelemetryExporter:
    """Exports simulation metrics and experiment runs to CSV/JSON files."""

    @staticmethod
    def export_json(file_path: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def export_csv(file_path: str, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        keys = list(rows[0].keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
