"""
CV/Resume Optimizer - Production Grade Implementation

A comprehensive resume analysis system that scores resumes against job descriptions
using ATS-aware frameworks and provides prioritized rewrite roadmaps.

Main entry point: harness.MainHarness

Modules:
- harness: Main orchestrator
- profile_intake: Resume and JD parsing
- framework_selector: Scoring framework selection
- scoring_engine: Multi-dimensional scoring
- improvement_roadmap: Prioritized action generation
- quality_reviewer: Devil's advocate validation
"""

__version__ = "1.0.0"
__author__ = "CV/Resume Optimizer Team"

from .harness import MainHarness, HarnessInput, HarnessOutput, HarnessStatus

__all__ = [
    "MainHarness",
    "HarnessInput",
    "HarnessOutput",
    "HarnessStatus",
]
