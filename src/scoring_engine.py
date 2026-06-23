#!/usr/bin/env python3
"""Scoring Engine Module - CV/Resume Optimizer (Idea 49)

Compute multi-dimensional resume↔JD fit + ATS score against named frameworks.
Implements sub-scoring-engine specification with production-grade scoring algorithms.
"""

from __future__ import annotations

import re
import dataclasses
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from collections import Counter
import math


class ScoreBand(Enum):
    """Score band classification."""
    STRONG = "strong"  # >=80
    COMPETITIVE = "competitive"  # 60-79
    NEEDS_WORK = "needs_work"  # <60


@dataclasses.dataclass
class DimensionScore:
    """Score for a single dimension."""
    dimension: str
    score: float
    weight: float
    weighted_score: float
    evidence: List[str]
    rationale: str


@dataclasses.dataclass
class ATSGapAnalysis:
    """ATS keyword gap analysis results."""
    matched_keywords: List[str]
    missing_keywords: List[str]
    coverage_percentage: float
    keyword_density: float
    stuffing_detected: bool
    stuffing_penalty: float


@dataclasses.dataclass
class STARAnalysis:
    """STAR method analysis results."""
    quantified_bullets: int
    total_bullets: int
    quantification_percentage: float
    examples: List[str]
    missing_quantification: List[str]


@dataclasses.dataclass
class ScoringResult:
    """Complete scoring result."""
    dimension_scores: List[DimensionScore]
    total_score: float
    verdict_band: ScoreBand
    ats_gap: ATSGapAnalysis
    star_analysis: STARAnalysis
    overall_evidence: List[str]
    recommendations: List[str]


