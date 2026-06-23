# SECOND-KNOWLEDGE-BRAIN.md — CV/Resume Optimizer (Idea 49)

Self-improving domain knowledge base. Grown weekly by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks
- **ATS (Applicant Tracking System) parsing:** machines parse resumes before humans; single-column, standard headings, no text-in-images, .docx/PDF-text preferred. Keyword coverage vs JD is the dominant filter.
- **STAR method:** Situation–Task–Action–Result; quantified Results signal impact.
- **Recruiter 6-second scan:** top-third must convey title fit, recency, and headline impact (Ladders eye-tracking studies).
- **O*NET skill taxonomy:** standardized skills/abilities per occupation — used for transferable-skill mapping.
- **Reverse-chronological vs functional vs hybrid:** ATS favors reverse-chronological; functional triggers parser/recruiter suspicion.

## Scoring Dimensions (this skill)
| Dimension | Weight | Source |
|-----------|--------|--------|
| ATS keyword coverage vs JD | 25% | ATS vendor docs, Jobscan |
| Impact quantification (STAR/metrics) | 20% | STAR literature |
| Role/seniority alignment | 20% | O*NET, JD parse |
| Readability & 6-sec scan | 15% | Ladders eye-tracking |
| Formatting/ATS-parseability | 10% | ATS vendor docs |
| Consistency & error-free | 10% | editorial standard |

## Key Research Papers
| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| Resume parsing with NER | — | 2021 | ArXiv cs.CL | arxiv.org | Parser failure modes |
| Hiring algorithms & bias | — | 2020 | SSRN | ssrn.com | Fairness in ATS ranking |

## State-of-the-Art Methods & Tools
- ATS keyword gap analysis (TF-IDF/embedding match between resume and JD).
- Skills ontology alignment via O*NET / ESCO.
- LLM bullet rewriting under STAR + metric constraints.

## Authoritative Data Sources
- O*NET Online (onetonline.org), BLS Occupational Outlook Handbook (bls.gov/ooh).
- LinkedIn Economic Graph / Future of Work reports.
- ATS vendor documentation (Workday, Greenhouse, Taleo, Lever).

## Analytical Frameworks
ATS keyword coverage · STAR · O*NET skill match · Ladders 6-second scan heuristics.

## Self-Update Protocol
- Queries: "ATS resume parsing 2026", "in-demand skills <role family> report", "resume keyword trends".
- Sources: ArXiv cs.IR/cs.CL, O*NET updates, BLS, LinkedIn reports.
- Frequency: weekly. Append format: `### [DATE] Title — Source — Key finding — URL`.
- Dedupe: skip if URL/DOI hash already present.

## Knowledge Update Log
- [2026-06-18] Seed entry — initial frameworks and dimensions documented.
