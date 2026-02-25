"""AI Tracker - Main entry point."""

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fetcher.github_client import GitHubClient
from fetcher import trending, search, watchlist
from storage import json_store
from report import markdown


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.
    
    Args:
        verbose: Enable verbose output.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def run_tracker(report_date: Optional[date] = None) -> None:
    """Run the AI tracker.
    
    Args:
        report_date: Date to generate report for. Defaults to today.
    """
    if report_date is None:
        report_date = date.today()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting AI Tracker for {report_date}")
    
    # Ensure directories exist
    json_store.ensure_directories()
    
    # Initialize GitHub client
    client = GitHubClient()
    
    # Check rate limit
    rate_status = client.get_rate_limit_status()
    logger.info(f"Rate limit: {rate_status['remaining']}/{rate_status['limit']}")
    
    if rate_status["remaining"] < 10:
        logger.warning("Low rate limit, some requests may fail")
    
    # Fetch from all sources
    logger.info("Fetching trending projects...")
    trending_projects = trending.fetch_ai_trending()
    logger.info(f"Found {len(trending_projects)} trending projects")
    
    logger.info("Searching for AI projects...")
    search_projects = search.search_ai_projects(client, per_keyword=10)
    logger.info(f"Found {len(search_projects)} search results")
    
    logger.info("Fetching watchlist...")
    watchlist_projects = watchlist.fetch_watchlist(client)
    logger.info(f"Found {len(watchlist_projects)} watchlist projects")
    
    # Generate and save report
    logger.info("Generating report...")
    report_content = markdown.generate_daily_report(
        trending=trending_projects,
        search_results=search_projects,
        watchlist=watchlist_projects,
        report_date=report_date,
    )
    
    report_path = json_store.save_daily_report(report_content, report_date)
    logger.info(f"Report saved to {report_path}")
    
    # Save projects data
    all_projects = trending_projects + search_projects + watchlist_projects
    for repo in all_projects:
        full_name = repo.get("full_name", "")
        if full_name:
            json_store.update_project(full_name, repo)
    
    logger.info("Projects data saved")
    
    # Print summary
    summary = markdown.generate_summary(
        trending_projects,
        search_projects,
        watchlist_projects,
    )
    logger.info(f"Summary: {summary['total_projects']} projects, {summary['total_stars']:,} total stars")
    
    print(f"\n✅ Report generated: {report_path}")
    print(f"   - {summary['trending_count']} trending projects")
    print(f"   - {summary['search_count']} search results")
    print(f"   - {summary['watchlist_count']} watchlist updates")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Tracker - GitHub AI Project Monitor")
    parser.add_argument(
        "--date",
        type=str,
        help="Report date (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.date:
        try:
            report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid date format: {args.date}")
            sys.exit(1)
    else:
        report_date = date.today()
    
    try:
        run_tracker(report_date)
    except Exception as e:
        logging.error(f"Tracker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
