# Test Scenarios — CV/Resume Optimizer (Idea 49)

## Scenario 1 — Senior SWE resume vs SWE JD
- **Input:** 2-page senior backend resume + Senior Backend Engineer JD (Go, Kubernetes, AWS).
- **Expected:** Dimension table with ATS keyword gap (e.g., missing "Kubernetes" if absent), STAR quantification score, roadmap top-3 fix missing required keywords. Overall verdict band.
- **Pass:** every dimension cites evidence; roadmap items carry effort+impact.

## Scenario 2 — Career switcher (teacher → UX designer)
- **Input:** teaching resume + Junior UX Designer JD; career_switch flag.
- **Expected:** O*NET transferable-skill mapping (e.g., curriculum design → user research empathy), reframed bullets, portfolio-link recommendation.
- **Pass:** transferable skills explicitly mapped; no fabricated UX experience.

## Scenario 3 — No JD provided (blocked path)
- **Input:** resume only, no target role.
- **Expected:** harness returns BLOCKED with request for target JD/role; no fabricated fit score.
- **Pass:** skill refuses to score fit without a target.

## Scenario 4 — ATS-hostile formatting
- **Input:** resume using two columns, tables, and a logo image with text.
- **Expected:** format-risk flags raised; ATS-parseability dimension penalized; roadmap recommends single-column reflow.
- **Pass:** format risks listed and reflected in score.

## Scenario 5 — Keyword-stuffed resume
- **Input:** resume with a hidden keyword block repeating JD terms unnaturally.
- **Expected:** quality reviewer flags stuffing; coverage not fully rewarded; roadmap recommends natural integration.
- **Pass:** stuffing penalized, logged in challenge log.

## Scenario 6 — Offline / degraded mode
- **Input:** any resume+JD with WebSearch unavailable.
- **Expected:** skill uses SECOND-KNOWLEDGE-BRAIN.md and flags the currency limitation.
- **Pass:** offline limitation explicitly stated in Sources section.
