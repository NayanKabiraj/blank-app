"""Loads production.yaml - the single place that controls topics/day, languages, formats,
visual style and whether rendering/publishing is enabled, without touching any source code
(spec section 18). A missing file falls back to small, safe defaults (1 topic, en+hi, vertical
only, cinematic style, publishing off) so the engine never silently does more than expected.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]   # repo root (src/explainer/config/ -> repo root)
DEFAULT_CONFIG_PATH = ROOT / "src" / "explainer" / "config" / "production.yaml"


class RenderConfig(BaseModel):
    enabled: bool = True
    parallel_jobs: int = Field(default=1, ge=1, le=4)
    quality: Literal["draft", "medium", "high"] = "medium"


class PublishingConfig(BaseModel):
    enabled: bool = False
    approval_required: bool = True


class ProductionConfig(BaseModel):
    topics_per_day: int = Field(default=1, ge=1, le=20)
    duration_min: int = Field(default=45, ge=20)
    duration_max: int = Field(default=60, le=90)
    languages: List[Literal["en", "hi"]] = Field(default_factory=lambda: ["en", "hi"])
    formats: List[Literal["vertical", "landscape"]] = Field(default_factory=lambda: ["vertical"])
    visual_style: Literal["whiteboard", "colourful", "cinematic"] = "cinematic"
    render: RenderConfig = Field(default_factory=RenderConfig)
    publishing: PublishingConfig = Field(default_factory=PublishingConfig)

    @property
    def jobs_per_day(self) -> int:
        return self.topics_per_day * len(self.languages) * len(self.formats)


def load_config(path: Optional[Path] = None) -> ProductionConfig:
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return ProductionConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ProductionConfig.model_validate(data.get("production", data))
