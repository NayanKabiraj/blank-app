"""The production manifest: the versioned, validated handoff contract between content
preparation (research -> script -> storyboard, normally done interactively) and the renderer
(which runs non-interactively, in GitHub Actions or locally, from files already committed to
the repo - see section 16 of the spec this module implements). The renderer never executes
anything named inside a manifest; it only reads text, numbers and file paths.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

Format = Literal["vertical", "landscape"]
Language = Literal["en", "hi"]
VerificationStatus = Literal["verified", "partially_verified", "unverified", "fictional_assumption"]


class Source(BaseModel):
    title: str
    url: str
    published: Optional[str] = Field(default=None, description="Publication date if known, e.g. '2023-08-23'.")

    @field_validator("url")
    @classmethod
    def _https_only(cls, v: str) -> str:
        if not (v.startswith("https://") or v.startswith("http://")):
            raise ValueError(f"source url must be http(s): {v!r}")
        return v


class Research(BaseModel):
    summary: str = Field(min_length=20)
    sources: List[Source] = Field(default_factory=list)
    verification_status: VerificationStatus
    uncertainties: str = Field(default="", description="What is NOT independently confirmed; empty only if nothing is uncertain.")

    @model_validator(mode="after")
    def _sources_or_say_why(self) -> "Research":
        if self.verification_status in ("verified", "partially_verified") and not self.sources:
            raise ValueError("verification_status claims sourcing but no sources are listed")
        return self


class Production(BaseModel):
    duration_seconds: int = Field(ge=30, le=75)
    languages: List[Language] = Field(min_length=1)
    formats: List[Format] = Field(min_length=1)
    visual_style: Literal["whiteboard", "colourful", "cinematic"] = "cinematic"
    render_enabled: bool = True


class AudioConfig(BaseModel):
    provider: str = Field(default="piper", description="Adapter name - see audio_engine.tts_engine.PROVIDERS.")
    enabled: bool = True
    voice_en: Optional[str] = None
    voice_hi: Optional[str] = None


class Publishing(BaseModel):
    """Publishing is a separate, later, explicit step. A manifest can describe metadata for it,
    but render_enabled producing an MP4 never implies anything was uploaded anywhere."""
    enabled: bool = False
    requires_approval: bool = True
    title: Optional[dict] = Field(default=None, description="{'en': ..., 'hi': ...}")
    description: Optional[dict] = None
    tags: Optional[dict] = None


class ProductionManifest(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    topic_id: str = Field(pattern=r"^[a-z0-9_]+$", description="Lowercase, digits, underscores only - used as a directory/file name.")
    topic: str
    research: Research
    production: Production
    scripts: dict = Field(default_factory=dict, description="{'en': 'content/scripts/<id>/en_script.md', ...}")
    storyboards: dict = Field(default_factory=dict, description="{'en': 'content/storyboards/<id>/en.json', ...}")
    audio: AudioConfig = Field(default_factory=AudioConfig)
    publishing: Publishing = Field(default_factory=Publishing)

    @model_validator(mode="after")
    def _languages_have_files(self) -> "ProductionManifest":
        for lang in self.production.languages:
            if lang not in self.scripts:
                raise ValueError(f"production.languages includes {lang!r} but scripts[{lang!r}] is missing")
            if lang not in self.storyboards:
                raise ValueError(f"production.languages includes {lang!r} but storyboards[{lang!r}] is missing")
        return self

    def script_path(self, lang: Language, root: Path) -> Path:
        return root / self.scripts[lang]

    def storyboard_path(self, lang: Language, root: Path) -> Path:
        return root / self.storyboards[lang]


def load_manifest(path: Path) -> ProductionManifest:
    return ProductionManifest.model_validate_json(Path(path).read_text(encoding="utf-8"))
