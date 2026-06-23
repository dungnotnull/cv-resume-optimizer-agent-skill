---
name: sub-profile-intake
description: Normalize a resume + target JD + candidate constraints into a structured profile for scoring.
---

## Purpose
Capture and normalize all inputs needed to score resume↔JD fit. Blocks the harness if a target JD/role is absent.

## Inputs
- Raw resume text (or extracted from file).
- Target JD text or role title + seniority.
- Constraints: geography, work authorization, salary band, remote/onsite, career-switch flag.

## Process
1. Extract resume sections: header, summary, experience (with bullets), skills, education, certs.
2. Parse JD into: required skills, preferred skills, responsibilities, seniority signals, hard requirements.
3. Flag missing-but-required inputs. If no JD/role → return BLOCKED with the request.
4. Detect format risks (multi-column, tables, images) for the ATS dimension.

## Outputs
Normalized profile object: `{resume_sections, jd_requirements, constraints, format_risks, career_switch}`.

## Quality Gate
- Resume + JD both present and parsed, OR explicit BLOCKED status with reason.
- Format risks listed for downstream ATS scoring.
