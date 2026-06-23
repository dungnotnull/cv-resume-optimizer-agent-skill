---
name: sub-scoring-engine
description: Compute multi-dimensional resume↔JD fit + ATS score against named frameworks with per-dimension evidence.
---

## Purpose
Produce defensible 0–100 scores per dimension and a weighted total.

## Inputs
Normalized profile + selected frameworks/weights.

## Dimensions & Default Weights
| Dimension | Weight | Evidence required |
|-----------|--------|-------------------|
| ATS keyword coverage vs JD | 25% | matched/missing keyword list |
| Impact quantification (STAR/metrics) | 20% | count of quantified bullets |
| Role/seniority alignment | 20% | O*NET / JD mapping |
| Readability & 6-sec scan | 15% | top-third content check |
| Formatting/ATS-parseability | 10% | format-risk flags |
| Consistency & error-free | 10% | error count |

## Process
1. For each dimension, compute score with an explicit rationale and evidence pointer.
2. Penalize keyword-stuffing (coverage high but unnatural density) — do not reward gaming.
3. Compute weighted total; assign verdict band (≥80 strong / 60–79 competitive / <60 needs work).

## Outputs
Dimension table (score, weight, evidence) + weighted total + verdict.

## Quality Gate
- Every dimension has a numeric score and a concrete evidence pointer.
- Keyword-stuffing check applied.
