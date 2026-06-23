#!/usr/bin/env python3
"""Improvement Roadmap Module - CV/Resume Optimizer (Idea 49)

Convert scoring gaps into prioritized resume rewrite roadmap with before/after samples.
Implements sub-improvement-roadmap specification with production-grade prioritization.
"""

from __future__ import annotations

import re
import dataclasses
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import field


class Effort(Enum):
    """Effort level for implementation."""
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"


class Impact(Enum):
    """Impact level on fit score."""
    LOW = "Low"
    MEDIUM = "Med"
    HIGH = "High"


@dataclasses.dataclass
class RoadmapAction:
    """Single action item in the roadmap."""
    action: str
    dimension: str
    before: Optional[str]
    after: Optional[str]
    effort: Effort
    impact: Impact
    priority_score: float
    rationale: str
    framework_reference: str


@dataclasses.dataclass
class ImprovementRoadmap:
    """Complete improvement roadmap."""
    actions: List[RoadmapAction]
    total_effort: str
    estimated_impact: str
    quick_wins: List[RoadmapAction]
    strategic_projects: List[RoadmapAction]


class O NETSkillMapper:
    """Map transferable skills using O*NET taxonomy."""

    # Transferable skill mappings for career switchers
    TRANSFERABLE_MAPPINGS = {
        "teaching": {
            "communication": ["Stakeholder management", "Cross-functional communication"],
            "presentation": ["Technical documentation", "User education"],
            "curriculum_design": ["Product roadmap", "User journey mapping"],
            "student_assessment": ["User research", "A/B testing"],
            "classroom_management": ["Project management", "Resource allocation"],
        },
        "retail": {
            "customer_service": ["User support", "Client relations"],
            "sales": ["Business development", "Revenue operations"],
            "inventory": ["Resource management", "Asset allocation"],
            "team_training": ["Onboarding", "Knowledge sharing"],
        },
        "hospitality": {
            "guest_relations": ["Client success", "Account management"],
            "event_planning": ["Project coordination", "Launch management"],
            "operations": ["Process optimization", "Workflow design"],
        },
        "admin_assistant": {
            "scheduling": ["Resource planning", "Timeline management"],
            "documentation": ["Technical writing", "Process documentation"],
            "coordination": ["Program management", "Cross-functional alignment"],
        },
    }

    def map_transferable_skills(
        self,
        current_role: str,
        target_role: str,
        resume_text: str
    ) -> List[Tuple[str, str]]:
        """Map current skills to target role terminology."""
        mappings = []

        role_lower = current_role.lower()
        for source_role, skill_map in self.TRANSFERABLE_MAPPINGS.items():
            if source_role in role_lower:
                for source_skill, target_skills in skill_map.items():
                    if source_skill.lower() in resume_text.lower():
                        for target_skill in target_skills:
                            mappings.append((source_skill, target_skill))

        return mappings


