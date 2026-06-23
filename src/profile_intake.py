#!/usr/bin/env python3
"""Profile Intake Module - CV/Resume Optimizer (Idea 49)

Normalizes resume + JD + candidate constraints into structured profile for scoring.
Implements sub-profile-intake specification with production-grade parsing and validation.
"""

from __future__ import annotations

import re
import dataclasses
from enum import Enum
from typing import Optional, Dict, List, Any
from pathlib import Path


class ParseStatus(Enum):
    """Status of profile parsing operation."""
    SUCCESS = "success"
    BLOCKED_MISSING_JD = "blocked_missing_jd"
    BLOCKED_MISSING_RESUME = "blocked_missing_resume"
    ERROR_PARSE_FAILURE = "error_parse_failure"
    ERROR_UNSUPPORTED_FORMAT = "error_unsupported_format"


@dataclasses.dataclass
class ResumeSection:
    """Parsed section from resume."""
    section_type: str
    content: str
    bullets: List[str]
    metadata: Dict[str, Any]


@dataclasses.dataclass
class JDRequirements:
    """Parsed job description requirements."""
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]
    seniority_signals: List[str]
    hard_requirements: List[str]
    raw_text: str


@dataclasses.dataclass
class CandidateConstraints:
    """Candidate-provided constraints."""
    geography: Optional[str] = None
    work_authorization: Optional[str] = None
    salary_band: Optional[str] = None
    remote_preference: Optional[str] = None
    career_switch: bool = False
    target_role: Optional[str] = None
    target_seniority: Optional[str] = None


@dataclasses.dataclass
class FormatRisk:
    """Detected formatting risk for ATS parsing."""
    risk_type: str
    severity: str
    location: str
    recommendation: str


@dataclasses.dataclass
class NormalizedProfile:
    """Normalized profile from intake process."""
    status: ParseStatus
    resume_sections: Dict[str, ResumeSection]
    jd_requirements: Optional[JDRequirements]
    constraints: CandidateConstraints
    format_risks: List[FormatRisk]
    career_switch: bool
    raw_resume: str
    block_reason: Optional[str] = None


