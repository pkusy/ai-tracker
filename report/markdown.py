"""Markdown report generator."""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


def generate_daily_report(
    trending: List[Dict[str, Any]],
    search_results: List[Dict[str, Any]],
    watchlist: List[Dict[str, Any]],
    report_date: Optional[date] = None,
) -> str:
    """Generate daily report in Markdown format.
    
    Args:
        trending: Trending projects.
        search_results: Search results.
        watchlist: Watchlist updates.
        report_date: Report date. Defaults to today.
    
    Returns:
        Markdown formatted report.
    """
    if report_date is None:
        report_date = date.today()
    
    lines = [
        f"# AI 前沿追踪 - {report_date}",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## 概览",
        "",
        f"- Trending 项目: {len(trending)}",
        f"- 搜索结果: {len(search_results)}",
        f"- Watchlist 更新: {len(watchlist)}",
        "",
        "---",
        "",
    ]
    
    # Trending section
    if trending:
        lines.extend([
            "## 🔥 Trending 项目",
            "",
            "| 项目 | 描述 | Stars | Language |",
            "|------|------|-------|----------|",
        ])
        
        for repo in trending[:15]:
            name = repo.get("name", "")
            desc = repo.get("description", "")[:60] + "..." if len(repo.get("description", "")) > 60 else repo.get("description", "")
            stars = repo.get("stars", 0)
            lang = repo.get("language", "-")
            
            lines.append(f"| [{name}](https://github.com/{repo.get('full_name', '')}) | {desc} | {stars:,} | {lang} |")
        
        lines.append("")
    
    # Search results section
    if search_results:
        lines.extend([
            "## 🔍 搜索发现 (AI关键词)",
            "",
            "| 项目 | 关键词 | Stars |",
            "|------|--------|-------|",
        ])
        
        for repo in search_results[:15]:
            name = repo.get("name", "")
            keyword = repo.get("source_keyword", "")
            stars = repo.get("stars", 0)
            
            lines.append(f"| [{name}](https://github.com/{repo.get('full_name', '')}) | {keyword} | {stars:,} |")
        
        lines.append("")
    
    # Watchlist section
    if watchlist:
        lines.extend([
            "## ⭐ Watchlist 更新",
            "",
            "| 项目 | Stars | 今日增长 | 最近更新 |",
            "|------|-------|----------|----------|",
        ])
        
        for repo in watchlist:
            name = repo.get("name", "")
            stars = repo.get("stars", 0)
            delta = repo.get("stars_delta", 0)
            updated = repo.get("last_updated", "")[:10] if repo.get("last_updated") else "-"
            
            delta_str = f"+{delta}" if delta > 0 else str(delta)
            lines.append(f"| [{name}](https://github.com/{repo.get('full_name', '')}) | {stars:,} | {delta_str} | {updated} |")
        
        lines.append("")
    
    # Hot projects section - combine all and get top
    all_projects = trending + search_results + watchlist
    if all_projects:
        lines.extend([
            "## 🏆 Top 热门项目",
            "",
            "| Rank | 项目 | Stars | 来源 |",
            "|------|------|-------|------|",
        ])
        
        # Sort by stars and get top 10
        sorted_projects = sorted(
            all_projects,
            key=lambda x: x.get("stars", 0),
            reverse=True
        )[:10]
        
        for i, repo in enumerate(sorted_projects, 1):
            name = repo.get("name", "")
            stars = repo.get("stars", 0)
            source = repo.get("source", "unknown")
            
            source_emoji = {
                "trending": "🔥",
                "search": "🔍",
                "watchlist": "⭐",
            }.get(source, "•")
            
            lines.append(f"| {i} | [{name}](https://github.com/{repo.get('full_name', '')}) | {stars:,} | {source_emoji} |")
        
        lines.append("")
    
    # Footer
    lines.extend([
        "---",
        "",
        f"*由 AI Tracker 自动生成 - {report_date}*",
    ])
    
    return "\n".join(lines)


def generate_summary(
    trending: List[Dict[str, Any]],
    search_results: List[Dict[str, Any]],
    watchlist: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate summary statistics.
    
    Args:
        trending: Trending projects.
        search_results: Search results.
        watchlist: Watchlist updates.
    
    Returns:
        Summary dictionary.
    """
    all_projects = trending + search_results + watchlist
    
    total_stars = sum(p.get("stars", 0) for p in all_projects)
    total_forks = sum(p.get("forks", 0) for p in all_projects)
    
    languages: Dict[str, int] = {}
    for p in all_projects:
        lang = p.get("language", "Unknown")
        languages[lang] = languages.get(lang, 0) + 1
    
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_projects": len(all_projects),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "trending_count": len(trending),
        "search_count": len(search_results),
        "watchlist_count": len(watchlist),
        "top_languages": top_languages,
    }