class STARRewriter:
    """Rewrite bullets using STAR method with quantification."""

    # Templates for adding quantification
    QUANTIFICATION_TEMPLATES = [
        "increased {metric} by {percent}%",
        "reduced {process} time by {time}",
        "managed {team_size} person team",
        "delivered {deliverable} for {stakeholder}",
        "achieved {result} within {timeframe}",
        "built {system} serving {users} users",
        "optimized {process} resulting in {benefit}",
    ]

    # Action verbs for different impact types
    ACTION_VERBS = {
        "growth": ["grew", "scaled", "expanded", "increased"],
        "efficiency": ["reduced", "optimized", "streamlined", "eliminated"],
        "quality": ["improved", "enhanced", "refactored", "standardized"],
        "delivery": ["built", "shipped", "launched", "delivered", "deployed"],
        "leadership": ["led", "managed", "mentored", "coached", "guided"],
        "innovation": ["designed", "architected", "pioneered", "created"],
    }

    def rewrite_bullet(self, original: str, jd_keywords: List[str]) -> Tuple[str, str]:
        """Rewrite a bullet to add STAR quantification."""
        bullet_lower = original.lower()

        # Identify impact type
        impact_type = self._identify_impact_type(bullet_lower)
        verbs = self.ACTION_VERBS.get(impact_type, ["improved"])

        # Extract key components
        action = self._extract_action(original, verbs)
        metric = self._suggest_metric(impact_type)
        result = self._extract_result(original)

        # Generate improved version
        improved = f"{action} {metric}, {result}"
        if not any(k in improved.lower() for k in jd_keywords[:5]):
            # Add a relevant keyword if missing
            if jd_keywords:
                improved += f" using {jd_keywords[0]}"

        return original, improved

    def _identify_impact_type(self, text: str) -> str:
        """Identify the type of impact in the text."""
        impact_keywords = {
            "growth": ["grew", "increased", "scaled", "revenue", "users", "adoption"],
            "efficiency": ["reduced", "faster", "saved", "cut", "time", "cost"],
            "quality": ["improved", "better", "accuracy", "reliability", "robust"],
            "delivery": ["built", "shipped", "launched", "delivered", "released"],
            "leadership": ["led", "managed", "team", "mentored", "guided"],
            "innovation": ["new", "created", "designed", "architected", "first"],
        }

        for impact_type, keywords in impact_keywords.items():
            if any(kw in text for kw in keywords):
                return impact_type

        return "delivery"  # Default

    def _extract_action(self, text: str, verbs: List[str]) -> str:
        """Extract or improve the action verb phrase."""
        words = text.split()
        if words:
            first_word = words[0].lower()
            if first_word in verbs:
                return f"{words[0].capitalize()} {' '.join(words[1:15])}"
            else:
                # Replace with stronger verb
                return f"{verbs[0].capitalize()} {' '.join(words[:15])}"
        return text

    def _suggest_metric(self, impact_type: str) -> str:
        """Suggest appropriate metrics for impact type."""
        metrics = {
            "growth": "user engagement by 25%",
            "efficiency": "processing time by 40%",
            "quality": "accuracy to 99.9%",
            "delivery": "feature in 8 weeks",
            "leadership": "team of 5 engineers",
            "innovation": "new architecture",
        }
        return metrics.get(impact_type, "performance by 30%")

    def _extract_result(self, text: str) -> str:
        """Extract the result/benefit from the text."""
        # Look for result indicators
        result_patterns = [
            r"resulting?\s+in\s+([^.]+)",
            r"achieved\s+([^.]+)",
            r"leading\s+to\s+([^.]+)",
        ]

        for pattern in result_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Default result
        return "driving business impact"


class ImpactEffortCalculator:
    """Calculate impact and effort for roadmap prioritization."""

    # Dimension impact weights
    DIMENSION_IMPACT = {
        "ats_keyword_coverage": 0.9,  # High impact - often first filter
        "impact_quantification": 0.85,  # High impact - differentiates candidates
        "role_seniority_alignment": 0.7,  # Medium-high - important but harder to fake
        "readability_6_sec_scan": 0.6,  # Medium - helps but not critical
        "formatting_ats_parseability": 0.8,  # High impact - can block parsing
        "consistency_error_free": 0.4,  # Lower impact - polish vs substance
    }

    def calculate_priority_score(
        self,
        dimension_score: float,
        dimension: str,
        effort: Effort
    ) -> float:
        """Calculate priority score (impact/effort ratio)."""
        # Priority = (gap * dimension_impact) / effort_factor
        gap = 100 - dimension_score
        dimension_impact = self.DIMENSION_IMPACT.get(dimension, 0.5)

        effort_factors = {Effort.SMALL: 1, Effort.MEDIUM: 2, Effort.LARGE: 3}
        effort_factor = effort_factors.get(effort, 2)

        priority = (gap * dimension_impact) / effort_factor
        return round(priority, 2)


