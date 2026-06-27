import json
import os

def create_calibration_fixture():
    with open('calibration_samples.json', 'r', encoding='utf-8') as f:
        samples = json.load(f)
        
    # The groups are 4 each in order: strong_ai, tcs_infosys, marketing_honeypot, fictional_company, bad_behavior
    # I want to assign ranks based on actual JD rules.
    # 1-4: Strong AI (real fits)
    # 5-8: TCS/Infosys (AI engineers, but consulting-only penalized)
    # 9-12: Bad behavior (AI engineers, but poor response rate)
    # 13-16: Marketing (Honeypot, disqualified)
    # 17-20: Fictional (Dropped entirely)
    
    # Re-order the loaded samples based on the actual JSON contents
    groups = {
        "strong_ai": [],
        "tcs_infosys": [],
        "bad_behavior": [],
        "marketing_honeypot": [],
        "fictional_company": []
    }
    
    for c in samples:
        career = c.get('career_history', [])
        c_names = [comp.get('company', '').lower() for comp in career]
        title = c.get('profile', {}).get('current_title', '').lower()
        sigs = c.get('redrob_signals', {})
        
        if any(cn in ['stark industries', 'pied piper', 'acme corp', 'dunder mifflin'] for cn in c_names):
            groups["fictional_company"].append(c)
        elif 'marketing' in title:
            groups["marketing_honeypot"].append(c)
        elif any(cn in ['tcs', 'infosys', 'wipro', 'accenture'] for cn in c_names):
            groups["tcs_infosys"].append(c)
        elif sigs.get('recruiter_response_rate', 1.0) < 0.1 or sigs.get('offer_acceptance_rate', 1.0) < 0.2:
            groups["bad_behavior"].append(c)
        else:
            groups["strong_ai"].append(c)
            
    ranked = []
    notes = []
    
    def add_group(group_list, reason_template, start_rank):
        for i, c in enumerate(group_list):
            rank = start_rank + i
            ranked.append(c["candidate_id"])
            notes.append({
                "candidate_id": c["candidate_id"],
                "rank": rank,
                "reason": reason_template.format(id=c["candidate_id"])
            })
            
    add_group(groups["strong_ai"], "{id} is a strong AI Engineer at a product company, matches JD requirements.", 1)
    add_group(groups["tcs_infosys"], "{id} is an AI Engineer but has a consulting-only background (TCS/Infosys), which is a soft disqualifier.", 5)
    add_group(groups["bad_behavior"], "{id} has AI experience but terrible behavioral signals (very low response/acceptance rate).", 9)
    add_group(groups["marketing_honeypot"], "{id} is a Marketing Manager with AI keywords. This is a honeypot and must be disqualified.", 13)
    add_group(groups["fictional_company"], "{id} works at a fictional company. Must be dropped by the first pipeline stage.", 17)
    
    fixture = {
        "jd_ref": "docx_extracts/job_description.txt",
        "created": "2026-06-27",
        "ranked_ids": ranked,
        "notes": notes
    }
    
    os.makedirs('tests/fixtures', exist_ok=True)
    with open('tests/fixtures/calibration_batch.json', 'w', encoding='utf-8') as f:
        json.dump(fixture, f, indent=2)

if __name__ == '__main__':
    create_calibration_fixture()
