"""Modality-based pipeline configuration routing."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "modalities.json"


class InvalidModalityError(ValueError):
    """Raised when the requested modality has no pipeline configuration."""

    def __init__(self, modality: str) -> None:
        self.modality = modality
        super().__init__(f"Unsupported modality: {modality}")


@lru_cache
def load_modality_configs() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def normalize_modality(modality: str) -> str:
    return modality.strip().upper()


def get_pipeline_config(modality: str) -> tuple[str, dict[str, Any]]:
    """Return the normalized modality key and its pipeline configuration."""
    key = normalize_modality(modality)
    configs = load_modality_configs()
    if key not in configs:
        raise InvalidModalityError(key)
    return key, configs[key]
