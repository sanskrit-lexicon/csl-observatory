#!/usr/bin/env python3
"""Shared `gh api` helpers: JSON fetch with on-disk caching and bounded retry.

Used by the read-only metadata/workflow snapshot scripts so the caching, error
handling, and transient-failure retry live in one place rather than being
copy-pasted per script.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Markers of a transient GitHub/network failure worth retrying (5xx, timeouts).
_TRANSIENT = ("502", "503", "504", "timed out", "timeout", "connection reset",
              "temporarily unavailable", "bad gateway")


def cache_path(cache_dir: Path, repo: str, topic: str, endpoint: str) -> Path:
    digest = hashlib.sha1(endpoint.encode("utf-8")).hexdigest()[:10]
    safe_repo = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in repo)
    return cache_dir / f"{safe_repo}.{topic}.{digest}.json"


def load_cached_json(path: Path) -> tuple[object | None, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except OSError as exc:
        return None, f"cache read failed: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"cache JSON invalid: {exc}"


def _looks_transient(message: str) -> bool:
    low = message.lower()
    return any(token in low for token in _TRANSIENT)


def run_gh(
    endpoint: str,
    *,
    cache_dir: Path | None = None,
    cache_repo: str = "",
    cache_topic: str = "",
    refresh_cache: bool = False,
    retries: int = 2,
    sleep=time.sleep,
) -> tuple[object | None, str]:
    """Fetch and parse `gh api <endpoint>`.

    Returns (data, warning). On success warning is "" (or a non-fatal note such
    as a cache-write failure, with data still returned). On failure data is None
    and warning describes it. Transient failures (timeouts, 5xx) are retried up
    to `retries` times with exponential backoff; `sleep` is injectable for tests.
    """
    cache_file: Path | None = None
    if cache_dir and cache_repo and cache_topic:
        cache_file = cache_path(cache_dir, cache_repo, cache_topic, endpoint)
        if cache_file.exists() and not refresh_cache:
            return load_cached_json(cache_file)

    last = "unknown gh api error"
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                ["gh", "api", endpoint],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            last = f"gh api failed: {exc}"
            if attempt < retries:
                sleep(2 ** attempt)
                continue
            return None, last
        except OSError as exc:
            return None, f"gh api failed: {exc}"

        if result.returncode != 0:
            last = (result.stderr.strip() or result.stdout.strip()
                    or "unknown gh api error").replace("\n", " ")
            if _looks_transient(last) and attempt < retries:
                sleep(2 ** attempt)
                continue
            return None, last

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            return None, f"invalid JSON from gh api: {exc}"

        if cache_file:
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            except OSError as exc:
                return data, f"cache write failed: {exc}"

        return data, ""

    return None, last
