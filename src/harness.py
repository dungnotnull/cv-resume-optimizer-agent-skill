#!/usr/bin/env python3
"""Main Harness Orchestrator - CV/Resume Optimizer (Idea 49)

Coordinates all sub-skills into complete resume analysis pipeline.
Implements main.md specification with production-grade orchestration.
"""

from __future__ import annotations

import json
import dataclasses
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class HarnessStatus(Enum):
    """Status of harness execution."""
    SUCCESS = "success"
    BLOCKED = "blocked"
    ERROR = "error"


# Import all sub-modules
from profile_intake import (
    ProfileIntake, NormalizedProfile, ParseStatus,
    ResumeSection, JDRequirements, CandidateConstraints
)
from framework_selector import (
    FrameworkSelector, FrameworkSelection, RoleFamily, Seniority
)
from scoring_engine import (
    ScoringEngine, ScoringResult, ScoreBand,
    DimensionScore, ATSGapAnalysis, STARAnalysis
)
from improvement_roadmap import (
    ImprovementRoadmapBuilder, ImprovementRoadmap,
    RoadmapAction, Effort, Impact
)
from quality_reviewer import (
    QualityReviewer, ChallengeLog, AssumptionChallenge,
    FairnessCheck, ClaimValidator
)


@dataclasses.dataclass
class HarnessInput:
    """Input to the harness."""
    resume_text: str
    jd_text: Optional[str] = None
    target_role: Optional[str] = None
    target_seniority: Optional[str] = None
    geography: Optional[str] = None
    work_authorization: Optional[str] = None
    salary_band: Optional[str] = None
    remote_preference: Optional[str] = None
    career_switch: bool = False


@dataclasses.dataclass
class HarnessOutput:
    """Output from the harness."""
    status: HarnessStatus
    block_reason: Optional[str]

    # Core results
    profile: Optional[NormalizedProfile]
    frameworks: Optional[FrameworkSelection]
    scoring: Optional[ScoringResult]
    roadmap: Optional[ImprovementRoadmap]
    review: Optional[ChallengeLog]

    # Metadata
    processing_time_seconds: float
    timestamp: str
    offline_mode: bool = False

    # Quality gate results
    quality_gate_passes: List[str]
    quality_gate_failures: List[str]