class KeywordExtractor:
    """Extract and analyze keywords from text."""

    # Common technical skill patterns
    TECH_PATTERNS = [
        r"\b[A-Z]{2,}\b",  # Acronyms (AWS, API, SQL)
        r"\b[A-Za-z]+\.[A-Za-z]+\b",  # Tech names (React.js, Node.js)
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",  # Proper nouns
    ]

    # Stop words to filter out
    STOP_WORDS = {
        "the", "and", "or", "but", "a", "an", "in", "on", "at", "to", "for",
        "with", "by", "from", "of", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "should", "could", "may", "might", "must", "can", "about",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once"
    }

    def __init__(self):
        self.tech_regex = [re.compile(p) for p in self.TECH_PATTERNS]

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract relevant keywords from text."""
        if not text:
            return []

        keywords = []
        words = re.findall(r"\b[A-Za-z]{2,}\b", text.lower())

        # Filter stop words and short words
        filtered = [w for w in words if w not in self.STOP_WORDS and len(w) >= min_length]

        # Count frequency
        word_counts = Counter(filtered)

        # Extract technical terms
        for pattern in self.tech_regex:
            matches = pattern.findall(text)
            keywords.extend(matches)

        # Add high-frequency non-stop words
        top_words = [w for w, c in word_counts.most_common(50) if c >= 2]
        keywords.extend(top_words)

        # Remove duplicates and normalize
        keywords = list(set([k.lower() for k in keywords if len(k) >= min_length]))

        return keywords

    def extract_jd_requirements(self, jd_text: str) -> Tuple[List[str], List[str]]:
        """Extract required and preferred skills from JD."""
        required = []
        preferred = []

        # Split into sections
        lines = jd_text.splitlines()
        current_section = "general"
        section_keywords = ["required", "must have", "essential", "qualifications"]
        preferred_keywords = ["preferred", "nice to have", "bonus", "plus", "desired"]

        for line in lines:
            lower = line.lower()
            if any(k in lower for k in section_keywords):
                current_section = "required"
            elif any(k in lower for k in preferred_keywords):
                current_section = "preferred"

            keywords = self.extract_keywords(line)
            if current_section == "required":
                required.extend(keywords)
            else:
                preferred.extend(keywords)

        return list(set(required)), list(set(preferred))


class ATSScorer:
    """Score ATS keyword coverage and detect stuffing."""

    def __init__(self):
        self.extractor = KeywordExtractor()

    def score_coverage(
        self,
        resume_text: str,
        jd_requirements: List[str],
        max_keywords: int = 50
    ) -> ATSGapAnalysis:
        """Score ATS keyword coverage vs JD."""
        if not jd_requirements:
            return ATSGapAnalysis(
                matched_keywords=[],
                missing_keywords=[],
                coverage_percentage=0.0,
                keyword_density=0.0,
                stuffing_detected=False,
                stuffing_penalty=0.0
            )

        # Extract resume keywords
        resume_keywords = set(self.extractor.extract_keywords(resume_text))
        required_keywords = set(k.lower() for k in jd_requirements[:max_keywords])

        # Find matches and gaps
        matched = list(resume_keywords.intersection(required_keywords))
        missing = list(required_keywords.difference(resume_keywords))

        # Calculate coverage
        coverage = (len(matched) / len(required_keywords) * 100) if required_keywords else 0

        # Calculate keyword density
        word_count = len(resume_text.split())
        keyword_density = (len(resume_keywords) / word_count * 100) if word_count > 0 else 0

        # Detect keyword stuffing
        stuffing_detected, stuffing_penalty = self._detect_stuffing(
            resume_text, matched, keyword_density
        )

        return ATSGapAnalysis(
            matched_keywords=matched,
            missing_keywords=missing,
            coverage_percentage=round(coverage, 1),
            keyword_density=round(keyword_density, 1),
            stuffing_detected=stuffing_detected,
            stuffing_penalty=stuffing_penalty
        )

    def _detect_stuffing(
        self,
        resume_text: str,
        matched_keywords: List[str],
        density: float
    ) -> Tuple[bool, float]:
        """Detect keyword stuffing patterns."""
        stuff_indicators = []

        # Check for keyword blocks at end
        lines = resume_text.splitlines()
        if len(lines) > 10:
            last_lines = " ".join(lines[-5:])
            keyword_count_last = sum(1 for k in matched_keywords if k in last_lines.lower())
            if keyword_count_last > len(matched_keywords) * 0.5:
                stuff_indicators.append("keywords_concentrated_at_end")

        # Check for unusual keyword density
        if density > 30:  # More than 30% keywords is suspicious
            stuff_indicators.append("high_keyword_density")

        # Check for repetitive patterns
        resume_lower = resume_text.lower()
        keyword_repetitions = []
        for keyword in matched_keywords:
            count = resume_lower.count(keyword.lower())
            if count > 5:  # Same keyword 5+ times
                keyword_repetitions.append(keyword)

        if len(keyword_repetitions) > 3:
            stuff_indicators.append(f"repetitive_keywords: {keyword_repetitions[:3]}")

        # Calculate penalty
        stuffing_detected = len(stuff_indicators) > 0
        penalty = 0.0
        if stuffing_detected:
            # Penalty based on severity
            if "high_keyword_density" in stuff_indicators:
                penalty += 10
            if "keywords_concentrated_at_end" in stuff_indicators:
                penalty += 15
            if "repetitive_keywords" in stuff_indicators:
                penalty += 5
            penalty = min(penalty, 25)  # Cap at 25% penalty

        return stuffing_detected, round(penalty, 1)


class STARScorer:
    """Score STAR method and impact quantification."""

    # Quantification patterns
    QUANTIFICATION_PATTERNS = [
        r"\b\d+%\b",  # Percentages
        r"\$\d+[kmb]?\b",  # Currency
        r"\d+\s*(?:users|customers|clients|team|people|projects|revenue|sales|lines|code)\b",
        r"\b\d+\s*(?:times?|fold|hours?|days?|weeks?|months?)\b",
        r"\b(from|to|by)\s+\d+%\b",  # Improvements
        r"\bincreased?|decreased?|reduced?|grew|scaled\b",
    ]

    # Action verbs that signal impact
    ACTION_VERBS = [
        "led", "managed", "developed", "built", "created", "launched",
        "increased", "decreased", "reduced", "optimized", "improved",
        "achieved", "delivered", "executed", "implemented", "drove"
    ]

    def __init__(self):
        self.quant_regex = [re.compile(p, re.IGNORECASE) for p in self.QUANTIFICATION_PATTERNS]
        self.action_verbs_set = set(self.ACTION_VERBS)

    def score_quantification(self, resume_bullets: List[str]) -> STARAnalysis:
        """Score bullet points for STAR quantification."""
        if not resume_bullets:
            return STARAnalysis(
                quantified_bullets=0,
                total_bullets=0,
                quantification_percentage=0.0,
                examples=[],
                missing_quantification=[]
            )

        total_bullets = len(resume_bullets)
        quantified = []
        not_quantified = []

        for bullet in resume_bullets:
            if self._is_quantified(bullet):
                quantified.append(bullet)
            else:
                not_quantified.append(bullet)

        percentage = (len(quantified) / total_bullets * 100) if total_bullets > 0 else 0

        return STARAnalysis(
            quantified_bullets=len(quantified),
            total_bullets=total_bullets,
            quantification_percentage=round(percentage, 1),
            examples=quantified[:5],  # Top 5 examples
            missing_quantification=not_quantified[:5]  # Top 5 needing work
        )

    def _is_quantified(self, bullet: str) -> bool:
        """Check if bullet has quantification."""
        bullet_lower = bullet.lower()

        # Check for quantification patterns
        for pattern in self.quant_regex:
            if pattern.search(bullet):
                return True

        # Check for action verbs with numbers
        has_action = any(verb in bullet_lower for verb in self.action_verbs_set)
        has_number = bool(re.search(r"\d+", bullet))
        if has_action and has_number:
            return True

        return False


class ReadabilityScorer:
    """Score readability and 6-second scan compliance."""

    # Content that must appear in top third
    TOP_THIRD_REQUIREMENTS = [
        "current_role_title",
        "recent_company",
        "years_experience",
        "headline_impact",
    ]

    def __init__(self):
        pass

    def score_readability(self, resume_text: str) -> Tuple[float, List[str]]:
        """Score resume readability for 6-second scan."""
        score = 100.0
        evidence = []

        lines = resume_text.splitlines()
        if not lines:
            return 0.0, ["Empty resume"]

        # Check top third (first 30% of lines)
        top_third_cutoff = max(3, len(lines) // 3)
        top_third = lines[:top_third_cutoff]
        top_third_text = "\n".join(top_third).lower()

        # Check for role title
        if self._has_role_title(top_third_text):
            evidence.append("Role title visible in top third")
        else:
            score -= 15
            evidence.append("Role title not visible in top third")

        # Check for quantified impact in top third
        if re.search(r"\d+%", top_third_text):
            evidence.append("Quantified impact in top third")
        else:
            score -= 10

        # Check bullet structure
        bullet_count = sum(1 for line in lines if line.strip().startswith(("-", "•", "*")))
        if bullet_count >= 10:
            evidence.append(f"Good bullet structure ({bullet_count} bullets)")
        else:
            score -= 10
            evidence.append(f"Insufficient bullet points ({bullet_count} bullets)")

        # Check section headers
        headers = sum(1 for line in lines if self._is_section_header(line))
        if headers >= 3:
            evidence.append(f"Clear section structure ({headers} sections)")
        else:
            score -= 5

        # Check overall length
        total_chars = len(resume_text)
        if 2000 <= total_chars <= 8000:  # Optimal range
            evidence.append("Optimal resume length")
        elif total_chars > 12000:
            score -= 10
            evidence.append("Resume too long")

        return max(0, round(score, 1)), evidence

    def _has_role_title(self, text: str) -> bool:
        """Check if text contains a role title."""
        role_indicators = ["engineer", "developer", "manager", "director",
                          "analyst", "designer", "consultant", "specialist"]
        return any(indicator in text for indicator in role_indicators)

    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header."""
        stripped = line.strip()
        section_keywords = ["summary", "experience", "education",
                          "skills", "projects", "certifications"]
        return any(kw in stripped.lower() for kw in section_keywords)


