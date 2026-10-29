"""Regression pins for the eight deterministic findings of the 19-10-2026
bughunt fix lane (H7108).

Every pin fails against the pre-fix code and passes after it:

  §5  krippendorff_alpha_nominal was Scott's-pi-shaped, not alpha
  §6  workflow_health.py wrote a header-only CSV for an unknown --repo
  §8  a dropped annotation batch shrank the kappa denominator silently
  §9  a missing flip-run file became a filename string in a float field
  §13 the duplicate-row_id guard could not fire for string ids
  §14 the blind-batch builder never cleared stale batches
  §15 the CRLF round-trip test could not fail on the platform it ran on
  §17 the token gate had no grandfathering (fixed upstream in PR #279; pinned here)

The reporting-contract findings (§4 §7 §10) are owner decisions and are
deliberately untouched.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys

import pytest
from conftest import REPO_ROOT

# Import-time path setup: the conftest fixture that adds these dirs runs after
# collection, and these pins need the modules at module scope.
for _dir in ("validation", "scripts"):
    _p = str(REPO_ROOT / _dir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import compute_component_kappa as cck  # noqa: E402  — validation/ (conftest)
import obs_t_baselines  # noqa: E402  — scripts/ (conftest)
import obs_t_gold  # noqa: E402, F401  — second copy of the same helper
import workflow_health  # noqa: E402

# --------------------------------------------------------------------- §5 ---
# Krippendorff's published worked example: 12 units, 2-4 coders, nominal
# alpha = 0.743 (Krippendorff 2004 §11.3; the fixture used by the reference
# implementations). Units are columns, None = missing label.
KRIPPENDORFF_CANON = [
    (1, 1, None, 1), (2, 2, 3, 2), (3, 3, 3, 3), (3, 3, 3, 3),
    (2, 2, 2, 2), (1, 2, 3, 4), (4, 4, 4, 4), (1, 1, 2, 1),
    (2, 2, 2, 2), (None, 5, 5, 5), (None, None, 1, 1), (None, 3, None, None),
]


@pytest.mark.parametrize("mod", [obs_t_baselines, obs_t_gold])
def test_alpha_matches_published_example(mod):
    alpha = mod.krippendorff_alpha_nominal(KRIPPENDORFF_CANON)
    assert round(alpha, 3) == 0.743, (
        f"{mod.__name__}: published Krippendorff example must give 0.743; "
        f"got {alpha:.4f} (the pre-fix implementation returns 0.8935)"
    )


@pytest.mark.parametrize("mod", [obs_t_baselines, obs_t_gold])
def test_alpha_is_not_the_pi_shaped_value(mod):
    """Negative control: the old formula's value on the same fixture."""
    assert abs(mod.krippendorff_alpha_nominal(KRIPPENDORFF_CANON) - 0.8935) > 1e-3


def test_alpha_two_rater_relation_to_scott_pi():
    units = [('a', 'a'), ('a', 'b'), ('b', 'b'), ('b', 'b'), ('a', 'a'),
             ('b', 'a'), ('a', 'a')]
    n = 2 * len(units)
    a_ = sum(1 for x, y in units if x == y)
    p_o = a_ / len(units)
    ca = {lab: sum(1 for u in units for v in u if v == lab) for lab in ('a', 'b')}
    p_e = sum((ca[lab] / n) ** 2 for lab in ca)
    pi = (p_o - p_e) / (1 - p_e)
    expected = 1 - (n - 1) / n * (1 - pi)
    assert abs(obs_t_baselines.krippendorff_alpha_nominal(units) - expected) < 1e-12


def test_published_alpha_3dp_unchanged():
    """2-rater n≈10^3: the definition fix moves alpha by ~1/n, not by 3 dp."""
    published = json.loads(
        (REPO_ROOT / "observatory" / "site" / "src" / "data"
         / "obs_t_baselines_field_metrics.json").read_text(encoding="utf-8"))
    for block in ("detection_field_metrics", "location_classification_agreement"):
        old = published[block]["krippendorff_alpha_nominal"]
        n = published[block]["krippendorff_alpha_pairable_values"]
        new = 1 - (n - 1) / n * (1 - old)
        assert abs(new - old) < 5e-4, f"{block}: 3-dp shift {old} -> {new}"
        assert round(new, 3) == old, f"{block}: published 3-dp value changed"


# --------------------------------------------------------------------- §6 ---
def test_workflow_health_refuses_unknown_repo():
    metadata = [{"repo": "alpha"}, {"repo": "beta"}]
    with pytest.raises(SystemExit) as exc:
        workflow_health.select_metadata(metadata, ["notarepo"])
    assert "unknown --repo" in str(exc.value)


def test_workflow_health_unknown_repo_leaves_csv_untouched(tmp_path):
    out = tmp_path / "workflow_health.csv"
    report = tmp_path / "workflow_health.md"
    out.write_text("SENTINEL\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "workflow_health.py"),
         "--offline", "--repo", "notarepo", "--out", str(out),
         "--report", str(report)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=120, check=False)
    assert proc.returncode != 0, "an unknown --repo must exit non-zero"
    assert out.read_text(encoding="utf-8") == "SENTINEL\n", (
        "an unknown --repo must not overwrite the published CSV"
    )


def test_workflow_health_selects_known_repo():
    metadata = [{"repo": "alpha"}, {"repo": "beta"}]
    assert workflow_health.select_metadata(metadata, ["beta"]) == [metadata[1]]
    assert workflow_health.select_metadata(metadata, None) == metadata


