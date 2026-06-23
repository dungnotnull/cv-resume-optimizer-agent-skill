#!/usr/bin/env python3
"""knowledge_updater.py — CV/Resume Optimizer (Idea 49)

Production-grade knowledge updater that crawls authoritative labor-market &
resume-science sources, scores by recency + relevance, and appends deduplicated
entries to SECOND-KNOWLEDGE-BRAIN.md.

Features:
- Multiple crawler backends (crawl4ai, requests+BeautifulSoup)
- Smart deduplication using content hashing
- Relevance scoring based on domain keywords
- Automatic categorization and tagging
- Dry-run mode for testing
- Configurable source lists and queries
- Error handling and graceful degradation
- Progress reporting and logging

Usage:
    python knowledge_updater.py [--dry-run] [--sources SOURCE] [--limit N]
    python knowledge_updater.py --update-cache  # Pre-warm cache

Schedule: Run weekly via cron or equivalent.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import pathlib
import re
import sys
import time
from dataclasses import dataclasses, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("knowledge_updater")

# Paths
BRAIN_PATH = pathlib.Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
CACHE_PATH = pathlib.Path(__file__).resolve().parent.parent / ".knowledge_cache.json"


class CrawlerBackend(Enum):
    """Available crawler backends."""
    CRAWL4AI = "crawl4ai"
    REQUESTS_BS4 = "requests_bs4"
    FALLBACK = "fallback"


@dataclasses.dataclass
class Source:
    """Authoritative source configuration."""
    name: str
    url: str
    category: str
    crawler_type: CrawlerBackend = CrawlerBackend.CRAWL4AI
    enabled: bool = True
    rate_limit_delay: float = 1.0  # Seconds between requests


@dataclasses.dataclass
class KnowledgeEntry:
    """Single knowledge entry from crawling."""
    title: str
    content: str
    source: str
    url: str
    date: str
    category: str
    relevance_score: float
    keywords: List[str] = field(default_factory=list)

    def to_hash(self) -> str:
        """Generate content hash for deduplication."""
        content = f"{self.url}{self.title}{self.content[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_markdown(self) -> str:
        """Convert to markdown format for SECOND-KNOWLEDGE-BRAIN.md."""
        keywords_str = ", ".join(self.keywords[:5])
        return (
            f"- [{self.date}] **{self.title}** — {self.source}\n"
            f"  - Category: {self.category} | Relevance: {self.relevance_score:.1f}\n"
            f"  - Keywords: {keywords_str}\n"
            f"  - URL: {self.url}\n"
            f"  - <!--h:{self.to_hash()}-->\n"
        )


class CrawlerFactory:
    """Factory for creating crawler instances."""

    @staticmethod
    def create(backend: CrawlerBackend) -> Callable[[str], str]:
        """Create a crawler function for the given backend."""
        if backend == CrawlerBackend.CRAWL4AI:
            return CrawlerFactory._create_crawl4ai()
        elif backend == CrawlerBackend.REQUESTS_BS4:
            return CrawlerFactory._create_requests_bs4()
        else:
            return CrawlerFactory._create_fallback()

    @staticmethod
    def _create_crawl4ai() -> Callable[[str], str]:
        """Create crawl4ai-based crawler."""
        try:
            from crawl4ai import WebCrawler
            crawler = WebCrawler()
            crawler.warmup()

            def fetch(url: str) -> str:
                try:
                    result = crawler.run(url=url)
                    return getattr(result, "markdown", "") or getattr(result, "cleaned_html", "")
                except Exception as e:
                    logger.warning(f"Crawl4AI error for {url}: {e}")
                    return ""

            return fetch
        except ImportError:
            logger.warning("crawl4ai not available, falling back to requests+BeautifulSoup")
            return CrawlerFactory._create_requests_bs4()

    @staticmethod
    def _create_requests_bs4() -> Callable[[str], str]:
        """Create requests+BeautifulSoup-based crawler."""
        try:
            import requests
            from bs4 import BeautifulSoup

            def fetch(url: str) -> str:
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (compatible; KnowledgeUpdater/1.0)"
                    }
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    return soup.get_text(separator="\n", strip=True)
                except Exception as e:
                    logger.warning(f"Requests+BS4 error for {url}: {e}")
                    return ""

            return fetch
        except ImportError:
            logger.warning("requests/BeautifulSoup not available, using fallback")
            return CrawlerFactory._create_fallback()

    @staticmethod
    def _create_fallback() -> Callable[[str], str]:
        """Create fallback crawler (returns empty string)."""

        def fetch(url: str) -> str:
            logger.warning(f"No crawler available, skipping {url}")
            return ""

        return fetch


class EntryExtractor:
    """Extract knowledge entries from crawled content."""

    # Resume and career-related keywords for relevance scoring
    DOMAIN_KEYWORDS = [
        "resume", "cv", "curriculum vitae", "ats", "applicant tracking",
        "recruit", "hiring", "talent acquisition", "job search",
        "skill", "competency", "qualification", "experience",
        "career", "employment", "labor market", "workforce",
        "onboarding", "performance", "retention", "compensation",
        "keyword", "parsing", "screening", "selection", "assessment",
        "bias", "fairness", "diversity", "inclusion", "equity",
        "linkedin", "indeed", "glassdoor", "monster", "careerbuilder"
    ]

    # Patterns for identifying relevant content
    TITLE_PATTERNS = [
        r"(?P<title>^(?!#{1,3}\s).{20,150}$)",  # Potential titles (20-150 chars)
        r"(?P<title>^#{1,3}\s+.+$)",  # Markdown headers
    ]

    def __init__(self):
        self.title_regexes = [re.compile(p, re.MULTILINE) for p in self.TITLE_PATTERNS]

    def extract(
        self,
        content: str,
        source: Source,
        url: str
    ) -> List[KnowledgeEntry]:
        """Extract knowledge entries from crawled content."""
        if not content or len(content.strip()) < 50:
            return []

        entries: List[KnowledgeEntry] = []
        lines = content.splitlines()
        current_content: List[str] = []
        current_title = ""
        current_depth = 0

        for line in lines:
            stripped = line.strip()

            # Check if this is a heading
            if line.startswith("#"):
                # Save previous entry if we have one
                if current_title and current_content:
                    entry = self._create_entry(
                        current_title,
                        "\n".join(current_content),
                        source,
                        url
                    )
                    if entry:
                        entries.append(entry)

                # Start new entry
                current_title = stripped.lstrip("#").strip()
                current_content = []
                current_depth = len(line) - len(line.lstrip("#"))

            # Check if this is a potential title
            elif self._is_title(stripped):
                # Save previous entry
                if current_title and current_content:
                    entry = self._create_entry(
                        current_title,
                        "\n".join(current_content),
                        source,
                        url
                    )
                    if entry:
                        entries.append(entry)

                current_title = stripped
                current_content = []

            # Otherwise, accumulate content
            elif stripped:
                current_content.append(stripped)

        # Don't forget the last entry
        if current_title and current_content:
            entry = self._create_entry(
                current_title,
                "\n".join(current_content),
                source,
                url
            )
            if entry:
                entries.append(entry)

        return entries

    def _is_title(self, line: str) -> bool:
        """Check if line looks like a title."""
        # Must be reasonable length and mostly uppercase words
        if not (20 <= len(line) <= 150):
            return False

        # Check for title-like capitalization
        words = line.split()
        if len(words) < 3:
            return False

        # At least 50% of words should start with uppercase
        uppercase_count = sum(1 for w in words if w[0].isupper())
        return uppercase_count / len(words) >= 0.5

    def _create_entry(
        self,
        title: str,
        content: str,
        source: Source,
        url: str
    ) -> Optional[KnowledgeEntry]:
        """Create a knowledge entry if it meets relevance criteria."""
        if not title or not content:
            return None

        # Calculate relevance score
        relevance = self._calculate_relevance(title + " " + content)

        # Filter out low-relevance entries
        if relevance < 2:
            return None

        # Extract keywords
        keywords = self._extract_keywords(title + " " + content)

        # Get category from source
        category = source.category

        return KnowledgeEntry(
            title=title,
            content=content[:500],  # Limit content length
            source=source.name,
            url=url,
            date=dt.date.today().isoformat(),
            category=category,
            relevance_score=relevance,
            keywords=keywords
        )

    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance score based on domain keywords."""
        text_lower = text.lower()
        score = 0.0

        for keyword in self.DOMAIN_KEYWORDS:
            count = text_lower.count(keyword.lower())
            score += count

        return score

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Simple keyword extraction using frequency
        words = re.findall(r"\b[A-Za-z]{3,}\b", text.lower())

        # Filter out common words
        stop_words = {
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "her",
            "was", "one", "our", "out", "has", "have", "been", "will", "with",
            "this", "that", "from", "they", "would", "there", "their", "what"
        }

        filtered = [w for w in words if w not in stop_words and len(w) > 3]

        # Count and return top keywords
        from collections import Counter
        counter = Counter(filtered)

        # Return keywords that appear at least twice and are domain-relevant
        relevant = [
            word for word, count in counter.items()
            if count >= 2 and any(kw in word for kw in self.DOMAIN_KEYWORDS[:10])
        ]

        return relevant[:10]


