#!/usr/bin/env python3
"""Comprehensive Test Suite - CV/Resume Optimizer (Idea 49)

Production-grade test suite covering all phases and test scenarios.
Implements automated testing for all components and end-to-end workflows.
"""

from __future__ import annotations

import sys
import pathlib
import unittest
import dataclasses
from typing import Optional, Dict, Any
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

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
    QualityReviewer, ChallengeLog, AssumptionChallenge, FairnessCheck
)
from harness import MainHarness, HarnessInput, HarnessOutput, HarnessStatus


class TestProfileIntake(unittest.TestCase):
    """Test profile intake functionality."""

    def setUp(self):
        self.intake = ProfileIntake()

    def test_successful_intake(self):
        """Test successful intake with valid resume and JD."""
        resume = """
        John Doe
        john@example.com

        SUMMARY
        Software engineer with 5 years experience building scalable systems.

        EXPERIENCE
        - Led team of 5 engineers to build microservices architecture
        - Increased system performance by 40% through optimization
        - Developed RESTful APIs serving 1M+ users

        SKILLS
        Python, JavaScript, AWS, Docker, Kubernetes, SQL
        """

        jd = """
        Senior Software Engineer

        Required Skills:
        - Python, AWS, Docker
        - 5+ years experience

        Responsibilities:
        - Design and implement scalable systems
        - Mentor junior engineers
        """

        profile = self.intake.process(resume_text=resume, jd_text=jd)

        self.assertEqual(profile.status, ParseStatus.SUCCESS)
        self.assertIsNotNone(profile.resume_sections)
        self.assertIsNotNone(profile.jd_requirements)
        self.assertFalse(profile.career_switch)

    def test_missing_jd_blocked(self):
        """Test that missing JD blocks processing."""
        resume = "Jane Doe\nSoftware Engineer"
        profile = self.intake.process(resume_text=resume, jd_text=None)

        self.assertEqual(profile.status, ParseStatus.BLOCKED_MISSING_JD)
        self.assertIsNotNone(profile.block_reason)

    def test_missing_resume_blocked(self):
        """Test that missing resume blocks processing."""
        jd = "Senior Software Engineer position"
        profile = self.intake.process(resume_text="", jd_text=jd)

        self.assertEqual(profile.status, ParseStatus.BLOCKED_MISSING_RESUME)

    def test_format_risk_detection(self):
        """Test detection of ATS-hostile formatting."""
        resume_with_tables = """
        John Doe

        | Company | Role | Years |
        |---------|------|-------|
        | Tech Corp | Senior Dev | 2020-2023 |
        """

        profile = self.intake.process(
            resume_text=resume_with_tables,
            jd_text="Software Engineer"
        )

        self.assertTrue(any(r.risk_type == "tables" for r in profile.format_risks))

    def test_career_switch_flag(self):
        """Test career switch flag is respected."""
        constraints = {"career_switch": True, "target_role": "UX Designer"}
        profile = self.intake.process(
            resume_text="Teacher with 10 years experience",
            jd_text="Junior UX Designer",
            constraints=constraints
        )

        self.assertTrue(profile.career_switch)
        self.assertEqual(profile.constraints.target_role, "UX Designer")


