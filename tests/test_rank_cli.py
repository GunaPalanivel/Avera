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
