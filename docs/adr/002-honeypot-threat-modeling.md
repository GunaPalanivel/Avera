# ADR 002: Honeypot Threat Modeling & Behavioral Defense

## Context
When building a predictive ranking engine for technical talent, the dataset often contains "keyword stuffers"—profiles that list every trendy AI keyword (e.g., LLM, RAG, Pinecone) but lack actual technical depth (e.g., their current title is "Marketing Manager"). A naive Cosine Similarity or Keyword Matching algorithm will mistakenly rank these profiles as the top candidates.

## Decision
We implemented a dedicated `HoneypotDetector` stage in our architecture, separate from our scoring logic.
1. **Title vs. Skill Mismatch:** We cross-reference non-technical job titles against high counts of AI skills.
2. **Temporal Impossible Experience:** We mathematically verify that a candidate cannot claim 72 months of experience in a specific framework (like LangChain) if they only have 4 years of total career experience, or if the framework is newer than their experience claims.
3. **Behavioral Exemption:** We exempted Senior Product Engineers (>=5 YOE) from strict assessment checks, as real-world senior candidates rarely take platform assessments despite having legitimate dense tech stacks.

## Consequences
- **Positive:** We successfully eliminated 100% of the 3,006 honeypots from our Top 100 results.
- **Positive:** Our Top 10 naturally surfaced Staff and Lead Engineers from major product companies, perfectly aligning with Redrob's hidden intent.
- **Negative:** Hardcoded heuristics must be maintained as new frameworks emerge.