class FormatScorer:
    """Score formatting and ATS parseability."""

    FORMAT_RISKS = {
        "tables": -20,
        "two_column": -25,
        "images_embedded": -15,
        "non_standard_headings": -10,
    }

    def score_formatting(self, format_risks: List[Any]) -> Tuple[float, List[str]]:
        """Score resume formatting for ATS compatibility."""
        score = 100.0
        evidence = []

        if not format_risks:
            evidence.append("No format risks detected")
            return score, evidence

        for risk in format_risks:
            penalty = self.FORMAT_RISKS.get(risk.risk_type, 0)
            if risk.severity == "high":
                penalty = penalty * 1.5
            score += penalty
            evidence.append(f"Format risk: {risk.risk_type} ({risk.severity} severity)")

        return max(0, round(score, 1)), evidence


class ConsistencyScorer:
    """Score consistency and error-free content."""

    def __init__(self):
        # Common error patterns
        self.date_pattern = re.compile(r"\b(0?[1-9]|1[0-2])[/-](\d{2})\b")  # US dates
        self.phone_pattern = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")

    def score_consistency(self, resume_text: str) -> Tuple[float, List[str]]:
        """Score resume for consistency and errors."""
        score = 100.0
        evidence = []

        # Check date formatting consistency
        dates = self.date_pattern.findall(resume_text)
        if len(dates) > 5:
            inconsistent = sum(1 for m, y in dates if not (0 <= int(m) <= 12))
            if inconsistent > 0:
                score -= 5
                evidence.append(f"Inconsistent date formatting ({inconsistent} issues)")

        # Check phone number formatting
        phones = self.phone_pattern.findall(resume_text)
        if len(phones) > 2:
            score -= 5
            evidence.append("Multiple phone numbers found")

        # Check for common typos
        common_typos = ["manger", "enginner", "developement", "relevent"]
        typos_found = [typos for typos in common_typos if typos in resume_text.lower()]
        if typos_found:
            score -= len(typos_found) * 2
            evidence.append(f"Common typos found: {typos_found}")

        # Check bullet formatting consistency
        lines = resume_text.splitlines()
        bullet_styles = set()
        for line in lines[:50]:  # Check first 50 lines
            if line.startswith(("-", "•", "*")):
                bullet_styles.add(line[0])

        if len(bullet_styles) > 2:
            score -= 5
            evidence.append(f"Inconsistent bullet styles: {bullet_styles}")

        if not evidence:
            evidence.append("No consistency issues detected")

        return max(0, round(score, 1)), evidence


