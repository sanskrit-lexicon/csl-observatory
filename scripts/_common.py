#!/usr/bin/env python3
"""Shared helpers for csl-observatory scripts.

Adapted from the Uprava tools/_common.py (H3283): before this module existed,
scripts carried their own private git()/gh() subprocess wrappers, many with NO
timeout (one hung git/gh call blocked the whole tool forever). New code routes
subprocess work through run(); existing private wrappers migrate onto the
shared contract when their call-site behaviour is provably identical.

The shared subprocess contract (H7356-class):
- run()            — any command, MANDATORY timeout, utf-8 text I/O
- git()            — git -C <repo> through run()
- gh()             — one-shot `gh` CLI through run()
- gh_api()         — `gh api` bounded retry, 404-terminal, linear backoff,
                     returns (code, text); err_max bounds the error text
- gh_cli_retry()   — `gh` CLI with fast no-sleep retries, returns the LAST
                     CompletedProcess (runbook-style callers)
- gh_api_harvest() — bulk-harvest `gh api` (pull_data semantics, verbatim):
                     rate-limit resets have their own capped retry budget,
                     5xx/timeout/EOF retry exponentially, a 404 fails now,
                     returns stdout-or-None

Known LOCAL exceptions (semantics deliberately not shared): the sandbox
test-harness runner in obs_t_gold_roundtrip_check.py, the stdout-only
git/git_ok pair in pre_push_stale_base_check.py (hot gate, own contract), and
the bytes-mode git() in envelope_check.py (blob-exact output, text mode would
corrupt it).
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


def gh_cli_retry(args: list, tries: int = 3) -> subprocess.CompletedProcess:
    """`gh` CLI with fast retries (NO sleep between attempts); returns the
    LAST CompletedProcess either way — callers that only check .returncode
    keep their shape.
    """
    r = subprocess.run(["gh", *args], capture_output=True, encoding="utf-8")
    for _ in range(tries - 1):
        if r.returncode == 0:
            return r
        r = subprocess.run(["gh", *args], capture_output=True, encoding="utf-8")
    return r


def rate_limit_wait_seconds(cap: float = 120.0) -> float:
    """Read the primary rate-limit reset time off GitHub; cap the wait so a
    single call never blocks the script for a full hour."""
    r = subprocess.run(["gh", "api", "rate_limit", "--jq", ".rate.reset"],
                       capture_output=True, encoding="utf-8")
    try:
        reset_epoch = int(r.stdout.strip())
        return max(1.0, min(reset_epoch - time.time() + 1, cap))
    except (ValueError, AttributeError):
        return cap


def gh_api_harvest(args: list, retries: int = 3, backoff: float = 2.0,
                   rate_limit_retries: int = 3) -> str | None:
    """`gh api` for bulk harvests (pull_data semantics, moved verbatim).

    Rate-limit hits (primary or secondary) get their OWN retry budget —
    waiting out a reset is a different failure mode than a transient server
    error, so the two counters never mix. 5xx/timeout/EOF retry on
    exponential backoff; everything else, including a 404, fails immediately.
    Returns stdout or None.
    """
    attempt = 0
    rl_attempt = 0
    while True:
        r = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return r.stdout
        stderr = r.stderr or ""
        if "rate limit" in stderr.lower() and rl_attempt < rate_limit_retries:
            rl_attempt += 1
            wait = rate_limit_wait_seconds()
            print(f"  ! rate limit hit — waiting {wait:.0f}s for reset "
                  f"(rate-limit retry {rl_attempt}/{rate_limit_retries})", file=sys.stderr)
            time.sleep(wait)
            continue
        retriable = any(s in stderr for s in ["HTTP 502", "HTTP 503", "HTTP 504", "timeout", "EOF"])
        if not retriable or attempt >= retries - 1:
            print(f"  ! gh api error: {stderr[:200].strip()}", file=sys.stderr)
            return None
        wait = backoff ** (attempt + 1)
        print(f"  … retrying in {wait:.1f}s (attempt {attempt+2}/{retries})", file=sys.stderr)
        time.sleep(wait)
        attempt += 1


def force_utf8_stdio() -> None:
    """Best-effort stdout/stderr reconfigure; safe under redirected streams."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