class ImprovementRoadmapBuilder:
    """Build prioritized improvement roadmap."""

    def __init__(self):
        self.onet_mapper = O_NETSkillMapper()
        self.star_rewriter = STARRewriter()
        self.priority_calculator = ImpactEffortCalculator()

    def build_roadmap(
        self,
        scoring_result: Any,
        profile: Any
    ) -> ImprovementRoadmap:
        """Build prioritized improvement roadmap."""
        actions: List[RoadmapAction] = []

        # Process each dimension score
        for dimension_score in scoring_result.dimension_scores:
            if dimension_score.score < 80:  # Only add actions for dimensions below 80
                dimension_actions = self._generate_actions_for_dimension(
                    dimension_score,
                    scoring_result,
                    profile
                )
                actions.extend(dimension_actions)

        # Sort by priority score
        actions.sort(key=lambda a: a.priority_score, reverse=True)

        # Categorize
        quick_wins = [a for a in actions if a.effort == Effort.SMALL]
        strategic_projects = [a for a in actions if a.effort == Effort.LARGE]

        # Calculate totals
        total_effort_score = sum(
            {"S": 1, "M": 2, "L": 3}.get(a.effort.value, 2) for a in actions
        )
        total_impact_score = sum(
            {"Low": 1, "Med": 2, "High": 3}.get(a.impact.value, 2) for a in actions
        )

        return ImprovementRoadmap(
            actions=actions,
            total_effort=self._calculate_effort_label(total_effort_score),
            estimated_impact=self._calculate_impact_label(total_impact_score),
            quick_wins=quick_wins,
            strategic_projects=strategic_projects
        )

    def _generate_actions_for_dimension(
        self,
        dimension_score: Any,
        scoring_result: Any,
        profile: Any
    ) -> List[RoadmapAction]:
        """Generate specific actions for a dimension."""
        actions = []
        dimension = dimension_score.dimension.lower()

        if "ats" in dimension or "keyword" in dimension:
            actions.extend(self._generate_ats_actions(
                dimension_score, scoring_result
            ))
        elif "star" in dimension or "quantification" in dimension:
            actions.extend(self._generate_star_actions(
                dimension_score, scoring_result
            ))
        elif "readability" in dimension:
            actions.extend(self._generate_readability_actions(
                dimension_score, profile
            ))
        elif "format" in dimension:
            actions.extend(self._generate_format_actions(
                dimension_score, profile
            ))
        elif "alignment" in dimension:
            actions.extend(self._generate_alignment_actions(
                dimension_score, profile
            ))
        elif "consistency" in dimension:
            actions.extend(self._generate_consistency_actions(
                dimension_score, profile
            ))

        return actions

    def _generate_ats_actions(
        self,
        dimension_score: Any,
        scoring_result: Any
    ) -> List[RoadmapAction]:
        """Generate ATS keyword gap actions."""
        actions = []
        gap = scoring_result.ats_gap

        if gap.missing_keywords:
            # High priority: Add missing keywords
            missing_str = ", ".join(gap.missing_keywords[:8])
            actions.append(RoadmapAction(
                action=f"Integrate missing JD keywords: {missing_str}",
                dimension=dimension_score.dimension,
                before=f"Resume lacks: {missing_str}",
                after=f"Skills section includes: {missing_str}, integrated naturally in experience bullets",
                effort=Effort.MEDIUM,
                impact=Impact.HIGH,
                priority_score=0.0,  # Will be calculated
                rationale=f"ATS filters often reject resumes missing required keywords",
                framework_reference="ATS Keyword Coverage framework"
            ))

        if gap.stuffing_detected:
            # Medium priority: Fix stuffing
            actions.append(RoadmapAction(
                action="Remove keyword stuffing and integrate naturally",
                dimension=dimension_score.dimension,
                before="Keywords listed in footer/skills block without context",
                after="Keywords woven into experience bullets with specific examples",
                effort=Effort.MEDIUM,
                impact=Impact.MEDIUM,
                priority_score=0.0,
                rationale="Keyword stuffing triggers ATS quality filters and recruiter suspicion",
                framework_reference="ATS Keyword Coverage framework"
            ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "ats_keyword_coverage",
                action.effort
            )

        return actions

    def _generate_star_actions(
        self,
        dimension_score: Any,
        scoring_result: Any
    ) -> List[RoadmapAction]:
        """Generate STAR quantification actions."""
        actions = []
        star = scoring_result.star_analysis

        # Get experience bullets
        if star.missing_quantification:
            for bullet in star.missing_quantification[:3]:
                jd_keywords = (
                    scoring_result.ats_gap.matched_keywords +
                    scoring_result.ats_gap.missing_keywords
                )

                before, after = self.star_rewriter.rewrite_bullet(bullet, jd_keywords)

                actions.append(RoadmapAction(
                    action=f"Quantify impact in bullet: {before[:50]}...",
                    dimension=dimension_score.dimension,
                    before=before,
                    after=after,
                    effort=Effort.SMALL,
                    impact=Impact.HIGH,
                    priority_score=0.0,
                    rationale="Quantified bullets demonstrate impact and differentiate candidates",
                    framework_reference="STAR Method framework"
                ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "impact_quantification",
                action.effort
            )

        return actions

    def _generate_readability_actions(
        self,
        dimension_score: Any,
        profile: Any
    ) -> List[RoadmapAction]:
        """Generate readability and 6-second scan actions."""
        actions = []

        # Check top-third content
        lines = profile.raw_resume.splitlines()
        top_third = "\n".join(lines[:len(lines)//3])

        if not re.search(r"\d+%", top_third):
            actions.append(RoadmapAction(
                action="Move quantified impact to top third",
                dimension=dimension_score.dimension,
                before="Key achievements buried in experience section",
                after="Summary line: 'Led engineering team that increased system performance by 40%'",
                effort=Effort.SMALL,
                impact=Impact.MEDIUM,
                priority_score=0.0,
                rationale="Recruiters spend 6 seconds scanning; top-third must convey fit",
                framework_reference="Ladders 6-second scan study"
            ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "readability_6_sec_scan",
                action.effort
            )

        return actions

    def _generate_format_actions(
        self,
        dimension_score: Any,
        profile: Any
    ) -> List[RoadmapAction]:
        """Generate format/ATS parseability actions."""
        actions = []

        for risk in profile.format_risks:
            if risk.severity == "high":
                actions.append(RoadmapAction(
                    action=f"Fix format risk: {risk.risk_type}",
                    dimension=dimension_score.dimension,
                    before=f"Resume uses {risk.risk_type}",
                    after=risk.recommendation,
                    effort=Effort.MEDIUM if "table" in risk.risk_type else Effort.SMALL,
                    impact=Impact.HIGH if risk.severity == "high" else Impact.MEDIUM,
                    priority_score=0.0,
                    rationale="ATS parsers fail on complex formatting; simple formats succeed",
                    framework_reference="ATS parseability standards"
                ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "formatting_ats_parseability",
                action.effort
            )

        return actions

    def _generate_alignment_actions(
        self,
        dimension_score: Any,
        profile: Any
    ) -> List[RoadmapAction]:
        """Generate role/seniority alignment actions."""
        actions = []

        if profile.career_switch:
            # Map transferable skills
            target_role = profile.constraints.target_role or "target role"
            mappings = self.onet_mapper.map_transferable_skills(
                "current", target_role, profile.raw_resume
            )

            for source, target in mappings[:3]:
                actions.append(RoadmapAction(
                    action=f"Reframe skill: '{source}' → '{target}'",
                    dimension=dimension_score.dimension,
                    before=f"Experience in {source}",
                    after=f"Applied {source} principles to deliver {target} outcomes",
                    effort=Effort.SMALL,
                    impact=Impact.MEDIUM,
                    priority_score=0.0,
                    rationale="Reframing transferable skills demonstrates relevant experience",
                    framework_reference="O*NET skill taxonomy"
                ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "role_seniority_alignment",
                action.effort
            )

        return actions

    def _generate_consistency_actions(
        self,
        dimension_score: Any,
        profile: Any
    ) -> List[RoadmapAction]:
        """Generate consistency and error-fix actions."""
        actions = []

        # Look for common issues
        if "•" in profile.raw_resume and "-" in profile.raw_resume:
            actions.append(RoadmapAction(
                action="Standardize bullet point characters",
                dimension=dimension_score.dimension,
                before="Mix of •, -, * for bullets",
                after="Consistent use of • for all bullet points",
                effort=Effort.SMALL,
                impact=Impact.LOW,
                priority_score=0.0,
                rationale="Consistent formatting shows attention to detail",
                framework_reference="Editorial standards"
            ))

        # Calculate priority scores
        for action in actions:
            action.priority_score = self.priority_calculator.calculate_priority_score(
                dimension_score.score,
                "consistency_error_free",
                action.effort
            )

        return actions

    def _calculate_effort_label(self, total_score: int) -> str:
        """Calculate human-readable effort label."""
        if total_score <= 3:
            return "Quick (~1-2 hours)"
        elif total_score <= 6:
            return "Moderate (~2-4 hours)"
        elif total_score <= 10:
            return "Significant (~4-8 hours)"
        else:
            return "Substantial (~8+ hours)"

    def _calculate_impact_label(self, total_score: int) -> str:
        """Calculate human-readable impact label."""
        if total_score >= 12:
            return "High impact (15+ point score improvement)"
        elif total_score >= 8:
            return "Medium impact (8-15 point score improvement)"
        else:
            return "Low impact (under 8 point score improvement)"


# CLI entry point
def main():
    """CLI entry point for improvement roadmap."""
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: improvement_roadmap.py <scoring_result.json> <profile.json>")
        sys.exit(1)

    print("Improvement roadmap builder running in demo mode")
    print("This requires integration with scoring_engine and profile_intake modules")


if __name__ == "__main__":
    main()
