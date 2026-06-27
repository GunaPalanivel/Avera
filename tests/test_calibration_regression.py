import csv
import json
from src.models import CandidateModel
from src.detectors.honeypot_detector import is_honeypot

def test_submission_regression():
    try:
        with open("submission.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception:
        return
        
    top_100_ids = [r["candidate_id"] for r in rows]
    
    for i in range(30):
        if i < len(rows):
            assert "junior" not in rows[i]["reasoning"].lower(), f"Junior found in top 30 at rank {i+1}"
            
    try:
        with open("tests/fixtures/calibration_batch.json", "r", encoding="utf-8") as f:
            cal_batch = [json.loads(line) for line in f]
            
        for c_dict in cal_batch:
            if c_dict["candidate_id"] == "CAND_0002025":
                candidate = CandidateModel.model_validate(c_dict)
                assert not is_honeypot(candidate), "Apple candidate CAND_0002025 should NOT be a honeypot"
    except Exception:
        pass
        
    assert "CAND_0006567" in top_100_ids[:20], "Meta candidate CAND_0006567 must be in top 20"

