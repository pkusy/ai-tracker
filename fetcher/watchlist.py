"""Watchlist fetcher - monitor known AI projects."""

import logging
from datetime import datetime
from typing import Any

import config
from fetcher.github_client import GitHubClient

logger = logging.getLogger(__name__)


def fetch_watchlist(client: GitHubClient) -> list[dict[str, Any]]:
    """Fetch updates for watchlist projects.
    
    Args:
        client: GitHubClient instance.
    
    Returns:
        List of watchlist project data with updates.
    """
    results = []
    
    for full_name in config.WATCHLIST:
        try:
            repo_data = client.get_repository(full_name)
            
            if repo_data is None:
                logger.warning(f"Could not fetch: {full_name}")
                continue
            
            # Get additional info
            commits = client.get_recent_commits(full_name, limit=5)
            contributors = client.get_contributors(full_name, limit=5)
            
            repo_data.update({
                "source": "watchlist",
                "recent_commits": commits,
                "contributors": contributors,
                "fetched_at": datetime.now().isoformat(),
            })
            
            results.append(repo_data)
            logger.info(f"Watchlist: {full_name} ({repo_data.get('stars', 0)} stars)")
        
        except Exception as e:
            logger.error(f"Watchlist error for {full_name}: {e}")
            continue
    
    return results


def get_watchlist_changes(
    client: GitHubClient,
    previous_data: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Get changes for watchlist projects compared to previous data.
    
    Args:
        client: GitHubClient instance.
        previous_data: Previous snapshot of watchlist data.
    
    Returns:
        List of projects with significant changes.
    """
    current_data = fetch_watchlist(client)
    changes = []
    
    for repo in current_data:
        full_name = repo.get("full_name", "")
        prev = previous_data.get(full_name, {})
        
        # Check for star changes
        current_stars = repo.get("stars", 0)
        prev_stars = prev.get("stars", 0)
        star_delta = current_stars - prev_stars
        
        if star_delta > 0:
            repo["stars_delta"] = star_delta
            changes.append(repo)
    
    # Sort by star delta
    changes.sort(key=lambda x: x.get("stars_delta", 0), reverse=True)
    
    return changes
