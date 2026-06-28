# Scoring Methodology

The Avera ranking engine implements a deterministic, multi-faceted scoring system. Weights and logic are derived strictly from the technical constraints of the Job Description.

## 1. Feature Engineering & Weights

| Scorer | Weight | Core Rationale (JD Derived) |
|--------|--------|-----------------------------|
| **Title & Career** | 45% (Base) | Candidates with explicit 'Senior AI Engineer' titles at product-focused companies are preferred over title-chasers (e.g., job hoppers with <15 month average tenures). |
| **Skills Credibility** | 30% (Base) | Prioritizes deep, verified expertise in Must-Have vector databases (e.g., Pinecone, Qdrant) over broad, unverified keyword stuffing. Assessment scores carry a 3x weight over self-reported proficiencies. |
| **Experience Fit** | 15% (Base) | Uses step bands for total YOE (favoring 5-9) and strictly evaluates ML/AI tenure in the career history to penalize high-YOE candidates lacking applied ML experience. |
| **Location & Logistics** | 10% (Base) | Heavily favors candidates located strictly in the 4 JD-named cities (Pune, Hyderabad, Mumbai, Delhi NCR). |
| **Behavioral Signals** | Multiplier | A multiplicative modifier (0.5 to 1.2) is applied to the final base score. A perfect-on-paper candidate who ghosts or has low response rates is functionally un-hireable. |

## 2. Honeypot Detection Engine

The dataset contains numerous "honeypot" candidates designed to trick keyword-based matching systems. Our engine employs 5 independent detection methods:

| Method | Detection Logic | Result |
|--------|-----------------|--------|
| **Fictional Companies** | Identifies companies like 'Dunder Mifflin' and 'Acme Corp' directly at ingestion layer. | Pre-filter (Dropped) |
| **Method 1: Title/Skill Mismatch** | Flags non-technical titles (e.g., 'HR Manager') claiming 5+ core AI skills like embeddings and LLMs. | Flagged (Dropped) |
| **Method 2: Expert Anomaly** | Flags candidates claiming 'Expert' proficiency on 3+ skills with exactly 0 months of duration. | Flagged (Dropped) |
| **Method 3: Impossible Seniority** | Flags 'Senior' titles with < 2 YOE, or 'Junior' titles with > 10 YOE. | Flagged (Dropped) |
| **Method 4: Unverified Generalist** | Flags candidates with > 15 skills but 0 assessment scores. | Flagged (Dropped) |

*Note: Senior Engineers (Lead/Principal/Staff/Senior) with ≥ 5 YOE are explicitly exempted from the Unverified Generalist (Method 4) filter, as true Staff engineers often possess wide skill variance legitimately.*

## 3. Dynamic Reasoning Generation

Instead of using non-deterministic LLMs that risk hallucination, our Output Subsystem generates human-readable reasoning deterministically.

1.  **Extract Verified Facts**: Pulls exact Title, Company, and YOE.
2.  **Match Must-Have Skills**: Cross-references the candidate's verified skills against the JD's exact vector database and ML requirements (e.g., `FAISS`, `Pinecone`, `Embeddings`).
3.  **Construct Sentence**: Creates sentences like: *“Strong fit: Lead AI Engineer at Razorpay with 6.7 YOE. Demonstrates deep expertise in Embeddings and Python.”*
