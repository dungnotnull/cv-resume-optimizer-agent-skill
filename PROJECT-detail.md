# PROJECT-detail.md — CV/Resume Optimizer (Idea 49)

## Executive Summary
A harness skill that scores a resume against a specific job description and an ATS rubric, then produces a prioritized, evidence-backed rewrite roadmap. Grounded in named recruiting/ATS frameworks and continuously refreshed by a crawl pipeline.

## Problem Statement
Most resumes are (1) not tailored to the JD and (2) not ATS-parseable, causing rejection before human review. Candidates lack objective feedback. This skill delivers recruiter-grade analysis with traceable evidence.

## Target Users & Use Cases
- **Active job seeker:** "Score my resume for this Senior Data Engineer JD" → skill returns fit score + rewrite roadmap.
- **Career switcher:** "I'm moving from teaching to UX" → skill maps transferable skills via O*NET and reframes bullets.
- **Coach/recruiter:** batch-evaluate candidate resumes against a role rubric.

## Harness Architecture
```
/cv-resume-optimizer
  → sub-profile-intake        (resume + JD + constraints)        [gate: inputs complete]
  → sub-framework-selector    (ATS + recruiting frameworks)      [gate: ≥2 named frameworks]
  → [main] research           (WebSearch/WebFetch verify trends) [gate: claims cited]
  → sub-scoring-engine        (multi-dim fit + ATS score)        [gate: every score has evidence]
  → sub-quality-reviewer      (challenge each score/claim)       [gate: no unsupported claim]
  → sub-improvement-roadmap   (prioritized rewrite + samples)    [gate: effort/impact on each item]
  → [main] synthesize deliverable
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Quality Gate |
|-----------|---------|--------|---------|-------|--------------|
| sub-profile-intake | Capture resume, JD, constraints | raw resume, JD text | normalized profile JSON | Read | All mandatory fields present |
| sub-framework-selector | Choose frameworks per role family | role family, seniority | framework set + weights | Read, WebSearch | ≥2 named, citable frameworks |
| sub-scoring-engine | Compute fit + ATS score | profile, frameworks | dimension scores 0–100 | Read | Each dimension cites evidence |
| sub-improvement-roadmap | Prioritized rewrite plan | scores, gaps | roadmap + before/after | Write | Effort & impact per item |
| sub-quality-reviewer | Devil's-advocate validation | draft scores/claims | challenge log + fixes | Read | No unsupported claim remains |

## Skill File Format Specification
Frontmatter: `name`, `description`. Sections: Role & Persona, Workflow, Sub-skills Available, Tools, Output Format, Quality Gates. See skills/main.md.

## E2E Execution Flow
1. Receive resume + JD. If JD missing → ask for target role/JD (cannot score fit without it).
2. Intake normalizes both. 3. Selector picks frameworks (e.g., ATS keyword coverage, STAR, 6-second scan, O*NET skill match).
4. Research step verifies current ATS quirks and role keyword trends; falls back to SECOND-KNOWLEDGE-BRAIN.md if offline (signal limitation).
5. Scoring engine produces dimension scores. 6. Quality reviewer challenges. 7. Roadmap emitted. 8. Final deliverable rendered.
Error handling: missing JD → blocked; image-only resume → request text; non-English → proceed with language note.

## SECOND-KNOWLEDGE-BRAIN Integration
Sources: O*NET, BLS, LinkedIn Economic Graph, ATS vendor docs, ArXiv cs.IR/cs.CL. Crawl appends scored entries (recency + keyword relevance). Append format defined in SECOND-KNOWLEDGE-BRAIN.md.

## Supporting Tools Spec
`knowledge_updater.py`: inputs = query list + brain path; output = appended dated entries; schedule = weekly cron.

## Quality Gates
- Every score dimension references a named framework or cited source.
- Roadmap items each carry effort (S/M/L) and impact (Low/Med/High).
- Challenge log shows ≥3 assumptions tested.
- Offline mode explicitly flagged when WebSearch unavailable.

## Test Scenarios (summary; full set in tests/)
1. Senior SWE resume vs SWE JD. 2. Career switcher teacher→UX. 3. New-grad with no JD (blocked path). 4. ATS-hostile formatting (tables/columns). 5. Over-keyword-stuffed resume (penalize).

## Key Design Decisions
1. Fit score requires a JD — refuse to fake it. 2. ATS coverage is a first-class dimension. 3. Every rewrite shows before/after. 4. O*NET used for transferable-skill mapping. 5. Crawl keeps keyword trends current.