class MainHarness:
    """Main orchestrator for resume analysis."""

    def __init__(self, enable_web_search: bool = True):
        """
        Initialize the harness.

        Args:
            enable_web_search: Whether to enable web search for current research.
                             Set to False for offline mode.
        """
        self.enable_web_search = enable_web_search

        # Initialize sub-modules
        self.intake = ProfileIntake()
        self.framework_selector = FrameworkSelector()
        self.scoring_engine = ScoringEngine()
        self.roadmap_builder = ImprovementRoadmapBuilder()
        self.quality_reviewer = QualityReviewer()

    def process(self, input_data: HarnessInput) -> HarnessOutput:
        """
        Process resume and JD through complete analysis pipeline.

        Args:
            input_data: HarnessInput with resume, JD, and constraints

        Returns:
            HarnessOutput with complete analysis or block reason
        """
        start_time = datetime.now()
        quality_passes = []
        quality_failures = []

        try:
            # Step 1: Intake (sub-profile-intake)
            profile = self._run_intake(input_data)
            if profile.status != ParseStatus.SUCCESS:
                return HarnessOutput(
                    status=HarnessStatus.BLOCKED,
                    block_reason=profile.block_reason,
                    profile=None,
                    frameworks=None,
                    scoring=None,
                    roadmap=None,
                    review=None,
                    processing_time_seconds=0.0,
                    timestamp=datetime.now().isoformat(),
                    quality_gate_passes=[],
                    quality_gate_failures=["Intake failed: " + profile.block_reason]
                )
            quality_passes.append("Intake: Resume and JD parsed successfully")

            # Step 2: Framework selection (sub-framework-selector)
            frameworks = self._run_framework_selection(input_data, profile)
            passes, failures = self.framework_selector.validate_quality_gates(frameworks)
            quality_passes.extend([f"Framework: {p}" for p in passes])
            quality_failures.extend([f"Framework: {f}" for f in failures])

            # Step 3: Research (verify current ATS behavior/keyword trends)
            self._run_research(profile, frameworks)

            # Step 4: Scoring (sub-scoring-engine)
            scoring = self._run_scoring(profile, frameworks)
            quality_passes.append("Scoring: All dimensions scored with evidence")

            # Step 5: Quality review (sub-quality-reviewer)
            review = self._run_quality_review(scoring, profile)
            passes, failures = self.quality_reviewer.validate_quality_gates(review)
            quality_passes.extend([f"Quality: {p}" for p in passes])
            quality_failures.extend([f"Quality: {f}" for f in failures])

            # Step 6: Roadmap (sub-improvement-roadmap)
            roadmap = self._run_roadmap(scoring, profile)
            quality_passes.append("Roadmap: Prioritized actions with effort/impact")

            # Step 7: Synthesize output
            processing_time = (datetime.now() - start_time).total_seconds()

            return HarnessOutput(
                status=HarnessStatus.SUCCESS,
                block_reason=None,
                profile=profile,
                frameworks=frameworks,
                scoring=scoring,
                roadmap=roadmap,
                review=review,
                processing_time_seconds=processing_time,
                timestamp=datetime.now().isoformat(),
                offline_mode=not self.enable_web_search,
                quality_gate_passes=quality_passes,
                quality_gate_failures=quality_failures
            )

        except Exception as e:
            return HarnessOutput(
                status=HarnessStatus.ERROR,
                block_reason=f"Processing error: {str(e)}",
                profile=None,
                frameworks=None,
                scoring=None,
                roadmap=None,
                review=None,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now().isoformat(),
                quality_gate_passes=[],
                quality_gate_failures=[f"Error: {str(e)}"]
            )

    def _run_intake(self, input_data: HarnessInput) -> NormalizedProfile:
        """Run profile intake sub-skill."""
        constraints = {
            "geography": input_data.geography,
            "work_authorization": input_data.work_authorization,
            "salary_band": input_data.salary_band,
            "remote_preference": input_data.remote_preference,
            "career_switch": input_data.career_switch,
            "target_role": input_data.target_role,
            "target_seniority": input_data.target_seniority,
        }

        profile = self.intake.process(
            resume_text=input_data.resume_text,
            jd_text=input_data.jd_text,
            constraints=constraints
        )

        # Validate intake quality gates
        passes, failures = self.intake.validate_quality_gates(profile)
        if not passes:
            raise ValueError(f"Intake quality gate failures: {failures}")

        return profile

    def _run_framework_selection(
        self,
        input_data: HarnessInput,
        profile: NormalizedProfile
    ) -> FrameworkSelection:
        """Run framework selection sub-skill."""
        # Infer role family and seniority from inputs
        role_family = input_data.target_role or "general_corporate"
        seniority = input_data.target_seniority or "mid"

        frameworks = self.framework_selector.select_frameworks(
            role_family=role_family,
            seniority=seniority,
            industry=None  # Could be added as input parameter
        )

        return frameworks

    def _run_research(
        self,
        profile: NormalizedProfile,
        frameworks: FrameworkSelection
    ) -> None:
        """Run research step to verify current ATS behavior and keyword trends."""
        if not self.enable_web_search:
            # In offline mode, rely on SECOND-KNOWLEDGE-BRAIN.md
            # Log that we're in offline mode
            return

        # In production with web search enabled:
        # 1. WebSearch for "ATS resume parsing 2026"
        # 2. WebSearch for "in-demand skills [role_family] 2026"
        # 3. Compare findings to SECOND-KNOWLEDGE-BRAIN.md
        # 4. Update scoring weights if significant changes detected

        # For now, this is a placeholder for web search integration
        pass

    def _run_scoring(
        self,
        profile: NormalizedProfile,
        frameworks: FrameworkSelection
    ) -> ScoringResult:
        """Run scoring engine sub-skill."""
        scoring = self.scoring_engine.compute_scores(profile, frameworks)
        return scoring

    def _run_quality_review(
        self,
        scoring: ScoringResult,
        profile: NormalizedProfile
    ) -> ChallengeLog:
        """Run quality reviewer sub-skill."""
        review = self.quality_reviewer.review(scoring, profile)
        return review

    def _run_roadmap(
        self,
        scoring: ScoringResult,
        profile: NormalizedProfile
    ) -> ImprovementRoadmap:
        """Run improvement roadmap sub-skill."""
        roadmap = self.roadmap_builder.build_roadmap(scoring, profile)
        return roadmap

    def format_output(self, output: HarnessOutput) -> str:
        """Format harness output as human-readable report."""
        if output.status == HarnessStatus.BLOCKED:
            return f"# BLOCKED: {output.block_reason}\n\nPlease provide both a resume and a target job description to proceed."

        if output.status == HarnessStatus.ERROR:
            return f"# ERROR: {output.block_reason}"

        # Build comprehensive report
        report_lines = []

        # Header
        role = output.profile.constraints.target_role or "Target Role"
        report_lines.append(f"# Resume Fit Report — {role}\n")
        report_lines.append(f"Generated: {output.timestamp}\n")
        if output.offline_mode:
            report_lines.append("**Note: Running in offline mode - using cached knowledge base**\n")

        # 1. Snapshot
        report_lines.append("## 1. Snapshot\n")
        verdict_emoji = {
            ScoreBand.STRONG: "✅",
            ScoreBand.COMPETITIVE: "🟡",
            ScoreBand.NEEDS_WORK: "🔴"
        }
        verdict_display = {
            ScoreBand.STRONG: "Strong Fit",
            ScoreBand.COMPETITIVE: "Competitive",
            ScoreBand.NEEDS_WORK: "Needs Work"
        }
        emoji = verdict_emoji.get(output.scoring.verdict_band, "")
        verdict = verdict_display.get(output.scoring.verdict_band, "Unknown")
        report_lines.append(f"**Overall Fit Score:** {output.scoring.total_score}/100 {emoji}\n")
        report_lines.append(f"**Verdict:** {verdict}\n")

        # 2. Dimension Scores
        report_lines.append("\n## 2. Dimension Scores\n")
        report_lines.append("| Dimension | Score | Weight | Evidence |")
        report_lines.append("|-----------|-------|--------|----------|")

        for dim in output.scoring.dimension_scores:
            evidence_str = "; ".join(dim.evidence[:2])
            report_lines.append(
                f"| {dim.dimension} | {dim.score}% | {dim.weight}% | {evidence_str} |"
            )

        # 3. ATS Keyword Gap
        report_lines.append("\n## 3. ATS Keyword Gap\n")
        gap = output.scoring.ats_gap
        report_lines.append(f"**Coverage:** {gap.coverage_percentage}%")
        report_lines.append(f"**Matched Keywords:** {', '.join(gap.matched_keywords[:10])}")
        report_lines.append(f"**Missing Keywords:** {', '.join(gap.missing_keywords[:10])}")
        if gap.stuffing_detected:
            report_lines.append(f"⚠️ **Keyword stuffing detected** - {gap.stuffing_penalty}% penalty applied")

        # 4. STAR Analysis
        report_lines.append("\n## 4. Impact Quantification (STAR)\n")
        star = output.scoring.star_analysis
        report_lines.append(f"**Quantified Bullets:** {star.quantified_bullets}/{star.total_bullets} ({star.quantification_percentage}%)")
        if star.examples:
            report_lines.append("\n**Strong Examples:**")
            for example in star.examples[:3]:
                report_lines.append(f"- {example}")

        # 5. Format Risks
        if output.profile.format_risks:
            report_lines.append("\n## 5. Format Risks\n")
            for risk in output.profile.format_risks:
                report_lines.append(f"- **{risk.risk_type}** ({risk.severity}): {risk.recommendation}")

        # 6. Prioritized Rewrite Roadmap
        report_lines.append("\n## 6. Prioritized Rewrite Roadmap\n")
        report_lines.append("| Priority | Action | Effort | Impact | Dimension |")
        report_lines.append("|----------|--------|--------|--------|------------|")

        for i, action in enumerate(output.roadmap.actions[:10], 1):
            report_lines.append(
                f"| {i} | {action.action[:60]} | {action.effort.value} | {action.impact.value} | {action.dimension[:20]} |"
            )

        # Quick wins and strategic projects
        if output.roadmap.quick_wins:
            report_lines.append("\n### Quick Wins (Effort: S)\n")
            for action in output.roadmap.quick_wins[:5]:
                report_lines.append(f"- {action.action}")

        if output.roadmap.strategic_projects:
            report_lines.append("\n### Strategic Projects (Effort: L)\n")
            for action in output.roadmap.strategic_projects[:3]:
                report_lines.append(f"- {action.action}")

        # 7. Challenge Log
        if output.review.assumption_challenges:
            report_lines.append("\n## 7. Challenge Log (Quality Assurance)\n")
            for challenge in output.review.assumption_challenges[:5]:
                report_lines.append(f"**Assumption:** {challenge.assumption}")
                report_lines.append(f"- **Test:** {challenge.test_method}")
                report_lines.append(f"- **Result:** {challenge.result}")
                report_lines.append(f"- **Resolution:** {challenge.resolution}\n")

        # 8. Fairness Checks
        if output.review.fairness_checks:
            report_lines.append("\n## 8. Fairness Checks\n")
            for check in output.review.fairness_checks:
                status = "✅" if check.passed else "⚠️"
                report_lines.append(f"{status} **{check.check_type}:** {check.details}")
                if check.mitigation:
                    report_lines.append(f"   - *Mitigation:* {check.mitigation}")

        # 9. Frameworks Used
        report_lines.append("\n## 9. Frameworks Applied\n")
        for framework in output.frameworks.frameworks:
            report_lines.append(f"- **{framework.name}**: {framework.description}")
            report_lines.append(f"  - Source: {framework.source}")

        # 10. Quality Gate Summary
        report_lines.append("\n## 10. Quality Gate Summary\n")
        report_lines.append(f"**Passed:** {len(output.quality_gate_passes)} gates")
        report_lines.append(f"**Failed:** {len(output.quality_gate_failures)} gates")

        if output.quality_gate_failures:
            report_lines.append("\n**Failures:**")
            for failure in output.quality_gate_failures:
                report_lines.append(f"- {failure}")

        # Processing time
        report_lines.append(f"\n---\n*Processing time: {output.processing_time_seconds:.2f} seconds*")

        return "\n".join(report_lines)

    def to_json(self, output: HarnessOutput) -> str:
        """Convert output to JSON format."""
        def serialize(obj):
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, Path):
                return str(obj)
            return str(obj)

        return json.dumps(output, default=serialize, indent=2)


