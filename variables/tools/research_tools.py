"""Research tools for influencer data collection."""

import os
import requests
from typing import Dict
from langchain_core.tools import tool as lc_tool
from langchain.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults

from src.config.settings import settings


def novada_google_search(query: str) -> dict:
    """
    Query Google through NovaDA's scraper API and return the raw JSON payload.
    Enhanced with better error handling and result formatting.
    """
    try:
        params = {
            "engine": "google",
            "q": query,
            "no_cache": False,
            "api_key": settings.NOVADA_API_KEY,
            "num": settings.MAX_SEARCH_RESULTS,  # Get more results
        }
        resp = requests.get("https://scraperapi.novada.com/search", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "results": []}


@lc_tool(
    "linkedin_lookup",
    description=(
        "Fetch basic company metadata from LinkedIn by its email domain. "
        "Returns the raw JSON payload from the RapidAPI linkedin-data-api."
    ),
)
def linkedin_lookup(domain: str) -> dict:
    """
    Query RapidAPI's linkedin-data-api and return company details found
    for the given email/website domain (e.g. 'apple.com').
    """
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com",
    }
    resp = requests.get(
        "https://linkedin-data-api.p.rapidapi.com/get-company-by-domain",
        headers=headers,
        params={"domain": domain},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


@lc_tool(
    "facebook_page_videos",
    description=(
        "search facebook to get details about profiles and pages and posts "
    ),
)
def facebook_page_videos(delegate_page_id: str) -> dict:
    url = "https://facebook-scraper3.p.rapidapi.com/page/videos"
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com",
    }
    resp = requests.get(url, headers=headers, params={"delegate_page_id": delegate_page_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


@lc_tool(
    "twitter_lookup",
    description=(
        "Retrieve a single tweet's JSON payload via the RapidAPI twitter241 endpoint. "
        "Input = tweet ID (pid)."
    ),
)
def twitter_lookup(pid: str) -> dict:
    """
    Example
    -------
    >>> twitter_lookup("1631781099415257088")
    {... full tweet JSON ...}
    """
    url = "https://twitter241.p.rapidapi.com/tweet"
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "twitter241.p.rapidapi.com",
    }
    resp = requests.get(url, headers=headers, params={"pid": pid}, timeout=30)
    resp.raise_for_status()
    return resp.json()


@lc_tool(
    "save_markdown_report",
    description="Write a Markdown string to outputs directory and return its path.",
)
def save_markdown_report(
    markdown_content: str,
    out_path: str | None = None,
) -> str:
    if out_path is None:
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        out_path = f"{settings.OUTPUT_DIR}/influencer_report.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content.strip() + "\n")

    return os.path.abspath(out_path)


# Initialize tools with enhanced configuration
def get_research_tools():
    """Get all research tools with enhanced settings."""
    novada_google_search_tool = StructuredTool.from_function(
        novada_google_search,
        name="novada_google_search",
        description="Enhanced Google search via NovaDA API. Use for broad influencer discovery, industry reports, and trending topics. Returns structured JSON with organic results.",
    )
    
    # Enhanced Tavily search with more results
    tavily_search = TavilySearchResults(
        max_results=8,  # Increased from 4
        search_depth="advanced",  # More thorough search
        include_answer=True,
        include_raw_content=True
    )
    
    return [
        novada_google_search_tool,
        tavily_search,
        linkedin_lookup,
        twitter_lookup,
        facebook_page_videos,
    ]


def get_reporter_tools():
    """Get reporter tools."""
    return [save_markdown_report]