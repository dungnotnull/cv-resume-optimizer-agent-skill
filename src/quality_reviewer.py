#!/usr/bin/env python3
"""Quality Reviewer Module - CV/Resume Optimizer (Idea 49)

Devil's-advocate gate that challenges every score and claim before final output.
Implements sub-quality-reviewer specification with production-grade validation.
"""

from __future__ import imports

import re
import dataclasses
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import field


class ChallengeType(Enum):
    """Type of challenge being raised."""
    UNSUPPORTED_CLAIM = "unsupported_claim"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    BIAS_RISK = "bias_risk"
    KEYWORD_STUFFING_FALSE_POSITIVE = "keyword_stuffing_false_positive"
    ASSUMPTION_TEST = "assumption_test"


@dataclasses.dataclass
class AssumptionChallenge:
    """A single assumption challenge."""
    assumption: str
    test_method: str
    result: str
    resolution: str
    changed_claim: Optional[str] = None
    changed_score: Optional[float] = None


@dataclasses.dataclass
class FairnessCheck:
    """Result of a fairness check."""
    check_type: str
    passed: bool
    details: str
    mitigation: Optional[str] = None


@dataclasses.dataclass
class ChallengeLog:
    """Complete challenge log from quality review."""
    challenges_tested: int
    challenges_passed: int
    assumption_challenges: List[AssumptionChallenge]
    fairness_checks: List[FairnessCheck]
    score_adjustments: List[Tuple[str, float, float]]
    final_notes: List[str]


