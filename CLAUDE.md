# CLAUDE.md — CV/Resume Optimizer Skill (Idea 49)

**Skill name:** `cv-resume-optimizer`
**Tagline:** JD-matched, ATS-aware resume scoring + targeted rewrite roadmap.
**Current phase:** Phase 0 → Phase 5 scaffold complete (see PROJECT-DEVELOPMENT-PHASE-TRACKING.md).
**Source idea:** 49 — *Analyze and optimize a CV/Resume for a specific role, cross-referenced against the job description (JD) to score fit, with per-section rewrite recommendations grounded in world-renowned recruiting & ATS methods; continuously crawl labor-market papers/reports to stay current.*
**Cluster:** `career-education`

## Problem This Skill Solves
Job seekers submit generic resumes that fail Applicant Tracking System (ATS) parsing and do not align to a specific job description. This skill ingests a resume + target JD, scores fit against named recruiting frameworks (STAR, ATS keyword coverage, recruiter 6-second-scan heuristics, O*NET skill taxonomy), and emits a section-by-section, evidence-backed rewrite roadmap with effort/impact prioritization.

## Harness Flow Summary
1. **Intake** (`sub-profile-intake`) — collect resume, target JD, seniority, geography, constraints.
2. **Framework selection** (`sub-framework-selector`) — pick ATS + recruiting frameworks for role family.
3. **Research** (main, WebSearch/WebFetch) — verify current ATS behavior + role keyword trends vs SECOND-KNOWLEDGE-BRAIN.md.
4. **Scoring** (`sub-scoring-engine`) — multi-dimensional fit score vs frameworks.
5. **Challenge** (`sub-quality-reviewer`) — devil's-advocate pass on every claim/score.
6. **Roadmap** (`sub-improvement-roadmap`) — prioritized rewrite actions, before/after samples.

## Sub-skills
- `sub-profile-intake.md` — structured intake of resume, JD, candidate constraints.
- `sub-framework-selector.md` — choose scoring frameworks per role family/seniority.
- `sub-scoring-engine.md` — compute the multi-dimensional fit + ATS score.
- `sub-improvement-roadmap.md` — prioritized rewrite roadmap with before/after.
- `sub-quality-reviewer.md` — challenge/validate gate before final output.

## Tools Required
WebSearch, WebFetch, Read, Write, Bash (for `knowledge_updater.py`).

## Knowledge Sources
- ArXiv cs.CL / cs.IR (resume parsing, IR ranking), SSRN (labor economics).
- O*NET (onetonline.org), BLS Occupational Outlook, LinkedIn Economic Graph reports, Jobscan/ATS vendor docs.

## Supporting Python Tools
- `tools/knowledge_updater.py` — crawl4ai pipeline → appends scored entries to SECOND-KNOWLEDGE-BRAIN.md.

## Active Development Tasks
- [x] Scaffold all required deliverables.
- [ ] Expand role-family keyword dictionaries.
- [ ] Wire weekly cron for knowledge_updater.py.

## Reference Docs
PROJECT-detail.md · PROJECT-DEVELOPMENT-PHASE-TRACKING.md · SECOND-KNOWLEDGE-BRAIN.md
