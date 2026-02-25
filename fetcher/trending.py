"""GitHub Trending fetcher."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

TRENDING_URL = "https://github.com/trending"


def fetch_trending(
    language: Optional[str] = None,
    since: str = "daily",
) -> List[Dict[str, Any]]:
    """Fetch trending repositories from GitHub.
    
    Args:
        language: Programming language to filter by.
        since: Time range (daily, weekly, monthly).
    
    Returns:
        List of trending repository data.
    """
    params = {"since": since}
    if language:
        params["spoken_language_code"] = ""
    
    url = f"{TRENDING_URL}/{language}" if language else TRENDING_URL
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return _parse_trending_page(response.text)
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch trending: {e}")
        return []


def _parse_trending_page(html: str) -> List[Dict[str, Any]]:
    """Parse GitHub trending page HTML.
    
    Args:
        html: HTML content of trending page.
    
    Returns:
        List of repository data.
    """
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    
    for article in soup.select("article.box-row"):
        try:
            # Extract repo link
            link = article.select_one("h2 a")
            if not link:
                continue
            
            full_name = link.get("href", "").lstrip("/")
            
            # Description
            description_elem = article.select_one("p")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Language
            lang_elem = article.select_one("[itemprop=programmingLanguage]")
            language = lang_elem.get_text(strip=True) if lang_elem else None
            
            # Stars (approximate from trending)
            stars_elem = article.select_one('a[href*="stargazers"]')
            stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
            stars = _parse_star_count(stars_text)
            
            repos.append({
                "full_name": full_name,
                "name": full_name.split("/")[-1] if "/" in full_name else full_name,
                "description": description,
                "stars": stars,
                "stars_delta": stars,  # Trending stars are new
                "language": language,
                "topics": [],
                "source": "trending",
                "fetched_at": datetime.now().isoformat(),
            })
        
        except Exception as e:
            logger.warning(f"Failed to parse trending repo: {e}")
            continue
    
    return repos


def _parse_star_count(text: str) -> int:
    """Parse star count from text.
    
    Args:
        text: Text like "1,234 stars" or "1.2k".
    
    Returns:
        Integer star count.
    """
    text = text.lower().replace(",", "").replace(" ", "").replace("stars", "").replace("k", "000")
    try:
        return int(float(text))
    except ValueError:
        return 0


def fetch_ai_trending() -> List[Dict[str, Any]]:
    """Fetch trending AI-related repositories.
    
    Returns:
        List of trending AI project data.
    """
    all_trending = []
    
    for lang in config.TRENDING_LANGUAGES:
        trending = fetch_trending(language=lang)
        
        # Filter for AI-related
        ai_trending = _filter_ai_projects(trending)
        all_trending.extend(ai_trending)
        logger.info(f"Found {len(ai_trending)} AI projects in {lang} trending")
    
    return all_trending


def _filter_ai_projects(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter repositories for AI-related projects.
    
    Args:
        repos: List of repository data.
    
    Returns:
        Filtered list of AI projects.
    """
    ai_keywords = [kw.lower() for kw in config.AI_KEYWORDS]
    
    filtered = []
    for repo in repos:
        # Check description and name
        text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
        
        if any(kw in text for kw in ai_keywords):
            filtered.append(repo)
    
    return filtered
