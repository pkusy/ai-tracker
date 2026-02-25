"""GitHub Search API fetcher."""

import logging
from datetime import datetime
from typing import Any

import config
from fetcher.github_client import GitHubClient

logger = logging.getLogger(__name__)


def search_ai_projects(
    client: GitHubClient,
    per_keyword: int = 10,
) -> list[dict[str, Any]]:
    """Search for AI-related projects using GitHub Search API.
    
    Args:
        client: GitHubClient instance.
        per_keyword: Number of results per keyword.
    
    Returns:
        List of AI project data.
    """
    all_results = []
    seen = set()
    
    for keyword in config.AI_KEYWORDS:
        query = f"{keyword} language:python OR language:typescript"
        
        try:
            results = client.search_repositories(
                query=query,
                sort="stars",
                order="desc",
                per_page=per_keyword,
            )
            
            for repo in results:
                full_name = repo.get("full_name", "")
                
                # Skip duplicates
                if full_name in seen:
                    continue
                
                seen.add(full_name)
                repo["source"] = "search"
                repo["source_keyword"] = keyword
                repo["fetched_at"] = datetime.now().isoformat()
                
                all_results.append(repo)
            
            logger.info(f"Search '{keyword}': {len(results)} results")
        
        except Exception as e:
            logger.error(f"Search error for '{keyword}': {e}")
            continue
    
    # Sort by stars
    all_results.sort(key=lambda x: x.get("stars", 0), reverse=True)
    
    return all_results


def search_new_projects(
    client: GitHubClient,
    days: int = 7,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """Search for newly created AI projects.
    
    Args:
        client: GitHubClient instance.
        days: Look for projects created in last N days.
        per_page: Number of results.
    
    Returns:
        List of newly created project data.
    """
    from datetime import timedelta
    
    created_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    query = f"created:>{created_date} "
    query += " OR ".join(config.AI_KEYWORDS[:5])  # Use top 5 keywords
    
    try:
        results = client.search_repositories(
            query=query,
            sort="stars",
            order="desc",
            per_page=per_page,
        )
        
        for repo in results:
            repo["source"] = "new"
            repo["fetched_at"] = datetime.now().isoformat()
        
        return results
    
    except Exception as e:
        logger.error(f"New projects search error: {e}")
        return []