class TestFrameworkSelector(unittest.TestCase):
    """Test framework selection functionality."""

    def setUp(self):
        self.selector = FrameworkSelector()

    def test_framework_selection_software_engineering(self):
        """Test framework selection for software engineering role."""
        selection = self.selector.select_frameworks(
            role_family="software engineering",
            seniority="senior"
        )

        self.assertEqual(selection.role_family, RoleFamily.SOFTWARE_ENGINEERING)
        self.assertEqual(selection.seniority, Seniority.SENIOR)
        self.assertGreaterEqual(len(selection.frameworks), 2)

    def test_dimension_weights_sum_to_100(self):
        """Test that dimension weights sum to 100%."""
        selection = self.selector.select_frameworks(
            role_family="data science",
            seniority="mid"
        )

        total_weight = sum(selection.dimension_weights.values())
        self.assertAlmostEqual(total_weight, 100.0, places=1)

    def test_seniority_weight_adjustments(self):
        """Test that weights are adjusted for seniority."""
        entry_selection = self.selector.select_frameworks("software", "entry")
        exec_selection = self.selector.select_frameworks("software", "executive")

        # Senior roles should weight impact higher than keywords
        entry_keyword_weight = entry_selection.dimension_weights.get("ats_keyword_coverage", 0)
        exec_keyword_weight = exec_selection.dimension_weights.get("ats_keyword_coverage", 0)

        self.assertGreater(entry_keyword_weight, exec_keyword_weight)

    def test_quality_gates(self):
        """Test framework selection quality gates."""
        selection = self.selector.select_frameworks("sales", "manager")
        passes, failures = self.selector.validate_quality_gates(selection)

        self.assertTrue(passes)
        self.assertEqual(len(failures), 0)


class TestScoringEngine(unittest.TestCase):
    """Test scoring engine functionality."""

    def setUp(self):
        self.engine = ScoringEngine()

        # Create mock profile
        self.profile = Mock()
        self.profile.raw_resume = """
        Software Engineer with 5 years experience
        - Led team of 5 engineers
        - Increased performance by 40%
        - Built system serving 1M users
        """
        self.profile.resume_sections = {
            "experience": Mock(bullets=[
                "Led team of 5 engineers",
                "Increased performance by 40%",
                "Built system serving 1M users"
            ])
        }
        self.profile.format_risks = []

        # Create mock JD requirements
        self.profile.jd_requirements = Mock()
        self.profile.jd_requirements.required_skills = [
            "python", "aws", "docker", "kubernetes", "leadership"
        ]
        self.profile.jd_requirements.seniority_signals = ["senior"]

        # Create mock frameworks
        self.frameworks = Mock()
        self.frameworks.dimension_weights = {
            "ats_keyword_coverage": 25.0,
            "impact_quantification": 20.0,
            "role_seniority_alignment": 20.0,
            "readability_6_sec_scan": 15.0,
            "formatting_ats_parseability": 10.0,
            "consistency_error_free": 10.0,
        }

    def test_ats_coverage_calculation(self):
        """Test ATS keyword coverage calculation."""
        result = self.engine.compute_scores(self.profile, self.frameworks)

        self.assertIsNotNone(result.ats_gap)
        self.assertGreaterEqual(result.ats_gap.coverage_percentage, 0)
        self.assertLessEqual(result.ats_gap.coverage_percentage, 100)

    def test_star_quantification_scoring(self):
        """Test STAR quantification scoring."""
        result = self.engine.compute_scores(self.profile, self.frameworks)

        self.assertIsNotNone(result.star_analysis)
        self.assertEqual(result.star_analysis.total_bullets, 3)
        self.assertGreater(result.star_analysis.quantified_bullets, 0)

    def test_total_score_calculation(self):
        """Test total score is calculated correctly."""
        result = self.engine.compute_scores(self.profile, self.frameworks)

        self.assertGreaterEqual(result.total_score, 0)
        self.assertLessEqual(result.total_score, 100)
        self.assertIsInstance(result.verdict_band, ScoreBand)

    def test_dimension_scores_have_evidence(self):
        """Test all dimension scores have evidence."""
        result = self.engine.compute_scores(self.profile, self.frameworks)

        for dim_score in result.dimension_scores:
            self.assertTrue(len(dim_score.evidence) > 0)
            self.assertIsNotNone(dim_score.rationale)


