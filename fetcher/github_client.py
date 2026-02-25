"""GitHub API client with authentication and error handling."""

import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests
from github import Github
from github.GithubException import RateLimitExceededException, GithubException

import config

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client with rate limiting and caching."""
    
    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize GitHub client.
        
        Args:
            token: GitHub Personal Access Token. Uses config.GITHUB_TOKEN if not provided.
        """
        self.token = token or config.GITHUB_TOKEN
        self._client = Github(self.token) if self.token else Github()
        self._session = requests.Session()
        
        if self.token:
            self._session.headers["Authorization"] = f"token {self.token}"
        
        self._cache: Dict[Tuple[str, str], Tuple[datetime, Any]] = {}
        self._cache_ttl = timedelta(seconds=config.CACHE_TTL_SECONDS)
    
    def _get_cached(self, key: Tuple[str, str]) -> Optional[Any]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key (endpoint, params).
        
        Returns:
            Cached value or None if expired/missing.
        """
        if key in self._cache:
            cached_time, value = self._cache[key]
            if datetime.now() - cached_time < self._cache_ttl:
                return value
            del self._cache[key]
        return None
    
    def _set_cached(self, key: Tuple[str, str], value: Any) -> None:
        """Set cache value with current timestamp.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        self._cache[key] = (datetime.now(), value)
    
    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search repositories by query.
        
        Args:
            query: Search query string.
            sort: Sort field (stars, forks, updated).
            order: Sort order (asc, desc).
            per_page: Results per page.
        
        Returns:
            List of repository dictionaries.
        """
        cache_key = ("search", f"{query}-{sort}-{order}-{per_page}")
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            results = self._client.search_repositories(
                query=query,
                sort=sort,
                order=order,
            )
            repos = []
            for repo in results[:per_page]:
                repos.append(self._extract_repo_data(repo))
            
            self._set_cached(cache_key, repos)
            return repos
        
        except RateLimitExceededException as e:
            logger.warning(f"Rate limit exceeded: {e}")
            self._handle_rate_limit(e)
            return []
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return []
    
    def get_repository(self, full_name: str) -> Optional[Dict[str, Any]]:
        """Get repository details.
        
        Args:
            full_name: Repository full name (owner/repo).
        
        Returns:
            Repository data dictionary or None if not found.
        """
        cache_key = ("repo", full_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            repo = self._client.get_repo(full_name)
            data = self._extract_repo_data(repo)
            self._set_cached(cache_key, data)
            return data
        
        except RateLimitExceededException:
            logger.warning("Rate limit exceeded")
            return None
        
        except GithubException:
            logger.error(f"Repository not found: {full_name}")
            return None
    
    def get_recent_commits(self, full_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent commits for a repository.
        
        Args:
            full_name: Repository full name.
            limit: Number of commits to retrieve.
        
        Returns:
            List of commit dictionaries.
        """
        try:
            repo = self._client.get_repo(full_name)
            commits = repo.get_commits()[:limit]
            return [
                {
                    "sha": c.sha,
                    "message": c.commit.message.split("\n")[0],
                    "author": c.commit.author.name if c.commit.author else "Unknown",
                    "date": c.commit.author.date.isoformat() if c.commit.author else None,
                }
                for c in commits  # type: ignore[misc]
            ]
        except GithubException as e:
            logger.error(f"Error fetching commits: {e}")
            return []
    
    def get_contributors(self, full_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top contributors for a repository.
        
        Args:
            full_name: Repository full name.
            limit: Number of contributors to retrieve.
        
        Returns:
            List of contributor dictionaries.
        """
        try:
            repo = self._client.get_repo(full_name)
            contributors = repo.get_contributors()[:limit]
            return [
                {
                    "login": c.login,
                    "contributions": c.contributions,
                    "avatar_url": c.avatar_url,
                }
                for c in contributors  # type: ignore[misc]
            ]
        except GithubException as e:
            logger.error(f"Error fetching contributors: {e}")
            return []
    
    def _extract_repo_data(self, repo: Any) -> Dict[str, Any]:
        """Extract relevant data from a repository object.
        
        Args:
            repo: PyGithub Repository object.
        
        Returns:
            Dictionary with extracted data.
        """
        return {
            "full_name": repo.full_name,
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "topics": list(repo.get_topics()) if repo.language else [],
            "last_updated": repo.updated_at.isoformat() if repo.updated_at else None,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "html_url": repo.html_url,
            "license": repo.license.name if repo.license else None,
        }
    
    def _handle_rate_limit(self, exception: RateLimitExceededException) -> None:
        """Handle rate limit exception.
        
        Args:
            exception: The rate limit exception.
        """
        # Wait and retry once
        logger.info("Waiting 60 seconds before retrying...")
        time.sleep(60)
    
    def get_rate_limit_status(self) -> Dict[str, int]:
        """Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information.
        """
        if not self.token:
            return {"remaining": 60, "limit": 60, "reset": 0}
        
        rates = self._client.get_rate_limit()
        core = rates.resources.core
        return {
            "remaining": core.remaining,
            "limit": core.limit,
            "reset": core.reset,
        }
