# Scoring Methodology

The Avera ranking engine implements a deterministic, multi-faceted scoring system. Weights and logic are derived strictly from the technical constraints of the Job Description.

## 1. Feature Engineering & Weights

| Scorer | Weight | Core Rationale (JD Derived) |
|--------|--------|-----------------------------|
| **Title & Career** | 35% | Candidates with explicit 'Senior AI Engineer' titles at product-focused companies are preferred over title-chasers (e.g., job hoppers with <15 month average tenures). |
| **Behavioral Signals** | 25% | A perfect-on-paper candidate who hasn't logged in for 6 months and has a 5% recruiter response rate is functionally un-hireable. |
| **Skills Credibility** | 20% | Prioritizes deep, verified expertise in Must-Have vector databases (e.g., Pinecone, Qdrant) over broad, unverified keyword stuffing. Assessment scores carry a 3x weight over self-reported proficiencies. |
| **Experience Fit** | 10% | Applies a Gaussian curve centered exactly on 7 years (the JD optimal band of 6-8 years). |
| **Location & Logistics** | 10% | Heavily favors candidates located in Pune/Noida, followed by Tier-1 Indian tech hubs, with steep penalties for inflexible remote-only candidates outside these zones. |

## 2. Honeypot Detection Engine

The dataset contains numerous "honeypot" candidates designed to trick keyword-based matching systems. Our engine employs 5 independent detection methods:

| Method | Detection Logic | Result |
|--------|-----------------|--------|
| **Fictional Companies** | Identifies companies like 'Dunder Mifflin' and 'Acme Corp' | Pre-filter (Dropped) |
| **Method 1: Timeline Impossible** | Flags candidates claiming 7 years of framework experience when their total career spans only 4 years. | Flagged (Dropped) |
| **Method 2: Expert Anomaly** | Flags 'Expert' proficiency tags on candidates with < 6 months total experience. | Flagged (Dropped) |
| **Method 3: Unverified Generalist** | Flags candidates claiming > 15 disparate skills without a single assessment score (keyword stuffing). | Flagged (Dropped) |
| **Method 4: Behavioral Ghost** | Flags perfect technical profiles that have a 0% recruiter response rate and haven't logged in for > 12 months. | Flagged (Dropped) |

*Note: Senior Engineers (Staff/Principal) with > 5 YOE are explicitly exempted from the Unverified Generalist (Method 3) filter, as true Staff engineers often possess wide skill variance legitimately.*

## 3. Dynamic Reasoning Generation

Instead of using non-deterministic LLMs that risk hallucination, our Output Subsystem generates human-readable reasoning deterministically.

1.  **Extract Verified Facts**: Pulls exact Title, Company, and YOE.
2.  **Match Must-Have Skills**: Cross-references the candidate's verified skills against the JD's exact vector database and ML requirements (e.g., `FAISS`, `Pinecone`, `Embeddings`).
3.  **Construct Sentence**: Creates sentences like: *“Strong fit: Lead AI Engineer at Razorpay with 6.7 YOE. Demonstrates deep expertise in Embeddings and Python.”*