class TestImprovementRoadmap(unittest.TestCase):
    """Test improvement roadmap functionality."""

    def setUp(self):
        self.builder = ImprovementRoadmapBuilder()

        # Create mock scoring result with low scores
        self.scoring_result = Mock()
        self.scoring_result.dimension_scores = [
            Mock(dimension="ATS Keyword Coverage", score=40),
            Mock(dimension="STAR Quantification", score=50),
        ]
        self.scoring_result.ats_gap = Mock(
            matched_keywords=["python"],
            missing_keywords=["aws", "docker", "kubernetes"]
        )
        self.scoring_result.star_analysis = Mock(
            quantified_bullets=1,
            total_bullets=5,
            missing_quantification=["Led team", "Managed project"]
        )

        # Create mock profile
        self.profile = Mock()
        self.profile.format_risks = []
        self.profile.raw_resume = "Software Engineer"
        self.profile.resume_sections = {}

    def test_roadmap_generation(self):
        """Test roadmap is generated for low scores."""
        roadmap = self.builder.build_roadmap(self.scoring_result, self.profile)

        self.assertIsNotNone(roadmap)
        self.assertGreater(len(roadmap.actions), 0)

    def test_actions_have_effort_and_impact(self):
        """Test all actions have effort and impact tags."""
        roadmap = self.builder.build_roadmap(self.scoring_result, self.profile)

        for action in roadmap.actions:
            self.assertIsInstance(action.effort, Effort)
            self.assertIsInstance(action.impact, Impact)

    def test_actions_have_before_after(self):
        """Test actions have before/after samples."""
        roadmap = self.builder.build_roadmap(self.scoring_result, self.profile)

        for action in roadmap.actions:
            # Most actions should have before/after
            if "quantify" in action.action.lower():
                self.assertIsNotNone(action.before)
                self.assertIsNotNone(action.after)

    def test_quick_wins_categorized(self):
        """Test quick wins are properly categorized."""
        roadmap = self.builder.build_roadmap(self.scoring_result, self.profile)

        for action in roadmap.quick_wins:
            self.assertEqual(action.effort, Effort.SMALL)


class TestQualityReviewer(unittest.TestCase):
    """Test quality reviewer functionality."""

    def setUp(self):
        self.reviewer = QualityReviewer()

        # Create mock scoring result
        self.scoring_result = Mock()
        self.scoring_result.dimension_scores = [
            Mock(
                dimension="ATS Coverage",
                score=70,
                evidence=["Matched 5 of 10 keywords"],
                rationale="Moderate keyword match"
            )
        ]
        self.scoring_result.ats_gap = Mock(
            matched_keywords=["python", "aws"],
            missing_keywords=["docker"]
        )

        # Create mock profile
        self.profile = Mock()
        self.profile.resume_sections = {
            "experience": Mock(content="Worked at Tech Corp 2020-2023")
        }
        self.profile.format_risks = []
        self.profile.constraints = Mock(
            target_seniority="mid",
            target_role="software engineer",
            geography="US"
        )
        self.profile.raw_resume = "Software Engineer"
        self.profile.jd_requirements = Mock(
            required_skills=["python"],
            preferred_skills=["docker"]
        )

    def test_assumption_testing(self):
        """Test assumptions are challenged."""
        challenge_log = self.reviewer.review(self.scoring_result, self.profile)

        self.assertGreater(challenge_log.challenges_tested, 0)
        self.assertGreater(len(challenge_log.assumption_challenges), 0)

    def test_fairness_checks(self):
        """Test fairness checks are performed."""
        challenge_log = self.reviewer.review(self.scoring_result, self.profile)

        self.assertGreater(len(challenge_log.fairness_checks), 0)

    def test_minimum_three_assumptions_tested(self):
        """Test at least 3 assumptions are tested."""
        challenge_log = self.reviewer.review(self.scoring_result, self.profile)

        self.assertGreaterEqual(challenge_log.challenges_tested, 3)

    def test_quality_gate_validation(self):
        """Test quality gate validation."""
        challenge_log = self.reviewer.review(self.scoring_result, self.profile)
        passes, failures = self.reviewer.validate_quality_gates(challenge_log)

        self.assertTrue(passes)
        self.assertEqual(len(failures), 0)