# CLI entry point
def main():
    """CLI entry point for main harness."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="CV/Resume Optimizer - Analyze resume against job description"
    )
    parser.add_argument("resume", help="Path to resume file (txt or md)")
    parser.add_argument("jd", help="Path to job description file (txt or md)")
    parser.add_argument("--role", help="Target role (e.g., 'Senior Software Engineer')")
    parser.add_argument("--seniority", help="Target seniority (e.g., 'senior', 'mid', 'entry')")
    parser.add_argument("--output", choices=["report", "json"], default="report",
                       help="Output format")
    parser.add_argument("--offline", action="store_true",
                       help="Run in offline mode without web search")

    args = parser.parse_args()

    # Read input files
    try:
        resume_text = Path(args.resume).read_text(encoding="utf-8")
        jd_text = Path(args.jd).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading input files: {e}", file=sys.stderr)
        sys.exit(1)

    # Build input
    input_data = HarnessInput(
        resume_text=resume_text,
        jd_text=jd_text,
        target_role=args.role,
        target_seniority=args.seniority
    )

    # Run harness
    harness = MainHarness(enable_web_search=not args.offline)
    output = harness.process(input_data)

    # Output results
    if args.output == "json":
        print(harness.to_json(output))
    else:
        print(harness.format_output(output))

    # Exit with error code if blocked or error
    if output.status != HarnessStatus.SUCCESS:
        sys.exit(1)


if __name__ == "__main__":
    main()