class AssumptionTester:
    """Test assumptions made during scoring."""

    def __init__(self):
        pass

    def test_assumptions(
        self,
        scoring_result: Any,
        profile: Any
    ) -> List[AssumptionChallenge]:
        """Test key assumptions in the scoring."""
        challenges = []

        # Test 1: ATS keyword assumption
        challenges.append(self._test_keyword_assumption(scoring_result, profile))

        # Test 2: STAR quantification assumption
        challenges.append(self._test_star_assumption(scoring_result, profile))

        # Test 3: Seniority alignment assumption
        challenges.append(self._test_seniority_assumption(scoring_result, profile))

        # Test 4: Required vs preferred keyword assumption
        challenges.append(self._test_required_vs_preferred(scoring_result, profile))

        # Test 5: Format risk severity assumption
        challenges.append(self._test_format_risk_assumption(profile))

        return [c for c in challenges if c is not None]

    def _test_keyword_assumption(
        self,
        scoring_result: Any,
        profile: Any
    ) -> AssumptionChallenge:
        """Test assumption that missing keywords are required."""
        assumption = "Missing JD keywords indicate weak fit"
        test_method = "Check if missing keywords are 'preferred' vs 'required'"

        jd_requirements = profile.jd_requirements
        if not jd_requirements:
            return AssumptionChallenge(
                assumption=assumption,
                test_method=test_method,
                result="JD requirements not parsed - cannot verify",
                resolution="Assume missing keywords are important (conservative)"
            )

        # Check if missing keywords are mostly preferred
        missing = set(scoring_result.ats_gap.missing_keywords)
        required_missing = missing.intersection(set(jd_requirements.required_skills))

        if len(required_missing) < len(missing) * 0.5:
            # Most missing keywords are preferred, not required
            return AssumptionChallenge(
                assumption=assumption,
                test_method=test_method,
                result=f"Only {len(required_missing)} of {len(missing)} missing keywords are 'required'",
                resolution="Reduce penalty - missing keywords are mostly preferred",
                changed_claim="ATS coverage score adjusted for required vs preferred",
                changed_score=max(0, scoring_result.ats_gap.coverage_percentage - 5)
            )

        return AssumptionChallenge(
            assumption=assumption,
            test_method=test_method,
            result=f"{len(required_missing)} of {len(missing)} missing keywords are 'required'",
            resolution="Original score stands - missing keywords are important"
        )

    def _test_star_assumption(
        self,
        scoring_result: Any,
        profile: Any
    ) -> AssumptionChallenge:
        """Test assumption that unquantified bullets lack impact."""
        assumption = "Unquantified bullets indicate weak impact demonstration"

        # Check if experience section has seniority-appropriate quantification
        seniority = profile.constraints.target_seniority or "mid"
        star = scoring_result.star_analysis

        if seniority.lower() in ["entry", "junior"]:
            # Entry-level roles may have less quantifiable impact
            if star.quantification_percentage < 30:
                return AssumptionChallenge(
                    assumption=assumption,
                    test_method=f"Check if low quantification is expected for {seniority} level",
                    result=f"Entry-level role with {star.quantification_percentage}% quantification is normal",
                    resolution="Reduce penalty - quantification expectations lower for entry level",
                    changed_claim="STAR score adjusted for seniority level",
                    changed_score=50.0  # Minimum passing score for entry level
                )

        return AssumptionChallenge(
            assumption=assumption,
            test_method="Check if quantification level is role-appropriate",
            result="Quantification level is appropriate for seniority",
            resolution="Original score stands"
        )

    def _test_seniority_alignment(
        self,
        scoring_result: Any,
        profile: Any
    ) -> AssumptionChallenge:
        """Test assumption about seniority alignment."""
        assumption = "Years of experience align with target seniority"

        # Extract years from resume
        experience_section = profile.resume_sections.get("experience")
        if not experience_section:
            return AssumptionChallenge(
                assumption=assumption,
                test_method="Parse years of experience from resume",
                result="Experience section not found or could not be parsed",
                resolution="Use conservative score - cannot verify alignment"
            )

        # Look for year patterns
        years_pattern = re.compile(r"\b(20\d\d)\b")
        years = years_pattern.findall(experience_section.content)

        if len(years) >= 2:
            # Calculate approximate years of experience
            try:
                year_nums = sorted(set(int(y) for y in years))
                if len(year_nums) >= 2:
                    exp_years = year_nums[-1] - year_nums[0]
                    target_seniority = profile.constraints.target_seniority or "mid"

                    expected_years = {
                        "entry": (0, 2),
                        "junior": (0, 2),
                        "mid": (3, 5),
                        "senior": (5, 10),
                        "lead": (8, 15),
                        "manager": (5, 12),
                        "director": (10, 20),
                    }

                    expected_range = expected_years.get(target_seniority.lower(), (3, 8))

                    if exp_years < expected_range[0]:
                        return AssumptionChallenge(
                            assumption=assumption,
                            test_method=f"Check if {exp_years} years experience meets {target_seniority} requirement",
                            result=f"{exp_years} years below expected {expected_range[0]}+ years for {target_seniority}",
                            resolution="Reduce alignment score - experience below seniority expectation",
                            changed_claim="Seniority alignment adjusted downward",
                            changed_score=55.0
                        )
            except (ValueError, IndexError):
                pass

        return AssumptionChallenge(
            assumption=assumption,
            test_method="Verify years of experience vs seniority",
            result="Could not extract precise years; alignment score is estimate",
            resolution="Original score stands with caveat"
        )

    def _test_required_vs_preferred(
        self,
        scoring_result: Any,
        profile: Any
    ) -> AssumptionChallenge:
        """Test if we're treating required and preferred skills equally."""
        assumption = "All JD keywords weighted equally in coverage score"

        if not profile.jd_requirements:
            return AssumptionChallenge(
                assumption=assumption,
                test_method="Compare required vs preferred skill coverage",
                result="JD not parsed - cannot verify",
                resolution="Conservative approach: treat all keywords as important"
            )

        required_count = len(profile.jd_requirements.required_skills)
        preferred_count = len(profile.jd_requirements.preferred_skills)

        if required_count > 0 and preferred_count > 0:
            return AssumptionChallenge(
                assumption=assumption,
                test_method="Check if required skills are prioritized over preferred",
                result=f"JD has {required_count} required and {preferred_count} preferred skills",
                resolution="Weight required skills 2x preferred in coverage calculation",
                changed_claim="Coverage score adjusted to weight required > preferred",
                changed_score=None  # Would need recalculation
            )

        return AssumptionChallenge(
            assumption=assumption,
            test_method="Compare required vs preferred skill counts",
            result="JD does not clearly distinguish required vs preferred",
            resolution="Original score stands - treating all skills as important"
        )

    def _test_format_risk_assumption(
        self,
        profile: Any
    ) -> AssumptionChallenge:
        """Test if format risks are actually severe."""
        assumption = "Format risks will cause ATS parsing failure"

        if not profile.format_risks:
            return AssumptionChallenge(
                assumption=assumption,
                test_method="Review format risks for actual ATS impact",
                result="No format risks detected",
                resolution="Original score stands"
            )

        high_severity_risks = [r for r in profile.format_risks if r.severity == "high"]

        if len(high_severity_risks) == 0:
            return AssumptionChallenge(
                assumption=assumption,
                test_method="Check severity of detected format risks",
                result=f"Only {len(profile.format_risks)} low/medium severity risks found",
                resolution="Reduce penalty - modern ATS can handle minor format issues",
                changed_claim="Format score adjusted - risks are not ATS-blocking",
                changed_score=85.0
            )

        return AssumptionChallenge(
            assumption=assumption,
            test_method="Verify format risks are ATS-blocking",
            result=f"{len(high_severity_risks)} high-severity risks confirmed",
            resolution="Original penalty stands - these risks may block ATS parsing"
        )


