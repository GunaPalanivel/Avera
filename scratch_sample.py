import json


def pull_samples():
    types = {"strong_ai": [], "tcs_infosys": [], "marketing_honeypot": [], "fictional_company": [], "bad_behavior": []}

    with open("DataSet/candidates.jsonl", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)

            career = c.get("career_history", [])
            c_names = [comp.get("company", "").lower() for comp in career]

            # Fictional companies
            if any(cn in ["stark industries", "pied piper", "acme corp", "dunder mifflin"] for cn in c_names):
                if len(types["fictional_company"]) < 4:
                    types["fictional_company"].append(c)
                continue

            profile = c.get("profile", {})
            title = profile.get("current_title", "").lower()

            # Marketing honeypot
            if "marketing" in title:
                if len(types["marketing_honeypot"]) < 4:
                    types["marketing_honeypot"].append(c)
                continue

            # Consulting
            if any(cn in ["tcs", "infosys", "wipro", "accenture"] for cn in c_names):
                if len(types["tcs_infosys"]) < 4:
                    types["tcs_infosys"].append(c)
                continue

            # Bad behavior
            sigs = c.get("redrob_signals", {})
            if sigs.get("recruiter_response_rate", 1.0) < 0.1 or sigs.get("offer_acceptance_rate", 1.0) < 0.2:
                if len(types["bad_behavior"]) < 4:
                    types["bad_behavior"].append(c)
                continue

            # AI Engineer
            if "ai engineer" in title or "machine learning" in title:
                if len(types["strong_ai"]) < 4:
                    types["strong_ai"].append(c)
                continue

            if all(len(v) >= 4 for v in types.values()):
                break

    all_samples = []
    for _k, v in types.items():
        all_samples.extend(v)

    with open("calibration_samples.json", "w", encoding="utf-8") as out:
        json.dump(all_samples, out, indent=2)

    print(f"Pulled {len(all_samples)} samples to calibration_samples.json")
    for k, v in types.items():
        print(f"  {k}: {len(v)}")


if __name__ == "__main__":
    pull_samples()
