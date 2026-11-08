"""Cache-augmented generation (CAG): a small, fixed, versioned context pack.

WHY
---
RAG retrieves a few chunks for every question. Some material is needed on
almost every turn for a language (its fundamentals and the shared 12-stage
path), and re-retrieving it is both noisy and slow. CAG preloads that material
once, as a fixed block in the STABLE prefix of the prompt, so the provider's
prompt cache serves it on every later call at a fraction of the input price.

WHAT A PACK IS
--------------
A JSON manifest in `data/context_packs/<id>.json`:

    {"id": "python-core", "version": "1", "language": "python",
     "description": "...", "files": ["data/content/language/python-fundamentals.md", ...],
     "sha256": "<hash of the rendered pack text>"}

`files` must live under `data/content/`. Each file passes through
`public_text`, which strips front matter (hidden tests) and any protected
solution section, so a pack can never carry answers into a prompt.

`sha256` pins the rendered text. If a source lesson changes, the hash no longer
matches, the pack is skipped with a warning, and prompts fall back to plain
RAG until the version is bumped and the hash refreshed:

    python -m app.services.context_pack          # print id, version, sha256, size

This keeps "which context did this answer see?" answerable from the logs.

WHAT A PACK IS NOT
------------------
It is not the retrieval index and never loads it. Per-question material still
comes from RAG. Packs are capped by `CAG_MAX_CHARS` and fail loudly (skipped,
logged) rather than being silently truncated.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
CONTENT_ROOT = ROOT / "data" / "content"


@dataclass(frozen=True)
class ContextPack:
    id: str
    version: str
    language: str
    text: str
    sha256: str
    files: tuple[str, ...]

    @property
    def tag(self) -> str:
        """Short identity for logs: id@version+hash-prefix."""
        return f"{self.id}@{self.version}+{self.sha256[:12]}"


def pack_dir() -> Path:
    path = Path(settings.cag_pack_dir)
    return path if path.is_absolute() else ROOT / path


def render(files: list[str]) -> str:
    """The exact text a pack contributes. Deterministic: same files, same bytes."""
    from app.services.content_access import public_text

    parts = []
    for rel in files:
        source = (ROOT / rel).resolve()
        if not source.is_relative_to(CONTENT_ROOT.resolve()):
            raise ValueError(f"pack file outside data/content: {rel}")
        if not source.is_file():
            raise ValueError(f"pack file missing: {rel}")
        body = public_text(source.read_text(encoding="utf-8")).strip()
        parts.append(f"### Source: {rel}\n{body}")
    return "\n\n".join(parts)


def load_pack(path: Path, *, verify_hash: bool = True) -> ContextPack:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for key in ("id", "version", "language", "files"):
        if not manifest.get(key):
            raise ValueError(f"{path.name}: missing '{key}'")
    files = list(manifest["files"])
    text = render(files)
    if len(text) > settings.cag_max_chars:
        raise ValueError(f"{path.name}: {len(text)} chars exceeds CAG_MAX_CHARS={settings.cag_max_chars}")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    pinned = manifest.get("sha256")
    if verify_hash and not pinned:
        raise ValueError(f"{path.name}: missing pinned sha256")
    if verify_hash and pinned != digest:
        raise ValueError(f"{path.name}: content changed (sha256 {digest[:12]} != pinned {pinned[:12]}); "
                         "bump 'version' and refresh 'sha256'")
    return ContextPack(id=str(manifest["id"]), version=str(manifest["version"]),
                       language=str(manifest["language"]).lower(), text=text,
                       sha256=digest, files=tuple(files))


def _allowed_ids() -> set[str]:
    return {p.strip() for p in settings.cag_pack_ids.split(",") if p.strip()}


@lru_cache(maxsize=32)
def _pack_for(directory: str, language: str, allowed: frozenset[str], max_chars: int) -> ContextPack | None:
    # max_chars is part of the key so a settings change in tests is not masked.
    folder = Path(directory)
    if not folder.is_dir():
        return None
    for path in sorted(folder.glob("*.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            if str(manifest.get("language", "")).lower() != language:
                continue
            if allowed and manifest.get("id") not in allowed:
                continue
            pack = load_pack(path)
        except Exception as exc:  # never break a request over a pack
            logger.warning("Context pack %s skipped: %s", path.name, exc)
            continue
        logger.info("Context pack loaded: %s (%d chars)", pack.tag, len(pack.text))
        return pack
    return None


def pack_for(language: str, provider: str | None = None) -> ContextPack | None:
    """The active pack for this language, or None when CAG is off or not applicable.

    Packs are only added for providers listed in CAG_PROVIDERS (default: claude,
    where explicit cache breakpoints make the preloaded block cheap). On a
    provider without caching every call would pay for the whole pack.
    """
    if not settings.cag_enabled or not language:
        return None
    providers = {p.strip() for p in settings.cag_providers.split(",") if p.strip()}
    if provider is not None and providers and provider not in providers:
        return None
    return _pack_for(str(pack_dir()), language.lower(), frozenset(_allowed_ids()), settings.cag_max_chars)


def reset_cache() -> None:
    _pack_for.cache_clear()


if __name__ == "__main__":  # pragma: no cover - maintenance helper
    for manifest_path in sorted(pack_dir().glob("*.json")):
        pack = load_pack(manifest_path, verify_hash=False)
        print(f"{manifest_path.name}: id={pack.id} version={pack.version} language={pack.language} "
              f"chars={len(pack.text)} sha256={pack.sha256}")