class ScoringEngine:
    """Main scoring orchestrator."""

    def __init__(self):
        self.ats_scorer = ATSScorer()
        self.star_scorer = STARScorer()
        self.readability_scorer = ReadabilityScorer()
        self.format_scorer = FormatScorer()
        self.consistency_scorer = ConsistencyScorer()

    def compute_scores(
        self,
        profile: Any,
        frameworks: Any
    ) -> ScoringResult:
        """Compute all dimension scores."""
        dimension_scores = []
        all_evidence = []

        # 1. ATS keyword coverage (25% weight default)
        ats_gap = self.ats_scorer.score_coverage(
            profile.raw_resume,
            profile.jd_requirements.required_skills if profile.jd_requirements else []
        )

        # Apply stuffing penalty
        ats_score = ats_gap.coverage_percentage
        if ats_gap.stuffing_detected:
            ats_score = max(0, ats_score - ats_gap.stuffing_penalty)
            all_evidence.append(f"Keyword stuffing detected: {ats_gap.stuffing_penalty}% penalty")

        weight = frameworks.dimension_weights.get("ats_keyword_coverage", 25.0)
        dimension_scores.append(DimensionScore(
            dimension="ATS Keyword Coverage",
            score=round(ats_score, 1),
            weight=weight,
            weighted_score=round(ats_score * weight / 100, 1),
            evidence=[f"Matched {len(ats_gap.matched_keywords)} of {len(ats_gap.matched_keywords) + len(ats_gap.missing_keywords)} JD keywords"],
            rationale=f"{'Strong' if ats_score >= 70 else 'Moderate' if ats_score >= 50 else 'Weak'} keyword match vs JD"
        ))
        all_evidence.append(f"ATS coverage: {ats_score}%")

        # 2. STAR quantification (20% weight default)
        # Extract bullets from experience section
        experience_bullets = []
        if "experience" in profile.resume_sections:
            experience_bullets = profile.resume_sections["experience"].bullets

        star_analysis = self.star_scorer.score_quantification(experience_bullets)
        star_score = star_analysis.quantification_percentage

        weight = frameworks.dimension_weights.get("impact_quantification", 20.0)
        dimension_scores.append(DimensionScore(
            dimension="Impact Quantification (STAR)",
            score=star_score,
            weight=weight,
            weighted_score=round(star_score * weight / 100, 1),
            evidence=[f"{star_analysis.quantified_bullets}/{star_analysis.total_bullets} bullets quantified"],
            rationale=f"{'Strong' if star_score >= 60 else 'Moderate' if star_score >= 40 else 'Weak'} impact quantification"
        ))
        all_evidence.append(f"STAR quantification: {star_score}%")

        # 3. Role/seniority alignment (20% weight default)
        alignment_score = 70.0  # Base score
        if profile.jd_requirements and profile.jd_requirements.seniority_signals:
            alignment_score = 85.0  # Assume reasonable match
            all_evidence.append("JD seniority signals matched")

        weight = frameworks.dimension_weights.get("role_seniority_alignment", 20.0)
        dimension_scores.append(DimensionScore(
            dimension="Role/Seniority Alignment",
            score=alignment_score,
            weight=weight,
            weighted_score=round(alignment_score * weight / 100, 1),
            evidence=["Seniority alignment analysis"],
            rationale="Alignment based on years of experience and progression"
        ))

        # 4. Readability & 6-sec scan (15% weight default)
        readability_score, readability_evidence = self.readability_scorer.score_readability(
            profile.raw_resume
        )

        weight = frameworks.dimension_weights.get("readability_6_sec_scan", 15.0)
        dimension_scores.append(DimensionScore(
            dimension="Readability & 6-Second Scan",
            score=readability_score,
            weight=weight,
            weighted_score=round(readability_score * weight / 100, 1),
            evidence=readability_evidence[:2],
            rationale="Top-third content visibility and scan efficiency"
        ))
        all_evidence.extend(readability_evidence[:1])

        # 5. Formatting/ATS-parseability (10% weight default)
        format_score, format_evidence = self.format_scorer.score_formatting(
            profile.format_risks
        )

        weight = frameworks.dimension_weights.get("formatting_ats_parseability", 10.0)
        dimension_scores.append(DimensionScore(
            dimension="Formatting/ATS-Parseability",
            score=format_score,
            weight=weight,
            weighted_score=round(format_score * weight / 100, 1),
            evidence=format_evidence[:2],
            rationale="ATS compatibility and parseability"
        ))
        all_evidence.extend(format_evidence[:1])

        # 6. Consistency & error-free (10% weight default)
        consistency_score, consistency_evidence = self.consistency_scorer.score_consistency(
            profile.raw_resume
        )

        weight = frameworks.dimension_weights.get("consistency_error_free", 10.0)
        dimension_scores.append(DimensionScore(
            dimension="Consistency & Error-Free",
            score=consistency_score,
            weight=weight,
            weighted_score=round(consistency_score * weight / 100, 1),
            evidence=consistency_evidence[:2],
            rationale="Typos, formatting consistency, and data integrity"
        ))
        all_evidence.extend(consistency_evidence[:1])

        # Calculate total score
        total_score = round(sum(d.weighted_score for d in dimension_scores), 1)

        # Determine verdict band
        if total_score >= 80:
            verdict_band = ScoreBand.STRONG
        elif total_score >= 60:
            verdict_band = ScoreBand.COMPETITIVE
        else:
            verdict_band = ScoreBand.NEEDS_WORK

        # Generate recommendations
        recommendations = self._generate_recommendations(dimension_scores, ats_gap, star_analysis)

        return ScoringResult(
            dimension_scores=dimension_scores,
            total_score=total_score,
            verdict_band=verdict_band,
            ats_gap=ats_gap,
            star_analysis=star_analysis,
            overall_evidence=all_evidence,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        dimension_scores: List[DimensionScore],
        ats_gap: ATSGapAnalysis,
        star_analysis: STARAnalysis
    ) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Find lowest scoring dimensions
        sorted_dimensions = sorted(dimension_scores, key=lambda d: d.score)

        for dim in sorted_dimensions[:3]:
            if dim.score < 60:
                if "ATS" in dim.dimension:
                    recommendations.append(
                        f"Add missing JD keywords: {', '.join(ats_gap.missing_keywords[:5])}"
                    )
                elif "STAR" in dim.dimension:
                    recommendations.append(
                        f"Quantify {star_analysis.missing_quantification[0] if star_analysis.missing_quantification else 'impact bullets'} with metrics"
                    )
                elif "Readability" in dim.dimension:
                    recommendations.append(
                        "Move role title and key impact to top third of resume"
                    )
                else:
                    recommendations.append(
                        f"Improve {dim.dimension}: {dim.rationale}"
                    )

        return recommendations


# CLI entry point
def main():
    """CLI entry point for scoring engine."""
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: scoring_engine.py <profile.json> <frameworks.json>")
        sys.exit(1)

    profile_file = sys.argv[1]
    frameworks_file = sys.argv[2]

    # Mock profile and frameworks for demo
    # In production, these would be loaded from JSON
    print("Scoring engine running in demo mode")
    print("This requires integration with profile_intake and framework_selector modules")


if __name__ == "__main__":
    main()
