import csv
import json


def test_submission_regression():
    # 1. Read the ranked output from submission.csv
    try:
        with open("submission.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        # If submission.csv does not exist yet (e.g. fresh clone), skip the test
        return

    top_100_ids = [r["candidate_id"] for r in rows]

    # 2. Assert no juniors in top 30
    for i in range(30):
        if i < len(rows):
            assert "junior" not in rows[i]["reasoning"].lower(), f"Junior found in top 30 at rank {i + 1}"

    # 3. Read calibration target IDs from calibration_batch.json
    try:
        with open("tests/fixtures/calibration_batch.json", encoding="utf-8") as f:
            cal_batch = json.load(f)
            target_ids = cal_batch.get("ranked_ids", [])
    except Exception as e:
        raise AssertionError(f"Failed to load calibration_batch.json: {e}") from e

    # 4. Assert positive calibration targets are in the top 100
    # Apple candidate
    if "CAND_0002025" in target_ids:
        assert "CAND_0002025" in top_100_ids, (
            "Apple candidate CAND_0002025 should NOT be a honeypot and must be in top 100"
        )

    # Netflix candidate
    if "CAND_0071974" in target_ids:
        assert "CAND_0071974" in top_100_ids, "Netflix candidate CAND_0071974 must be in top 100"

    # Adobe candidate
    if "CAND_0005538" in target_ids:
        assert "CAND_0005538" in top_100_ids, (
            "Adobe candidate CAND_0005538 must be in top 100 (job hopping threshold fix)"
        )

    # Meta candidate
    if "CAND_0006567" in target_ids:
        assert "CAND_0006567" in top_100_ids[:20], "Meta candidate CAND_0006567 must be in top 20"