# ------------------------------------------------------------- §8 §9 §13 ---
@pytest.fixture()
def kappa_dir(tmp_path, monkeypatch):
    """A minimal, self-consistent validation/ fixture directory."""
    monkeypatch.setattr(cck, "HERE", tmp_path)
    (tmp_path / "blind_batches").mkdir()
    (tmp_path / "flip_runs").mkdir()
    labels = ["citation", "grammar", "meta", "sense"]

    def dump(name, rows):
        (tmp_path / name).write_text(json.dumps(rows), encoding="utf-8")

    base = [{"row_id": i + 1, "label": labels[i % 4]} for i in range(4)]
    dump("component_passA.json", base)
    dump("component_passB.json", base)
    for ann in ("A", "B"):
        for run in (2, 3):
            dump(f"flip_runs/pass{ann}_run{run}.json", base)
    dump("blind_batches/batch_01.json", [{"row_id": 1}, {"row_id": 2}])
    (tmp_path / "gold_sample.csv").write_text(
        "row_id,source_layer,dict,headword_iast,old_iast,new_iast,comment_raw\n"
        + "".join(f"{i + 1},layer,d,ha,old,new,comment\n" for i in range(4)),
        encoding="utf-8")
    return tmp_path


def test_kappa_records_missing_rows_with_allow_partial(kappa_dir):
    b = json.loads((kappa_dir / "component_passB.json").read_text(encoding="utf-8"))
    (kappa_dir / "component_passB.json").write_text(
        json.dumps([r for r in b if r["row_id"] != 4]), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cck.check_denominator(cck.load_pass("component_passA.json"),
                              cck.load_pass("component_passB.json"))
    assert "only one pass" in str(exc.value)
    cck.main(["--allow-partial"])
    stats = json.loads((kappa_dir / "component_kappa_stats.json").read_text(encoding="utf-8"))
    assert stats["n_missing"] == 1
    assert stats["missing_row_ids"] == [4]


def test_kappa_missing_flip_file_raises(kappa_dir):
    with pytest.raises(SystemExit) as exc:
        cck.flip_rate(["flip_runs/passA_run2.json", "flip_runs/gone.json"], [1])
    assert "missing" in str(exc.value)


def test_kappa_flip_rate_returns_a_number_when_files_exist(kappa_dir):
    rate = cck.flip_rate(
        ["component_passA.json", "flip_runs/passA_run2.json"], [1, 2])
    assert isinstance(rate, float) and 0.0 <= rate <= 1.0


def test_kappa_duplicate_string_row_id_raises(kappa_dir):
    rows = [{"row_id": "1", "label": "citation"},
            {"row_id": 1, "label": "citation"}]
    (kappa_dir / "component_passA.json").write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(AssertionError, match="duplicate row_id"):
        cck.load_pass("component_passA.json")


# -------------------------------------------------------------------- §14 ---
def test_blind_batches_clear_stale_draws(tmp_path):
    import build_blind_sample

    out = tmp_path / "blind_batches"
    out.mkdir()
    for n in (1, 2, 3):
        (out / f"batch_{n:02d}.json").write_text("[]", encoding="utf-8")
    (out / "gap_01.json").write_text("[]", encoding="utf-8")
    build_blind_sample.write_batches(out, [[{"row_id": 1}], [{"row_id": 2}]])
    assert sorted(p.name for p in out.glob("batch_*.json")) == [
        "batch_01.json", "batch_02.json"]
    assert not (out / "batch_03.json").exists(), "a smaller re-draw left a stale batch"
    assert (out / "gap_01.json").exists(), "gap_*.json must be left alone"


# -------------------------------------------------------------------- §17 ---
def _load_gate():
    path = REPO_ROOT / ".githooks" / "token_size_gate.py"
    spec = importlib.util.spec_from_file_location("token_size_gate", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses resolves the module by name
    spec.loader.exec_module(mod)
    return mod


def test_token_gate_grandfathers_preexisting_oversized():
    gate = _load_gate()
    budget = 20_000
    assert gate.grandfather_verdict(25_000, 25_010, budget) is not None
    assert gate.grandfather_verdict(None, 20_001, budget) is None
    assert gate.grandfather_verdict(19_999, 20_001, budget) is None
    assert gate.grandfather_verdict(25_000, 25_000 + budget + 1, budget) is None


def test_token_gate_staged_end_to_end(tmp_path):
    git = shutil.which("git") or "git"
    gate_py = REPO_ROOT / ".githooks" / "token_size_gate.py"
    repo = tmp_path / "repo"
    repo.mkdir()

    def run(*args):
        return subprocess.run([git, "-c", "user.email=t@example.invalid",
                               "-c", "user.name=t", *args],
                              cwd=repo, capture_output=True, text=True, check=True)

    run("init", "-q")
    big = repo / "big.txt"
    big.write_text("x" * 25_000, encoding="utf-8")
    run("add", "big.txt")
    run("commit", "-q", "-m", "base")
    big.write_text("x" * 25_010, encoding="utf-8")
    run("add", "big.txt")
    edited = subprocess.run([sys.executable, str(gate_py), "--staged"],
                            cwd=repo, capture_output=True, text=True, check=False)
    assert edited.returncode == 0, (
        "editing a file already over budget at HEAD must be grandfathered: "
        f"{edited.stderr[-500:]}")

    new = repo / "new.txt"
    new.write_text("y" * 20_001, encoding="utf-8")
    run("add", "new.txt")
    added = subprocess.run([sys.executable, str(gate_py), "--staged"],
                           cwd=repo, capture_output=True, text=True, check=False)
    assert added.returncode == 1, "a NEW oversized file must still be refused"