class TestMainHarness(unittest.TestCase):
    """Test main harness orchestration."""

    def setUp(self):
        self.harness = MainHarness(enable_web_search=False)

    def test_successful_end_to_end(self):
        """Test successful end-to-end processing."""
        input_data = HarnessInput(
            resume_text="""
            John Doe
            Senior Software Engineer

            EXPERIENCE
            - Led team of 5 engineers
            - Increased performance by 40%
            - Built system serving 1M users

            SKILLS
            Python, AWS, Docker, Kubernetes
            """,
            jd_text="""
            Senior Software Engineer

            Required Skills:
            Python, AWS, Docker, Kubernetes
            """,
            target_role="Senior Software Engineer",
            target_seniority="senior"
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)
        self.assertIsNotNone(output.profile)
        self.assertIsNotNone(output.frameworks)
        self.assertIsNotNone(output.scoring)
        self.assertIsNotNone(output.roadmap)
        self.assertIsNotNone(output.review)

    def test_blocked_without_jd(self):
        """Test processing is blocked without JD."""
        input_data = HarnessInput(
            resume_text="Software Engineer",
            jd_text=None
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.BLOCKED)
        self.assertIsNotNone(output.block_reason)

    def test_quality_gates_checked(self):
        """Test quality gates are checked and logged."""
        input_data = HarnessInput(
            resume_text="Engineer with experience",
            jd_text="Senior Engineer required"
        )

        output = self.harness.process(input_data)

        # Should have both passes and failures logged
        self.assertIsInstance(output.quality_gate_passes, list)
        self.assertIsInstance(output.quality_gate_failures, list)

    def test_output_formatting(self):
        """Test output can be formatted as report."""
        input_data = HarnessInput(
            resume_text="Software Engineer",
            jd_text="Senior Software Engineer position"
        )

        output = self.harness.process(input_data)

        if output.status == HarnessStatus.SUCCESS:
            report = self.harness.format_output(output)
            self.assertIn("Resume Fit Report", report)


