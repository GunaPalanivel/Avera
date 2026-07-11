import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_health_check_exits_zero():
    result = subprocess.run(
        [sys.executable, "rank.py", "--health"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "[OK] avera foundation ready" in result.stdout
    assert "must-have skills loaded" in result.stdout


def test_fast_flag_ranks_sample():
    out = ROOT / ".sandbox" / "fast_cli_test.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    result = subprocess.run(
        [
            sys.executable,
            "rank.py",
            "--fast",
            "--candidates",
            "tests/fixtures/sample.jsonl",
            "--limit",
            "1",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "Pipeline summary:" in result.stdout
    out.unlink(missing_ok=True)


def test_missing_candidates_exits_two():
    result = subprocess.run(
        [sys.executable, "rank.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "--candidates required" in result.stderr