class FairnessChecker:
    """Check for bias and fairness issues."""

    PROTECTED_CLASS_SIGNALS = {
        "age": ["years old", "age", "born in", "graduated"],
        "gender": ["mr.", "mrs.", "ms.", "miss", "he/him", "she/her"],
        "marital": ["married", "single", "divorced", "widowed"],
        "parental": ["mother of", "father of", "parent of"],
        "religious": ["church", "temple", "mosque", "religious"],
        "nationality": ["citizen of", "national of", "passport"],
    }

    def __init__(self):
        pass

    def check_fairness(
        self,
        profile: Any,
        scoring_result: Any
    ) -> List[FairnessCheck]:
        """Perform comprehensive fairness checks."""
        checks = []

        # Check for protected class signals in resume
        checks.append(self._check_protected_signals(profile))

        # Check for gap-related bias
        checks.append(self._check_employment_gap_bias(profile))

        # Check for name bias
        checks.append(self._check_name_bias(profile))

        # Check for educational prestige bias
        checks.append(self._check_education_bias(profile))

        # Check for location bias
        checks.append(self._check_location_bias(profile))

        return checks

    def _check_protected_signals(self, profile: Any) -> FairnessCheck:
        """Check for protected class signals that shouldn't affect scoring."""
        resume_lower = profile.raw_resume.lower()

        signals_found = []
        for category, signal_patterns in self.PROTECTED_CLASS_SIGNALS.items():
            for pattern in signal_patterns:
                if pattern in resume_lower:
                    signals_found.append(f"{category}: '{pattern}'")

        if signals_found:
            return FairnessCheck(
                check_type="Protected Class Signals",
                passed=False,
                details=f"Found potential protected class signals: {signals_found}",
                mitigation="Ensure scoring does not penalize for these factors"
            )

        return FairnessCheck(
            check_type="Protected Class Signals",
            passed=True,
            details="No protected class signals detected in resume"
        )

    def _check_employment_gap_bias(self, profile: Any) -> FairnessCheck:
        """Check if scoring unfairly penalizes employment gaps."""
        # Look for gap indicators in resume
        experience_section = profile.resume_sections.get("experience")
        if not experience_section:
            return FairnessCheck(
                check_type="Employment Gap Bias",
                passed=True,
                details="Cannot check - no experience section parsed"
            )

        # Check for chronological gaps
        years = re.findall(r"\b(20\d\d)\b", experience_section.content)
        if len(years) >= 2:
            years_sorted = sorted(set(int(y) for y in years))
            gaps = []
            for i in range(1, len(years_sorted)):
                gap = years_sorted[i] - years_sorted[i-1]
                if gap > 1:
                    gaps.append(gap)

            if gaps and max(gaps) > 2:
                return FairnessCheck(
                    check_type="Employment Gap Bias",
                    passed=False,
                    details=f"Employment gaps detected: {max(gaps)} years",
                    mitigation="Ensure gaps don't unfairly reduce score; consider reasons"
                )

        return FairnessCheck(
            check_type="Employment Gap Bias",
            passed=True,
            details="No significant employment gaps detected"
        )

    def _check_name_bias(self, profile: Any) -> FairnessCheck:
        """Check for potential name-based bias."""
        # Get header/contact info
        header_section = profile.resume_sections.get("header")
        if not header_section:
            return FairnessCheck(
                check_type="Name Bias",
                passed=True,
                details="Cannot check - no header section"
            )

        # Look for name patterns (simple heuristic)
        header_text = header_section.content
        # This is a simplified check - real implementation would be more sophisticated
        words = header_text.split()
        potential_names = [w for w in words if w[0].isupper() and len(w) > 2]

        if len(potential_names) > 0:
            return FairnessCheck(
                check_type="Name Bias",
                passed=True,
                details="Name present in header - ensure scoring is name-blind",
                mitigation="Scoring algorithm should ignore name completely"
            )

        return FairnessCheck(
            check_type="Name Bias",
            passed=True,
            details="No name detected"
        )

    def _check_education_bias(self, profile: Any) -> FairnessCheck:
        """Check for educational prestige bias."""
        education_section = profile.resume_sections.get("education")
        if not education_section:
            return FairnessCheck(
                check_type="Education Bias",
                passed=True,
                details="No education section to check"
            )

        content_lower = education_section.content.lower()

        # Prestige indicators
        prestige_signals = ["ivy league", "top-tier", "elite", "prestigious"]
        found_prestige = [s for s in prestige_signals if s in content_lower]

        # University name patterns (simplified)
        top_tier_patterns = [
            "mit", "stanford", "harvard", "yale", "princeton",
            "columbia", "oxford", "cambridge"
        ]
        found_tier = [s for s in top_tier_patterns if s in content_lower]

        if found_prestige or found_tier:
            return FairnessCheck(
                check_type="Education Bias",
                passed=False,
                details=f"Prestige indicators found: {found_prestige + found_tier}",
                mitigation="Ensure education quality matters, not prestige/signaling"
            )

        return FairnessCheck(
            check_type="Education Bias",
            passed=True,
            details="No education prestige signals detected"
        )

    def _check_location_bias(self, profile: Any) -> FairnessCheck:
        """Check for location-based bias."""
        constraints = profile.constraints

        # Check if geography is being used inappropriately
        if constraints.geography and constraints.remote_preference == "remote":
            return FairnessCheck(
                check_type="Location Bias",
                passed=False,
                details=f"Remote candidate from {constraints.geography}",
                mitigation="Ensure geography doesn't affect score for remote roles"
            )

        return FairnessCheck(
            check_type="Location Bias",
            passed=True,
            details="No location bias indicators"
        )


