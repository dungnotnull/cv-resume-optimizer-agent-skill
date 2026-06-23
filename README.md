# CV/Resume Optimizer

**Production-grade resume analysis system that scores resumes against job descriptions using ATS-aware frameworks and provides targeted rewrite roadmaps.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/your-org/cv-resume-optimizer)

## Overview

This tool analyzes resumes against specific job descriptions using evidence-based recruiting frameworks:

- **ATS Keyword Coverage** - Measures how well your resume matches JD keywords
- **STAR Method** - Scores impact quantification in bullet points
- **O*NET Alignment** - Maps skills to standardized occupation taxonomies
- **6-Second Scan** - Evaluates readability for recruiter scan heuristics
- **Format Parseability** - Detects ATS-hostile formatting risks
- **Consistency** - Checks for errors and inconsistencies

The output includes:
- Multi-dimensional fit score (0-100) with evidence
- ATS keyword gap analysis
- Prioritized rewrite roadmap with before/after examples
- Effort/impact tags for each recommendation
- Quality assurance with assumption testing

## Features

✅ **Production-Grade** - Full implementation with comprehensive error handling
✅ **ATS-Aware** - Detects and flags ATS-hostile formatting
✅ **Evidence-Based** - Every score cites specific frameworks and evidence
✅ **Quality Gated** - Devil's advocate validation challenges assumptions
✅ **Offline Mode** - Works without internet using cached knowledge
✅ **Career Switcher Support** - Maps transferable skills via O*NET
✅ **Open Source** - Ready for contribution and extension

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/cv-resume-optimizer.git
cd cv-resume-optimizer

# Install dependencies
pip install -r requirements.txt

# Or install with optional crawling support
pip install -e ".[crawl]"
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

```bash
# Basic analysis
python -m src.harness resume.txt jd.txt --role "Senior Software Engineer" --seniority senior

# Offline mode (no web search)
python -m src.harness resume.txt jd.txt --offline

# JSON output for automation
python -m src.harness resume.txt jd.txt --output json > results.json

# Specify output file
python -m src.harness resume.txt jd.txt --output report > analysis.md
```

### Python API

```python
from src import MainHarness, HarnessInput

# Initialize harness
harness = MainHarness(enable_web_search=False)

# Prepare input
input_data = HarnessInput(
    resume_text=open("resume.txt").read(),
    jd_text=open("jd.txt").read(),
    target_role="Senior Backend Engineer",
    target_seniority="senior",
    career_switch=False
)

# Process and get results
output = harness.process(input_data)

# Check status
if output.status == HarnessStatus.SUCCESS:
    # Get formatted report
    report = harness.format_output(output)
    print(report)

    # Or get JSON
    import json
    results = harness.to_json(output)
else:
    print(f"Blocked: {output.block_reason}")
```

### Example Output

```
# Resume Fit Report — Senior Backend Engineer

## 1. Snapshot
**Overall Fit Score:** 72/100 🟡
**Verdict:** Competitive

## 2. Dimension Scores
| Dimension | Score | Weight | Evidence |
|-----------|-------|--------|----------|
| ATS Keyword Coverage | 65% | 25% | Matched 5 of 8 JD keywords |
| Impact Quantification (STAR) | 70% | 20% | 14/20 bullets quantified |
| Role/Seniority Alignment | 75% | 20% | Seniority alignment analysis |
| Readability & 6-Second Scan | 80% | 15% | Role title in top third |
| Formatting/ATS-Parseability | 85% | 10% | No format risks detected |
| Consistency & Error-Free | 90% | 10% | No consistency issues |

## 3. ATS Keyword Gap
**Coverage:** 65%
**Matched:** python, aws, docker, restful, microservices
**Missing:** kubernetes, terraform, graphql

## 6. Prioritized Rewrite Roadmap
| Priority | Action | Effort | Impact | Dimension |
|----------|--------|--------|--------|------------|
| 1 | Integrate missing JD keywords: Kubernetes, Terraform | M | High | ATS Keyword Coverage |
| 2 | Quantify impact: "Led team" → "Led team of 5 engineers..." | S | High | STAR Quantification |
| 3 | Add GraphQL to skills section with project example | S | Med | ATS Keyword Coverage |
```

## Architecture

The system consists of six main modules:

1. **Profile Intake** (`profile_intake.py`)
   - Parses resume sections and JD requirements
   - Detects ATS-hostile formatting risks
   - Validates inputs and blocks if JD missing

2. **Framework Selector** (`framework_selector.py`)
   - Chooses scoring frameworks based on role/seniority
   - Adjusts dimension weights appropriately
   - Cites all framework sources

3. **Scoring Engine** (`scoring_engine.py`)
   - Computes multi-dimensional fit scores
   - Analyzes ATS keyword coverage and gaps
   - Scores STAR quantification
   - Detects keyword stuffing

4. **Improvement Roadmap** (`improvement_roadmap.py`)
   - Generates prioritized rewrite actions
   - Provides before/after examples
   - Tags effort (S/M/L) and impact (Low/Med/High)

5. **Quality Reviewer** (`quality_reviewer.py`)
   - Challenges all assumptions
   - Performs fairness checks
   - Validates evidence for claims

6. **Main Harness** (`harness.py`)
   - Orchestrates the complete pipeline
   - Validates all quality gates
   - Formats final output

## Knowledge Updates

The system includes a knowledge crawler that updates the domain knowledge base:

```bash
# Preview updates (dry-run)
python tools/knowledge_updater.py --dry-run

# Run actual update
python tools/knowledge_updater.py

# Limit number of entries
python tools/knowledge_updater.py --limit 10

# Specific sources only
python tools/knowledge_updater.py --sources "ArXiv cs.IR,O*NET"
```

Sources include:
- ArXiv cs.IR/cs.CL (academic research)
- O*NET Online (occupation taxonomy)
- BLS Occupational Outlook (government data)
- LinkedIn Economic Graph (industry reports)

## Testing

Run the comprehensive test suite:

```bash
python tests/test_suite.py
```

The test suite covers:
- Unit tests for all modules
- Integration tests for end-to-end workflows
- All 6 documented test scenarios
- Quality gate validation

## Contributing

We welcome contributions! Areas for enhancement:

- Additional framework support
- New crawling sources
- Enhanced scoring algorithms
- International language support
- Web UI development

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built on established research:
- **STAR Method** - Behavioral interviewing standards
- **Ladders 6-Second Scan** - Eye-tracking studies on resume review
- **O*NET** - US Department of Labor occupation taxonomy
- **ATS Vendor Research** - Workday, Greenhouse, Taleo documentation

## Citation

If you use this tool in research, please cite:

```
CV/Resume Optimizer v1.0.0
Production-grade resume analysis with ATS-aware frameworks
https://github.com/your-org/cv-resume-optimizer
```

## Support

- **Documentation**: See `PROJECT-detail.md` for architecture details
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**Status**: Production Ready | **Version**: 1.0.0 | **Date**: 2026-06-23