class ResumeParser:
    """Parse resume text into structured sections."""

    # Common resume section headings
    SECTION_PATTERNS = {
        "summary": [
            r"^summary\s*$", r"^professional\s+summary\s*$", r"^profile\s*$",
            r"^about\s*$", r"^objective\s*$"
        ],
        "experience": [
            r"^experience\s*$", r"^work\s+experience\s*$", r"^professional\s+experience\s*$",
            r"^employment\s+history\s*$", r"^work\s+history\s*$"
        ],
        "skills": [
            r"^skills\s*$", r"^technical\s+skills\s*$", r"^competencies\s*$",
            r"^expertise\s*$", r"^technologies\s*$"
        ],
        "education": [
            r"^education\s*$", r"^academic\s+background\s*$", r"^qualifications\s*$"
        ],
        "certifications": [
            r"^certifications\s*$", r"^certificates\s*$", r"^credentials\s*$",
            r"^professional\s+development\s*$"
        ],
        "projects": [
            r"^projects\s*$", r"^portfolio\s*$", r"^key\s+projects\s*$"
        ]
    }

    # ATS-hostile format patterns
    FORMAT_RISK_PATTERNS = {
        "two_column": [
            r".{80,}\s{3,}\S",  # Multiple columns separated by spaces
            r"\|.{20,}\|.{20,}\|",  # Table-like structures
        ],
        "tables": [
            r"\|.*\|",  # Markdown tables
            r"^\+[-=]+\+[-=]+\+",  # ASCII tables
        ],
        "images_embedded": [
            r"!\[.*\]\(.*\)",  # Markdown images
            r"<img[^>]*>",  # HTML images
        ],
        "non_standard_headings": [
            r"^(?!.*(?:summary|experience|skills|education|projects|certifications)).{1,10}$",
        ]
    }

    BULLET_PATTERNS = [
        r"^[•‣⁃◦○]\s+",  # Unicode bullets
        r"^[\-\*•]\s+",  # Common bullet chars
        r"^\d+\.\s+",  # Numbered lists
    ]

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.section_regex = {}
        for section, patterns in self.SECTION_PATTERNS.items():
            self.section_regex[section] = [
                re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns
            ]

        self.format_risk_regex = {}
        for risk_type, patterns in self.FORMAT_RISK_PATTERNS.items():
            self.format_risk_regex[risk_type] = [
                re.compile(p, re.MULTILINE) for p in patterns
            ]

        self.bullet_regex = [re.compile(p, re.MULTILINE) for p in self.BULLET_PATTERNS]

    def parse(self, resume_text: str) -> Dict[str, ResumeSection]:
        """Parse resume text into structured sections."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty")

        lines = resume_text.splitlines()
        sections: Dict[str, ResumeSection] = {}
        current_section = "header"
        current_content: List[str] = []

        for line in lines:
            stripped = line.rstrip()
            if not stripped:
                continue

            # Check if this line is a section header
            matched_section = self._identify_section(stripped)
            if matched_section and matched_section != current_section:
                # Save previous section
                if current_content:
                    sections[current_section] = self._create_section(
                        current_section, current_content
                    )
                current_section = matched_section
                current_content = []

            current_content.append(stripped)

        # Save last section
        if current_content:
            sections[current_section] = self._create_section(
                current_section, current_content
            )

        # Ensure header section exists
        if "header" not in sections and lines:
            header_content = [line for line in lines[:5] if line.strip()][:3]
            sections["header"] = self._create_section("header", header_content)

        return sections

    def _identify_section(self, line: str) -> Optional[str]:
        """Identify if line is a section header."""
        clean_line = line.strip().lower()

        for section, patterns in self.section_regex.items():
            for pattern in patterns:
                if pattern.match(clean_line):
                    return section
        return None

    def _create_section(self, section_type: str, content: List[str]) -> ResumeSection:
        """Create ResumeSection from content lines."""
        bullets = []
        non_bullets = []

        for line in content:
            if self._is_bullet(line):
                bullets.append(line)
            else:
                non_bullets.append(line)

        section_text = "\n".join(content)
        metadata = self._extract_metadata(section_type, section_text)

        return ResumeSection(
            section_type=section_type,
            content=section_text,
            bullets=bullets,
            metadata=metadata
        )

    def _is_bullet(self, line: str) -> bool:
        """Check if line is a bullet point."""
        for pattern in self.bullet_regex:
            if pattern.match(line):
                return True
        return False

    def _extract_metadata(self, section_type: str, content: str) -> Dict[str, Any]:
        """Extract metadata from section content."""
        metadata = {}

        if section_type == "experience":
            # Extract company names and dates
            metadata["companies"] = self._extract_companies(content)
            metadata["years"] = self._extract_years(content)

        elif section_type == "education":
            metadata["degrees"] = self._extract_degrees(content)
            metadata["institutions"] = self._extract_institutions(content)

        elif section_type == "skills":
            metadata["skill_count"] = len(self._extract_skills(content))

        return metadata

    def _extract_companies(self, content: str) -> List[str]:
        """Extract company names from experience section."""
        companies = []
        lines = content.splitlines()
        for line in lines[:20]:  # Check first 20 lines only
            # Look for lines that might be company entries
            if re.search(r"[A-Z][A-Za-z\s&]+", line) and not self._is_bullet(line):
                potential = line.strip()
                if 3 < len(potential) < 50 and not re.search(r"\d{4}", potential):
                    companies.append(potential)
        return companies[:5]  # Limit to 5 companies

    def _extract_years(self, content: str) -> List[str]:
        """Extract year ranges from content."""
        year_pattern = re.compile(r"\b(20\d\d)\s*[-–]\s*(20\d\d|present)\b")
        return year_pattern.findall(content)

    def _extract_degrees(self, content: str) -> List[str]:
        """Extract degree information."""
        degree_keywords = ["bachelor", "master", "phd", "doctor", "mba", "bs", "ms", "ba", "ma"]
        degrees = []
        for keyword in degree_keywords:
            if keyword.lower() in content.lower():
                degrees.append(keyword)
        return degrees

    def _extract_institutions(self, content: str) -> List[str]:
        """Extract educational institutions."""
        institutions = []
        lines = content.splitlines()
        for line in lines[:10]:
            if re.search(r"[A-Z][A-Za-z\s]+(?:University|College|Institute|School)", line):
                institutions.append(line.strip())
        return institutions[:3]

    def _extract_skills(self, content: str) -> List[str]:
        """Extract individual skills from skills section."""
        # Split by common separators
        separators = r"[\n,;•\-\|]+"
        raw_skills = re.split(separators, content)
        skills = [s.strip() for s in raw_skills if 2 < len(s.strip()) < 50]
        return skills

    def detect_format_risks(self, resume_text: str) -> List[FormatRisk]:
        """Detect ATS-hostile formatting risks."""
        risks: List[FormatRisk] = []

        for risk_type, patterns in self.format_risk_regex.items():
            for pattern in patterns:
                matches = pattern.findall(resume_text)
                if matches:
                    severity = "high" if risk_type in ["two_column", "tables"] else "medium"
                    risks.append(FormatRisk(
                        risk_type=risk_type,
                        severity=severity,
                        location=f"{len(matches)} occurrence(s) found",
                        recommendation=self._get_risk_recommendation(risk_type)
                    ))

        return risks

    def _get_risk_recommendation(self, risk_type: str) -> str:
        """Get recommendation for format risk."""
        recommendations = {
            "two_column": "Convert to single-column layout for ATS compatibility",
            "tables": "Replace tables with bullet points and standard formatting",
            "images_embedded": "Remove embedded images; use text-only format",
            "non_standard_headings": "Use standard section headings (Summary, Experience, Skills, etc.)"
        }
        return recommendations.get(risk_type, "Review formatting for ATS compatibility")


class JDParser:
    """Parse job description into structured requirements."""

    SKILL_PATTERNS = [
        r"(?:required|must have|need|essential)[\s:]+([^.]*?(?:skills?|technologies?|experience|knowledge)[^.]*\.)",
        r"(?:preferred|nice to have|bonus|plus)[\s:]+([^.]*?(?:skills?|technologies?|experience)[^.]*\.)",
    ]

    REQUIREMENT_PATTERNS = [
        r"(?:must|required|essential)[\s:]+([^.]{10,150})",
        r"(?:years|yrs?)\s+of\s+(?:experience|exp)[\s:]+([^.]{10,100})",
    ]

    SENIORITY_SIGNALS = [
        "senior", "lead", "principal", "staff", "junior", "intern", "entry",
        "manager", "director", "vp", "chief", "head", "sr", "jr"
    ]

    def __init__(self):
        self.skill_regex = [re.compile(p, re.IGNORECASE) for p in self.SKILL_PATTERNS]
        self.requirement_regex = [re.compile(p, re.IGNORECASE) for p in self.REQUIREMENT_PATTERNS]

    def parse(self, jd_text: str) -> JDRequirements:
        """Parse job description into structured requirements."""
        if not jd_text or not jd_text.strip():
            raise ValueError("Job description text is empty")

        jd_lower = jd_text.lower()

        # Extract skills
        required_skills, preferred_skills = self._extract_skills(jd_text)

        # Extract responsibilities
        responsibilities = self._extract_responsibilities(jd_text)

        # Extract seniority signals
        seniority_signals = self._extract_seniority(jd_lower)

        # Extract hard requirements
        hard_requirements = self._extract_hard_requirements(jd_text)

        return JDRequirements(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=responsibilities,
            seniority_signals=seniority_signals,
            hard_requirements=hard_requirements,
            raw_text=jd_text
        )

    def _extract_skills(self, jd_text: str) -> tuple[List[str], List[str]]:
        """Extract required and preferred skills."""
        required, preferred = [], []

        # Look for explicit skill sections
        lines = jd_text.splitlines()
        in_skill_section = False
        skill_type = "required"

        for line in lines:
            lower = line.lower()
            if "required skill" in lower or "must have" in lower:
                in_skill_section = True
                skill_type = "required"
            elif "preferred skill" in lower or "nice to have" in lower:
                in_skill_section = True
                skill_type = "preferred"
            elif in_skill_section and not line.strip():
                in_skill_section = False
            elif in_skill_section:
                skills = self._parse_skill_line(line)
                if skill_type == "required":
                    required.extend(skills)
                else:
                    preferred.extend(skills)

        # Remove duplicates while preserving order
        required = list(dict.fromkeys(required))
        preferred = list(dict.fromkeys(preferred))

        return required[:20], preferred[:20]

    def _parse_skill_line(self, line: str) -> List[str]:
        """Parse individual skills from a line."""
        # Split by common separators
        separators = r"[,;•\-\|]+"
        skills = re.split(separators, line)
        return [s.strip() for s in skills if 2 < len(s.strip()) < 50]

    def _extract_responsibilities(self, jd_text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        lines = jd_text.splitlines()

        in_responsibility_section = False
        for line in lines:
            lower = line.lower()
            if any(k in lower for k in ["responsibility", "you will", "role involves", "duties"]):
                in_responsibility_section = True
            elif in_responsibility_section and not line.strip():
                in_responsibility_section = False
            elif in_responsibility_section:
                if self._is_bullet(line) or len(line) > 30:
                    responsibilities.append(line.strip())

        return responsibilities[:10]

    def _extract_seniority(self, jd_lower: str) -> List[str]:
        """Extract seniority signals from JD."""
        found = []
        for signal in self.SENIORITY_SIGNALS:
            if signal in jd_lower:
                found.append(signal)
        return found

    def _extract_hard_requirements(self, jd_text: str) -> List[str]:
        """Extract hard/non-negotiable requirements."""
        hard_reqs = []

        # Look for "must have", "required", "essential" patterns
        for pattern in self.requirement_regex:
            matches = pattern.findall(jd_text)
            hard_reqs.extend(matches)

        return list(set(hard_reqs[:15]))


class ProfileIntake:
    """Main profile intake orchestrator."""

    def __init__(self):
        self.resume_parser = ResumeParser()
        self.jd_parser = JDParser()

    def process(
        self,
        resume_text: str,
        jd_text: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> NormalizedProfile:
        """Process resume and JD into normalized profile."""
        constraints_dict = constraints or {}

        # Build candidate constraints
        candidate_constraints = CandidateConstraints(
            geography=constraints_dict.get("geography"),
            work_authorization=constraints_dict.get("work_authorization"),
            salary_band=constraints_dict.get("salary_band"),
            remote_preference=constraints_dict.get("remote_preference"),
            career_switch=constraints_dict.get("career_switch", False),
            target_role=constraints_dict.get("target_role"),
            target_seniority=constraints_dict.get("target_seniority")
        )

        # Check for blocking conditions
        if not resume_text or not resume_text.strip():
            return NormalizedProfile(
                status=ParseStatus.BLOCKED_MISSING_RESUME,
                resume_sections={},
                jd_requirements=None,
                constraints=candidate_constraints,
                format_risks=[],
                career_switch=candidate_constraints.career_switch,
                raw_resume="",
                block_reason="Resume text is required but was not provided"
            )

        if not jd_text or not jd_text.strip():
            return NormalizedProfile(
                status=ParseStatus.BLOCKED_MISSING_JD,
                resume_sections={},
                jd_requirements=None,
                constraints=candidate_constraints,
                format_risks=[],
                career_switch=candidate_constraints.career_switch,
                raw_resume=resume_text,
                block_reason="Job description or target role is required for fit scoring"
            )

        # Parse resume
        try:
            resume_sections = self.resume_parser.parse(resume_text)
        except Exception as e:
            return NormalizedProfile(
                status=ParseStatus.ERROR_PARSE_FAILURE,
                resume_sections={},
                jd_requirements=None,
                constraints=candidate_constraints,
                format_risks=[],
                career_switch=candidate_constraints.career_switch,
                raw_resume=resume_text,
                block_reason=f"Failed to parse resume: {str(e)}"
            )

        # Detect format risks
        format_risks = self.resume_parser.detect_format_risks(resume_text)

        # Parse job description
        try:
            jd_requirements = self.jd_parser.parse(jd_text)
        except Exception as e:
            return NormalizedProfile(
                status=ParseStatus.ERROR_PARSE_FAILURE,
                resume_sections=resume_sections,
                jd_requirements=None,
                constraints=candidate_constraints,
                format_risks=format_risks,
                career_switch=candidate_constraints.career_switch,
                raw_resume=resume_text,
                block_reason=f"Failed to parse job description: {str(e)}"
            )

        return NormalizedProfile(
            status=ParseStatus.SUCCESS,
            resume_sections=resume_sections,
            jd_requirements=jd_requirements,
            constraints=candidate_constraints,
            format_risks=format_risks,
            career_switch=candidate_constraints.career_switch,
            raw_resume=resume_text
        )

    def validate_quality_gates(self, profile: NormalizedProfile) -> tuple[bool, List[str]]:
        """Validate that profile meets quality gates."""
        failures = []

        if profile.status != ParseStatus.SUCCESS:
            failures.append(f"Profile parsing failed: {profile.block_reason}")

        if not profile.resume_sections:
            failures.append("No resume sections were parsed")

        if not profile.jd_requirements:
            failures.append("Job description requirements were not parsed")

        if profile.format_risks and any(r.severity == "high" for r in profile.format_risks):
            failures.append("High-severity format risks detected that may block ATS parsing")

        return len(failures) == 0, failures


# CLI entry point
def main():
    """CLI entry point for profile intake."""
    import sys
    import json

    if len(sys.argv) < 3:
        print("Usage: profile_intake.py <resume_file> <jd_file> [constraints.json]")
        sys.exit(1)

    resume_file = Path(sys.argv[1])
    jd_file = Path(sys.argv[2])
    constraints_file = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if not resume_file.exists():
        print(f"Error: Resume file not found: {resume_file}")
        sys.exit(1)

    if not jd_file.exists():
        print(f"Error: JD file not found: {jd_file}")
        sys.exit(1)

    resume_text = resume_file.read_text(encoding="utf-8")
    jd_text = jd_file.read_text(encoding="utf-8")

    constraints = None
    if constraints_file and constraints_file.exists():
        constraints = json.loads(constraints_file.read_text(encoding="utf-8"))

    intake = ProfileIntake()
    profile = intake.process(resume_text, jd_text, constraints)

    # Output as JSON
    output = dataclasses.asdict(profile)
    print(json.dumps(output, indent=2, default=str))

    # Return exit code based on status
    sys.exit(0 if profile.status == ParseStatus.SUCCESS else 1)


if __name__ == "__main__":
    main()