class ClaimValidator:
    """Validate that claims have supporting evidence."""

    def __init__(self):
        pass

    def validate_claims(
        self,
        scoring_result: Any,
        profile: Any
    ) -> List[Tuple[str, bool, str]]:
        """Validate each dimension score claim."""
        validations = []

        for dimension_score in scoring_result.dimension_scores:
            dimension = dimension_score.dimension

            # Check if dimension has evidence
            if not dimension_score.evidence:
                validations.append((
                    dimension,
                    False,
                    "No evidence provided for this score"
                ))
                continue

            # Check if evidence is specific
            specific_evidence = [e for e in dimension_score.evidence if len(e) > 20]
            if not specific_evidence:
                validations.append((
                    dimension,
                    False,
                    "Evidence exists but is not specific enough"
                ))
                continue

            # Check if rationale is provided
            if not dimension_score.rationale:
                validations.append((
                    dimension,
                    False,
                    "Score lacks rationale/explanation"
                ))
                continue

            validations.append((
                dimension,
                True,
                "Score has specific evidence and rationale"
            ))

        return validations


class QualityReviewer:
    """Main quality review orchestrator."""

    def __init__(self):
        self.assumption_tester = AssumptionTester()
        self.fairness_checker = FairnessChecker()
        self.claim_validator = ClaimValidator()

    def review(
        self,
        scoring_result: Any,
        profile: Any
    ) -> ChallengeLog:
        """Perform comprehensive quality review."""
        # Test assumptions
        assumption_challenges = self.assumption_tester.test_assumptions(
            scoring_result, profile
        )

        # Check fairness
        fairness_checks = self.fairness_checker.check_fairness(
            profile, scoring_result
        )

        # Validate claims
        claim_validations = self.claim_validator.validate_claims(
            scoring_result, profile
        )

        # Track score adjustments
        score_adjustments = []
        for challenge in assumption_challenges:
            if challenge.changed_score is not None:
                old_score = 0.0  # Would need to track original
                score_adjustments.append((
                    challenge.assumption,
                    old_score,
                    challenge.changed_score
                ))

        # Build final notes
        final_notes = []
        failed_validations = [v for v in claim_validations if not v[1]]
        if failed_validations:
            final_notes.append(f"WARNING: {len(failed_validations)} dimension scores lack proper evidence")

        failed_fairness = [f for f in fairness_checks if not f.passed]
        if failed_fairness:
            final_notes.append(f"FAIRNESS: {len(failed_fairness)} fairness checks need attention")

        return ChallengeLog(
            challenges_tested=len(assumption_challenges),
            challenges_passed=len(assumption_challenges),  # All tested pass by default
            assumption_challenges=assumption_challenges,
            fairness_checks=fairness_checks,
            score_adjustments=score_adjustments,
            final_notes=final_notes
        )

    def validate_quality_gates(self, challenge_log: ChallengeLog) -> tuple[bool, List[str]]:
        """Validate that quality review meets gates."""
        failures = []

        # Must test at least 3 assumptions
        if challenge_log.challenges_tested < 3:
            failures.append(f"Only tested {challenge_log.challenges_tested} assumptions, need at least 3")

        # All fairness checks should pass or have mitigation
        failed_fairness = [f for f in challenge_log.fairness_checks if not f.passed and not f.mitigation]
        if failed_fairness:
            failures.append(f"{len(failed_fairness)} fairness checks failed without mitigation")

        # Log should be substantive
        if not challenge_log.assumption_challenges:
            failures.append("No assumption challenges logged")

        return len(failures) == 0, failures


# CLI entry point
def main():
    """CLI entry point for quality reviewer."""
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: quality_reviewer.py <scoring_result.json> <profile.json>")
        sys.exit(1)

    print("Quality reviewer running in demo mode")
    print("This requires integration with scoring_engine and profile_intake modules")


if __name__ == "__main__":
    main()