class TestScenarios(unittest.TestCase):
    """Test scenarios from test-scenarios.md."""

    def setUp(self):
        self.harness = MainHarness(enable_web_search=False)

    def test_scenario_1_senior_swe(self):
        """Scenario 1: Senior SWE resume vs SWE JD."""
        resume = """
        John Smith
        Senior Backend Engineer
        john@example.com

        SUMMARY
        Senior backend engineer with 7 years experience building scalable systems.

        EXPERIENCE
        Senior Backend Engineer | TechCorp | 2020-Present
        - Led migration from monolith to microservices, reducing deployment time by 60%
        - Managed team of 4 engineers, implementing code review and CI/CD practices
        - Built RESTful APIs handling 10M+ daily requests with 99.9% uptime

        Backend Engineer | StartupCo | 2018-2020
        - Developed Python services using Django and FastAPI
        - Optimized database queries, improving response times by 40%
        - Implemented caching layer using Redis, reducing load by 35%

        SKILLS
        Python, Go, Kubernetes, AWS, PostgreSQL, Redis, Docker, CI/CD
        """

        jd = """
        Senior Backend Engineer

        Required Skills:
        - Go, Kubernetes, AWS
        - 5+ years backend experience
        - Microservices architecture

        Responsibilities:
        - Design and implement scalable backend systems
        - Mentor junior engineers
        - Drive technical decisions
        """

        input_data = HarnessInput(
            resume_text=resume,
            jd_text=jd,
            target_role="Senior Backend Engineer",
            target_seniority="senior"
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)

        # Check dimension scores exist
        self.assertGreater(len(output.scoring.dimension_scores), 0)

        # Check ATS gap analysis
        self.assertIsNotNone(output.scoring.ats_gap)

        # Check roadmap has effort/impact
        for action in output.roadmap.actions:
            self.assertIsNotNone(action.effort)
            self.assertIsNotNone(action.impact)

    def test_scenario_2_career_switcher(self):
        """Scenario 2: Career switcher (teacher → UX designer)."""
        resume = """
        Jane Johnson
        High School Teacher
        jane@example.com

        SUMMARY
        Passionate educator with 8 years experience teaching and curriculum development.

        EXPERIENCE
        High School Teacher | Public Schools | 2016-Present
        - Developed curriculum for 150+ students across multiple subjects
        - Conducted user research through student feedback surveys
        - Created engaging presentations and visual materials
        - Collaborated with team of 10 teachers on educational programs

        EDUCATION
        Master of Education | State University | 2016
        Bachelor of Arts | Liberal College | 2014
        """

        jd = """
        Junior UX Designer

        Required:
        - User research experience
        - Presentation skills
        - Collaboration abilities

        Preferred:
        - Portfolio of design projects
        """

        input_data = HarnessInput(
            resume_text=resume,
            jd_text=jd,
            target_role="Junior UX Designer",
            target_seniority="entry",
            career_switch=True
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)

        # Check for transferable skill mapping
        roadmap_actions = output.roadmap.actions
        self.assertTrue(any("transferable" in a.action.lower() for a in roadmap_actions))

    def test_scenario_3_no_jd_blocked(self):
        """Scenario 3: No JD provided (blocked path)."""
        input_data = HarnessInput(
            resume_text="Software Engineer looking for opportunities",
            jd_text=None
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.BLOCKED)
        self.assertIn("job description", output.block_reason.lower())

    def test_scenario_4_ats_hostile_formatting(self):
        """Scenario 4: ATS-hostile formatting."""
        resume = """
        John Doe
        Software Engineer

        | Company | Role | Years |
        |---------|------|-------|
        | TechCorp | Senior Dev | 2020-2023 |
        | StartupCo | Dev | 2018-2020 |

        Skills: Python, Java, AWS
        """

        input_data = HarnessInput(
            resume_text=resume,
            jd_text="Software Engineer needed"
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)

        # Check format risks detected
        self.assertGreater(len(output.profile.format_risks), 0)

        # Check ATS score penalized
        ats_score = next(
            (d.score for d in output.scoring.dimension_scores if "format" in d.dimension.lower()),
            None
        )
        self.assertIsNotNone(ats_score)
        self.assertLess(ats_score, 100)

    def test_scenario_5_keyword_stuffing(self):
        """Scenario 5: Keyword-stuffed resume."""
        resume = """
        John Doe
        Software Engineer

        Experience working with Python, Java, JavaScript, Go, Rust, C++, Python,
        Python, Docker, Kubernetes, AWS, Azure, GCP, Python, Kubernetes, Docker.

        More experience with Python, Docker, Kubernetes, AWS, Java, JavaScript.

        SKILLS
        Python, Python, Python, Docker, Kubernetes, AWS, Python, Kubernetes
        """

        jd = """
        Senior Software Engineer

        Required:
        - Python, Docker, Kubernetes
        - AWS experience
        """

        input_data = HarnessInput(
            resume_text=resume,
            jd_text=jd
        )

        output = self.harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)

        # Check stuffing detected
        self.assertTrue(output.scoring.ats_gap.stuffing_detected)

        # Check penalty applied
        self.assertGreater(output.scoring.ats_gap.stuffing_penalty, 0)

    def test_scenario_6_offline_mode(self):
        """Scenario 6: Offline/degraded mode."""
        harness = MainHarness(enable_web_search=False)

        input_data = HarnessInput(
            resume_text="Software Engineer",
            jd_text="Senior Software Engineer"
        )

        output = harness.process(input_data)

        self.assertEqual(output.status, HarnessStatus.SUCCESS)
        self.assertTrue(output.offline_mode)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProfileIntake))
    suite.addTests(loader.loadTestsFromTestCase(TestFrameworkSelector))
    suite.addTests(loader.loadTestsFromTestCase(TestScoringEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestImprovementRoadmap))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityReviewer))
    suite.addTests(loader.loadTestsFromTestCase(TestMainHarness))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
