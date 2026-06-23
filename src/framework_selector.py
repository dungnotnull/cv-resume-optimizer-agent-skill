#!/usr/bin/env python3
"""Framework Selector Module - CV/Resume Optimizer (Idea 49)

Select scoring frameworks and dimension weights appropriate to role family and seniority.
Implements sub-framework-selector specification with production-grade framework selection.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional, Dict, List, Any
from pathlib import Path


class RoleFamily(Enum):
    """Standard role families for framework selection."""
    SOFTWARE_ENGINEERING = "software_engineering"
    DATA_SCIENCE = "data_science"
    PRODUCT_MANAGEMENT = "product_management"
    DESIGN = "design"
    SALES = "sales"
    MARKETING = "marketing"
    GENERAL_CORPORATE = "general_corporate"
    EXECUTIVE_LEADERSHIP = "executive_leadership"


class Seniority(Enum):
    """Standard seniority levels."""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


@dataclasses.dataclass
class FrameworkDefinition:
    """Definition of a scoring framework."""
    name: str
    description: str
    source: str
    url: Optional[str] = None
    weight: float = 0.0
    dimensions: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class FrameworkSelection:
    """Selected frameworks with tuned weights."""
    frameworks: List[FrameworkDefinition]
    dimension_weights: Dict[str, float]
    role_family: RoleFamily
    seniority: Seniority
    rationale: str


class FrameworkRepository:
    """Repository of available scoring frameworks."""

    # Core frameworks always included
    CORE_FRAMEWORKS = {
        "ats_keyword_coverage": FrameworkDefinition(
            name="ats_keyword_coverage",
            description="Measures coverage of JD-required keywords in resume for ATS parsing",
            source="ATS vendor documentation (Workday, Greenhouse, Taleo)",
            url="https://www.jobscan.co/blog/ats-resume-keywords/",
            dimensions=["ats_keywords", "formatting"]
        ),
        "star_method": FrameworkDefinition(
            name="star_method",
            description="Situation-Task-Action-Result quantified impact in bullet points",
            source="Career coaching literature; behavioral interviewing standards",
            url="https://www.themuse.com/advice/star-interview-method",
            dimensions=["impact_quantification", "results_orientation"]
        ),
    }

    # Additional frameworks by role family
    ROLE_SPECIFIC_FRAMEWORKS = {
        RoleFamily.SOFTWARE_ENGINEERING: [
            FrameworkDefinition(
                name="onet_tech_skills_match",
                description="O*NET software developer skill taxonomy alignment",
                source="O*NET Online (onetonline.org)",
                url="https://www.onetonline.org/link/summary/15-1132.00",
                dimensions=["technical_skills", "skill_relevance"]
            ),
            FrameworkDefinition(
                name="github_portfolio_quality",
                description="GitHub/contribution quality as technical proof",
                source="Engineering hiring practices",
                dimensions=["portfolio_quality", "code_quality"]
            ),
        ],
        RoleFamily.DATA_SCIENCE: [
            FrameworkDefinition(
                name="onet_data_skills_match",
                description="O*NET data science skill taxonomy alignment",
                source="O*NET Online (onetonline.org)",
                url="https://www.onetonline.org/link/summary/15-2051.00",
                dimensions=["technical_skills", "analytical_skills"]
            ),
            FrameworkDefinition(
                name="quantifiable_impact",
                description="Model performance metrics and business impact",
                source="Data science hiring standards",
                dimensions=["impact_quantification", "metrics"]
            ),
        ],
        RoleFamily.PRODUCT_MANAGEMENT: [
            FrameworkDefinition(
                name="product_sense_framework",
                description="Product thinking, user empathy, business metrics",
                source="Product management hiring standards",
                dimensions=["product_thinking", "business_impact"]
            ),
        ],
        RoleFamily.DESIGN: [
            FrameworkDefinition(
                name="portfolio_quality",
                description="Design portfolio case studies and process",
                source="Design hiring standards (Dribbble, Behance)",
                dimensions=["portfolio_quality", "design_thinking"]
            ),
        ],
        RoleFamily.SALES: [
            FrameworkDefinition(
                name="quota_attainment",
                description="Sales metrics, quota achievement, deal size",
                source="Sales performance standards",
                dimensions=["metrics", "achievement"]
            ),
        ],
        RoleFamily.MARKETING: [
            FrameworkDefinition(
                name="campaign_metrics",
                description="Campaign performance, ROI, conversion metrics",
                source="Marketing measurement standards",
                dimensions=["metrics", "impact"]
            ),
        ],
        RoleFamily.EXECUTIVE_LEADERSHIP: [
            FrameworkDefinition(
                name="scope_scale_impact",
                description="Team/organization size, budget managed, strategic impact",
                source="Executive search standards",
                dimensions=["scope", "scale", "strategic_impact"]
            ),
        ],
    }

    # Universal frameworks applicable to all roles
    UNIVERSAL_FRAMEWORKS = {
        "ladders_6_second_scan": FrameworkDefinition(
            name="ladders_6_second_scan",
            description="Ladders eye-tracking study: top-third must convey fit",
            source="The Ladders 6-second resume study",
            url="https://www.theladders.com/resume-study",
            dimensions=["readability", "top_third_content"]
        ),
        "ons_resume_parseability": FrameworkDefinition(
            name="ons_resume_parseability",
            description="O*NET resume parsing compatibility standards",
            source="O*NET Online documentation",
            url="https://www.onetcenter.org/",
            dimensions=["formatting", "ats_compatibility"]
        ),
    }


class DimensionWeightCalculator:
    """Calculate dimension weights based on role and seniority."""

    # Base dimensions and default weights
    BASE_DIMENSIONS = {
        "ats_keyword_coverage": 25.0,
        "impact_quantification": 20.0,
        "role_seniority_alignment": 20.0,
        "readability_6_sec_scan": 15.0,
        "formatting_ats_parseability": 10.0,
        "consistency_error_free": 10.0,
    }

    # Seniority-specific adjustments
    SENIORITY_ADJUSTMENTS = {
        Seniority.ENTRY: {
            "ats_keyword_coverage": 1.2,  # Entry roles more keyword-driven
            "impact_quantification": 0.8,
            "readability_6_sec_scan": 1.3,
        },
        Seniority.MID: {
            "ats_keyword_coverage": 1.1,
            "impact_quantification": 0.9,
        },
        Seniority.SENIOR: {
            "ats_keyword_coverage": 0.9,
            "impact_quantification": 1.2,
            "role_seniority_alignment": 1.1,
        },
        Seniority.LEAD: {
            "ats_keyword_coverage": 0.8,
            "impact_quantification": 1.3,
            "role_seniority_alignment": 1.2,
        },
        Seniority.MANAGER: {
            "ats_keyword_coverage": 0.7,
            "impact_quantification": 1.4,
            "role_seniority_alignment": 1.3,
        },
        Seniority.DIRECTOR: {
            "impact_quantification": 1.5,
            "role_seniority_alignment": 1.4,
            "formatting_ats_parseability": 0.8,
        },
        Seniority.EXECUTIVE: {
            "impact_quantification": 1.6,
            "role_seniority_alignment": 1.5,
            "ats_keyword_coverage": 0.5,
            "formatting_ats_parseability": 0.7,
        },
    }

    def calculate_weights(
        self,
        role_family: RoleFamily,
        seniority: Seniority,
        custom_frameworks: Optional[List[FrameworkDefinition]] = None
    ) -> Dict[str, float]:
        """Calculate optimized dimension weights."""
        weights = self.BASE_DIMENSIONS.copy()

        # Apply seniority adjustments
        adjustments = self.SENIORITY_ADJUSTMENTS.get(seniority, {})
        for dimension, factor in adjustments.items():
            if dimension in weights:
                weights[dimension] *= factor

        # Add dimensions from custom frameworks
        if custom_frameworks:
            for framework in custom_frameworks:
                for dimension in framework.dimensions:
                    if dimension not in weights:
                        weights[dimension] = 5.0  # Small default weight

        # Normalize to 100%
        total = sum(weights.values())
        if total > 0:
            weights = {k: round((v / total) * 100, 1) for k, v in weights.items()}

        return weights


class FrameworkSelector:
    """Main framework selection orchestrator."""

    def __init__(self):
        self.repository = FrameworkRepository()
        self.weight_calculator = DimensionWeightCalculator()

    def select_frameworks(
        self,
        role_family: str,
        seniority: str,
        industry: Optional[str] = None,
        custom_frameworks: Optional[List[str]] = None
    ) -> FrameworkSelection:
        """Select optimal frameworks for the given role and seniority."""
        # Normalize inputs
        role = self._parse_role_family(role_family)
        level = self._parse_seniority(seniority)

        # Start with core frameworks (always included)
        selected = list(self.repository.CORE_FRAMEWORKS.values())

        # Add role-specific frameworks
        role_frameworks = self.repository.ROLE_SPECIFIC_FRAMEWORKS.get(
            role, []
        )
        selected.extend(role_frameworks)

        # Add universal frameworks
        selected.extend(list(self.repository.UNIVERSAL_FRAMEWORKS.values()))

        # Calculate tuned weights
        dimension_weights = self.weight_calculator.calculate_weights(
            role, level, [f for f in selected if f not in self.repository.CORE_FRAMEWORKS.values()]
        )

        # Apply weights to frameworks
        for framework in selected:
            if framework.name == "ats_keyword_coverage":
                framework.weight = dimension_weights.get("ats_keyword_coverage", 25.0)
            elif framework.name == "star_method":
                framework.weight = dimension_weights.get("impact_quantification", 20.0)
            elif framework.name == "ladders_6_second_scan":
                framework.weight = dimension_weights.get("readability_6_sec_scan", 15.0)
            elif "parseability" in framework.name:
                framework.weight = dimension_weights.get("formatting_ats_parseability", 10.0)

        # Build rationale
        rationale = self._build_rationale(role, level, selected)

        return FrameworkSelection(
            frameworks=selected,
            dimension_weights=dimension_weights,
            role_family=role,
            seniority=level,
            rationale=rationale
        )

    def _parse_role_family(self, role_input: str) -> RoleFamily:
        """Parse role family from string input."""
        role_lower = role_input.lower()

        role_mappings = {
            "software": RoleFamily.SOFTWARE_ENGINEERING,
            "developer": RoleFamily.SOFTWARE_ENGINEERING,
            "engineer": RoleFamily.SOFTWARE_ENGINEERING,
            "swe": RoleFamily.SOFTWARE_ENGINEERING,
            "data": RoleFamily.DATA_SCIENCE,
            "scientist": RoleFamily.DATA_SCIENCE,
            "analytics": RoleFamily.DATA_SCIENCE,
            "product": RoleFamily.PRODUCT_MANAGEMENT,
            "pm": RoleFamily.PRODUCT_MANAGEMENT,
            "design": RoleFamily.DESIGN,
            "ux": RoleFamily.DESIGN,
            "ui": RoleFamily.DESIGN,
            "sales": RoleFamily.SALES,
            "marketing": RoleFamily.MARKETING,
            "executive": RoleFamily.EXECUTIVE_LEADERSHIP,
            "director": RoleFamily.EXECUTIVE_LEADERSHIP,
            "vp": RoleFamily.EXECUTIVE_LEADERSHIP,
            "manager": RoleFamily.MANAGER,
        }

        for key, role in role_mappings.items():
            if key in role_lower:
                return role

        return RoleFamily.GENERAL_CORPORATE

    def _parse_seniority(self, seniority_input: str) -> Seniority:
        """Parse seniority from string input."""
        seniority_lower = seniority_input.lower()

        seniority_mappings = {
            "intern": Seniority.ENTRY,
            "entry": Seniority.ENTRY,
            "junior": Seniority.ENTRY,
            "jr": Seniority.ENTRY,
            "associate": Seniority.MID,
            "mid": Seniority.MID,
            "intermediate": Seniority.MID,
            "senior": Seniority.SENIOR,
            "sr": Seniority.SENIOR,
            "lead": Seniority.LEAD,
            "staff": Seniority.LEAD,
            "principal": Seniority.LEAD,
            "manager": Seniority.MANAGER,
            "mgr": Seniority.MANAGER,
            "head": Seniority.DIRECTOR,
            "director": Seniority.DIRECTOR,
            "vp": Seniority.EXECUTIVE,
            "c-level": Seniority.EXECUTIVE,
            "executive": Seniority.EXECUTIVE,
            "cto": Seniority.EXECUTIVE,
            "ceo": Seniority.EXECUTIVE,
        }

        for key, level in seniority_mappings.items():
            if key in seniority_lower:
                return level

        return Seniority.MID

    def _build_rationale(
        self,
        role: RoleFamily,
        seniority: Seniority,
        frameworks: List[FrameworkDefinition]
    ) -> str:
        """Build rationale explanation for framework selection."""
        parts = [
            f"Selected {len(frameworks)} frameworks for {role.value} at {seniority.value} level.",
            "\nCore frameworks (always included):",
        ]

        for f in frameworks:
            if f.name in self.repository.CORE_FRAMEWORKS:
                parts.append(f"- {f.name}: {f.description} (Source: {f.source})")

        parts.append("\nDimension weights tuned for seniority:")
        if seniority in [Seniority.SENIOR, Seniority.LEAD, Seniority.MANAGER]:
            parts.append("- Increased emphasis on impact quantification and scope")
            parts.append("- Reduced emphasis on pure keyword coverage")
        elif seniority == Seniority.ENTRY:
            parts.append("- Higher emphasis on ATS keyword coverage and readability")
            parts.append("- Focus on 6-second scan heuristics")

        return "\n".join(parts)

    def validate_quality_gates(self, selection: FrameworkSelection) -> tuple[bool, List[str]]:
        """Validate framework selection meets quality gates."""
        failures = []

        # Must have at least 2 named frameworks
        named_frameworks = [f for f in selection.frameworks if f.source]
        if len(named_frameworks) < 2:
            failures.append(f"Need at least 2 named frameworks, found {len(named_frameworks)}")

        # All frameworks must have citations
        for framework in selection.frameworks:
            if not framework.source:
                failures.append(f"Framework {framework.name} lacks citation/source")

        # Weights must sum to 100%
        total_weight = sum(selection.dimension_weights.values())
        if not (99.0 <= total_weight <= 101.0):  # Allow small rounding errors
            failures.append(f"Dimension weights sum to {total_weight}%, should be 100%")

        # Weights should be justified for seniority
        if not selection.rationale:
            failures.append("Missing weight justification for seniority level")

        return len(failures) == 0, failures


# CLI entry point
def main():
    """CLI entry point for framework selection."""
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: framework_selector.py <role_family> <seniority> [industry]")
        sys.exit(1)

    role_family = sys.argv[1]
    seniority = sys.argv[2]
    industry = sys.argv[3] if len(sys.argv) > 3 else None

    selector = FrameworkSelector()
    selection = selector.select_frameworks(role_family, seniority, industry)

    # Validate quality gates
    passes, failures = selector.validate_quality_gates(selection)
    if not passes:
        print("Quality gate failures:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        sys.exit(1)

    # Output as JSON
    output = {
        "role_family": selection.role_family.value,
        "seniority": selection.seniority.value,
        "frameworks": [
            {
                "name": f.name,
                "description": f.description,
                "source": f.source,
                "url": f.url,
                "weight": f.weight,
                "dimensions": f.dimensions,
            }
            for f in selection.frameworks
        ],
        "dimension_weights": selection.dimension_weights,
        "rationale": selection.rationale,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
