#!/usr/bin/env python3
"""Shared helpers for csl-observatory scripts.

Adapted from the Uprava tools/_common.py (H3283): before this module existed,
scripts carried their own private git()/gh() subprocess wrappers, many with NO
timeout (one hung git/gh call blocked the whole tool forever). New code routes
subprocess work through run(); existing private wrappers migrate opportunistically
when they are TRUE duplicates — retry/rate-limit variants with their own semantics
stay local until a shared contract is agreed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 60


def repo_root() -> Path:
    """The csl-observatory checkout holding THIS module (scripts/' parent)."""
    return Path(__file__).resolve().parent.parent


def github_root() -> Path:
    """Parent directory of the org clones.

    Derived from this file's location rather than Path.home() so it stays correct
    under relocated checkouts where home-based resolution false-fails.
    """
    return repo_root().parent


def run(
    cmd: list,
    cwd=None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    check: bool = False,
    env: dict | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess:
    """subprocess.run with utf-8 text I/O, captured output, and a MANDATORY timeout.

    Raises subprocess.TimeoutExpired when the deadline passes (caller decides
    retry vs fail); raises CalledProcessError only when check=True.
    """
    merged = os.environ.copy() if env is None else dict(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=check,
        env=merged,
    )


def git(repo, *args: str, check: bool = False, timeout: float = DEFAULT_TIMEOUT,
        env: dict | None = None) -> subprocess.CompletedProcess:
    """git -C <repo> <args...> through run()."""
    return run(["git", "-C", str(repo), *args], check=check, timeout=timeout, env=env)


def gh(*args: str, check: bool = False, timeout: float = 120) -> subprocess.CompletedProcess:
    """GitHub CLI through run()."""
    return run(["gh", *args], check=check, timeout=timeout)


def gh_api(args: list, tries: int = 5, err_max: int = 100) -> tuple[int, str]:
    """`gh api` with bounded retry; returns (code, stdout_or_error_text).

    A genuine 404 is terminal and returns (1, "404"); other failures retry with
    linear backoff (2s, 4s, ...) and exhaust as (2, "TRANSIENT:<stderr>").
    """
    last = ""
    for i in range(tries):
        r = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return 0, r.stdout
        last = (r.stderr or "").strip()
        if "Not Found" in last or '"status":"404"' in last:
            return 1, "404"
        time.sleep(2 * (i + 1))
    return 2, f"TRANSIENT:{last[:err_max]}"


def force_utf8_stdio() -> None:
    """Best-effort stdout/stderr reconfigure; safe under redirected streams."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
