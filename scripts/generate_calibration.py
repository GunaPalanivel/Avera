import json
import sys
from pathlib import Path


def generate():
    data_path = Path("DataSet/candidates.jsonl")
    if not data_path.exists():
        print("Data path not found")
        sys.exit(1)

    out_path = Path("tests/fixtures/calibration_batch.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    selected = []

    with data_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)

            # Select 20 specific types for calibration
            title = c["profile"].get("current_title", "").lower()
            company = c["profile"].get("current_company", "").lower()

            if "marketing" in title and len(selected) < 5:
                selected.append(
                    (
                        c["candidate_id"],
                        20 - len(selected),
                        "Marketing Manager honeypot trap, automatically disqualified.",
                    )
                )
            elif company in ["dunder mifflin", "stark industries"] and len(selected) < 10:
                selected.append(
                    (c["candidate_id"], 20 - len(selected), "Fictional company, automatically disqualified.")
                )
            elif "ai engineer" in title and company == "tcs" and len(selected) < 15:
                selected.append(
                    (c["candidate_id"], 15 - len(selected), "Consulting-only AI Engineer, lower priority fit.")
                )
            elif "senior ai engineer" in title and len(selected) < 20:
                selected.append(
                    (c["candidate_id"], 20 - len(selected), "Strong Senior AI Engineer fit for product role.")
                )

            if len(selected) == 20:
                break

    # Format
    batch = {
        "jd_ref": "docx_extracts/job_description.txt",
        "created": "2026-06-27",
        "ranked_ids": [s[0] for s in sorted(selected, key=lambda x: x[1])],
        "notes": [{"candidate_id": s[0], "rank": s[1], "reason": s[2]} for s in sorted(selected, key=lambda x: x[1])],
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)

    print(f"Generated {out_path} with {len(selected)} candidates.")


if __name__ == "__main__":
    generate()
