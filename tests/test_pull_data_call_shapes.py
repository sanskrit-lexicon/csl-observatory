"""Regression pins for pull_data.py's gh_api_harvest call shapes (H7879).

The 28-10-2026 subprocess-contract refactor (H7360, PR #292) replaced
pull_data's private varargs wrapper (`def gh(*args)` → `["gh", "api", *args]`)
with the shared `_common.gh_api_harvest(args: list, …)` alias but never updated
the call sites. Import probes stayed green while every scheduled run died at
runtime: fetch_repos' 4 positional args fit the 1–4 parameter signature, so
`args` became the string "--paginate" and `subprocess` unpacked its CHARACTERS
("gh api: accepts 1 arg(s), received 10"), and fetch_project_fields' 5 args
raised TypeError outright. These tests fail on that code and pass on the fix:
each fetcher must hand gh_api_harvest exactly ONE list argument — no varargs,
no bare string.
"""
from __future__ import annotations

import sys
from unittest import mock

from conftest import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pull_data  # noqa: E402


def _captured(target: str, **call_kwargs):
    """Call a pull_data fetcher with pull_data.gh mocked out; return the
    mock so the tests can assert on the exact call shape (no network).

    return_value=None mimics gh_api_harvest's failure return: the fetchers'
    own `if not out: break` / parse_jsonl(None)→[] paths exit the pagination
    loop cleanly, so exactly ONE call is made and inspected.
    """
    with mock.patch.object(pull_data, "gh", return_value=None) as gh_mock:
        getattr(pull_data, target)(**call_kwargs)
    return gh_mock


def test_fetch_repos_passes_one_list_argument():
    m = _captured("fetch_repos")
    m.assert_called_once()
    args = m.call_args.args
    assert len(args) == 1 and isinstance(args[0], list), (
        "fetch_repos must call gh_api_harvest with ONE list argument — "
        "varargs silently repack into retries/backoff/rate_limit_retries"
    )
    argv = args[0]
    assert argv[0] == "--paginate"
    assert argv[1].startswith("orgs/sanskrit-lexicon/repos?")
    assert "--jq" in argv


def test_fetch_issues_passes_one_list_argument():
    m = _captured("fetch_issues", repo="MW")
    m.assert_called_once()
    args = m.call_args.args
    assert len(args) == 1 and isinstance(args[0], list), (
        "fetch_issues must call gh_api_harvest with ONE list argument"
    )
    argv = args[0]
    assert argv[0] == "--paginate"
    assert argv[1] == "repos/sanskrit-lexicon/MW/issues?state=all&per_page=100"


def test_fetch_project_fields_passes_one_list_argument():
    # The mocked gh returns None, so the pagination loop breaks immediately —
    # one call, no network.
    m = _captured("fetch_project_fields")
    m.assert_called_once()
    args = m.call_args.args
    assert len(args) == 1 and isinstance(args[0], list), (
        "fetch_project_fields must call gh_api_harvest with ONE list "
        "argument (5 varargs raised TypeError on every 2026-11 run)"
    )
    assert args[0][0] == "graphql"
    assert "-f" in args[0]


def test_fetch_commits_passes_one_list_argument():
    m = _captured("fetch_commits", repo="MW")
    m.assert_called_once()
    args = m.call_args.args
    assert len(args) == 1 and isinstance(args[0], list), (
        "fetch_commits must call gh_api_harvest with ONE list argument"
    )
    assert args[0][0] == "graphql"


def test_no_varargs_gh_call_sites_remain():
    """Source-level pin: `gh(*` must never come back into pull_data.py."""
    src = (REPO_ROOT / "scripts" / "pull_data.py").read_text(encoding="utf-8")
    assert "gh(*" not in src, (
        "pull_data.py regressed to varargs gh() calls — gh_api_harvest takes "
        "ONE list argument (H7879)"
    )
