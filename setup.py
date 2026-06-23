#!/usr/bin/env python3
"""Setup script for CV/Resume Optimizer"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README = Path(__file__).parent / "README.md"
try:
    LONG_DESCRIPTION = README.read_text(encoding="utf-8")
except Exception:
    LONG_DESCRIPTION = "Production-grade resume analysis system with ATS-aware scoring and improvement roadmaps"

setup(
    name="cv-resume-optimizer",
    version="1.0.0",
    description="Score resumes against job descriptions with ATS-aware frameworks and targeted rewrite roadmaps",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="CV/Resume Optimizer Team",
    python_requires=">=3.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "cv-optimizer=harness:main",
            "cv-knowledge-update=tools.knowledge_updater:main",
        ],
    },
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
    ],
    extras_require={
        "crawl": ["crawl4ai>=0.2.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Employment",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="resume cv job-description ATS scoring optimization career",
    project_urls={
        "Documentation": "https://github.com/your-org/cv-resume-optimizer#readme",
        "Source": "https://github.com/your-org/cv-resume-optimizer",
        "Tracker": "https://github.com/your-org/cv-resume-optimizer/issues",
    },
)