class KnowledgeUpdater:
    """Main knowledge update orchestrator."""

    # Default sources
    DEFAULT_SOURCES = [
        Source(
            name="ArXiv cs.IR",
            url="https://arxiv.org/list/cs.IR/recent",
            category="Academic Research",
            crawler_type=CrawlerBackend.REQUESTS_BS4
        ),
        Source(
            name="ArXiv cs.CL",
            url="https://arxiv.org/list/cs.CL/recent",
            category="Academic Research",
            crawler_type=CrawlerBackend.REQUESTS_BS4
        ),
        Source(
            name="O*NET",
            url="https://www.onetonline.org/",
            category="Government Data",
            crawler_type=CrawlerBackend.REQUESTS_BS4
        ),
        Source(
            name="BLS OOH",
            url="https://www.bls.gov/ooh/",
            category="Government Data",
            crawler_type=CrawlerBackend.REQUESTS_BS4
        ),
        Source(
            name="LinkedIn Economic Graph",
            url="https://economicgraph.linkedin.com/research",
            category="Industry Reports",
            crawler_type=CrawlerBackend.REQUESTS_BS4
        ),
    ]

    def __init__(
        self,
        sources: Optional[List[Source]] = None,
        cache_path: pathlib.Path = CACHE_PATH
    ):
        """Initialize the knowledge updater."""
        self.sources = sources or self.DEFAULT_SOURCES
        self.cache_path = cache_path
        self.extractor = EntryExtractor()
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """Load cached data if available."""
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {"entries": {}, "last_update": None}

    def _save_cache(self) -> None:
        """Save cached data."""
        try:
            self.cache_path.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_existing_hashes(self, brain_path: pathlib.Path) -> set[str]:
        """Extract existing content hashes from brain file."""
        if not brain_path.exists():
            return set()

        content = brain_path.read_text(encoding="utf-8")
        hashes = re.findall(r"<!--h:([0-9a-f]{16})-->", content)
        return set(hashes)

    def update(
        self,
        brain_path: pathlib.Path = BRAIN_PATH,
        dry_run: bool = False,
        limit: Optional[int] = None
    ) -> int:
        """Run knowledge update process.

        Args:
            brain_path: Path to SECOND-KNOWLEDGE-BRAIN.md
            dry_run: If True, print results without writing
            limit: Maximum number of entries to process

        Returns:
            Number of new entries added (or would be added in dry-run mode)
        """
        logger.info("Starting knowledge update process")
        all_entries: List[KnowledgeEntry] = []

        # Get existing hashes for deduplication
        existing_hashes = self._get_existing_hashes(brain_path)
        logger.info(f"Found {len(existing_hashes)} existing entries")

        # Process each source
        for i, source in enumerate(self.sources, 1):
            if not source.enabled:
                logger.info(f"Skipping disabled source: {source.name}")
                continue

            logger.info(f"Processing source {i}/{len(self.sources)}: {source.name}")

            # Create crawler for this source
            crawler = CrawlerFactory.create(source.crawler_type)

            # Fetch content
            try:
                logger.info(f"Fetching {source.url}")
                content = crawler(source.url)

                if not content:
                    logger.warning(f"No content retrieved from {source.url}")
                    continue

                # Extract entries
                entries = self.extractor.extract(content, source, source.url)
                logger.info(f"Extracted {len(entries)} potential entries from {source.name}")
                all_entries.extend(entries)

                # Rate limiting
                time.sleep(source.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error processing {source.name}: {e}")
                continue

        # Sort by relevance score
        all_entries.sort(key=lambda e: e.relevance_score, reverse=True)

        # Filter out duplicates
        new_entries: List[KnowledgeEntry] = []
        for entry in all_entries:
            entry_hash = entry.to_hash()
            if entry_hash not in existing_hashes:
                new_entries.append(entry)
                existing_hashes.add(entry_hash)

                if limit and len(new_entries) >= limit:
                    break

        logger.info(f"Found {len(new_entries)} new entries after deduplication")

        if not new_entries:
            logger.info("No new entries to add")
            return 0

        # Generate markdown block
        today = dt.date.today().isoformat()
        markdown_lines = [
            f"\n### Auto-update {today}",
            f"Source: CV/Resume Optimizer Knowledge Updater",
            f"Entries: {len(new_entries)} new items",
            ""
        ]

        for entry in new_entries:
            markdown_lines.append(entry.to_markdown())

        markdown_block = "\n".join(markdown_lines)

        if dry_run:
            print("\n" + "=" * 80)
            print("DRY RUN - Results that would be added:")
            print("=" * 80)
            print(markdown_block)
            print("=" * 80)
            print(f"Total new entries: {len(new_entries)}")
            return len(new_entries)

        # Write to brain file
        try:
            with brain_path.open("a", encoding="utf-8") as f:
                f.write(markdown_block)
            logger.info(f"Successfully appended {len(new_entries)} entries to {brain_path}")

            # Update cache
            self.cache["last_update"] = dt.datetime.now().isoformat()
            for entry in new_entries:
                entry_hash = entry.to_hash()
                self.cache["entries"][entry_hash] = {
                    "title": entry.title,
                    "source": entry.source,
                    "date": entry.date
                }
            self._save_cache()

            return len(new_entries)

        except Exception as e:
            logger.error(f"Failed to write to brain file: {e}")
            return 0


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Update SECOND-KNOWLEDGE-BRAIN.md with latest research"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show results without writing to file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of entries to add"
    )
    parser.add_argument(
        "--sources",
        help="Comma-separated list of source names to process (default: all)"
    )
    parser.add_argument(
        "--brain",
        type=pathlib.Path,
        default=BRAIN_PATH,
        help="Path to SECOND-KNOWLEDGE-BRAIN.md"
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available sources and exit"
    )

    args = parser.parse_args()

    # Initialize updater
    sources = KnowledgeUpdater.DEFAULT_SOURCES

    if args.sources:
        source_names = [s.strip().lower() for s in args.sources.split(",")]
        sources = [s for s in sources if s.name.lower() in source_names]

    updater = KnowledgeUpdater(sources=sources)

    if args.list_sources:
        print("Available sources:")
        for source in updater.sources:
            status = "enabled" if source.enabled else "disabled"
            print(f"  - [{status}] {source.name}: {source.url} ({source.category})")
        return 0

    # Run update
    new_count = updater.update(
        brain_path=args.brain,
        dry_run=args.dry_run,
        limit=args.limit
    )

    if new_count > 0 and not args.dry_run:
        print(f"✓ Added {new_count} new entries")
        return 0
    elif new_count == 0:
        print("No new entries to add")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
