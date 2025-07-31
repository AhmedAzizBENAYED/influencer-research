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
    """Save markdown report with enhanced error handling and path resolution."""
    try:
        if out_path is None:
            # If no path is provided, use the default settings.OUTPUT_DIR and filename
            os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
            final_file_path = os.path.join(settings.OUTPUT_DIR, "influencer_report.md")
        elif os.path.isdir(out_path):
            # If out_path is an existing directory, join the default filename to it
            os.makedirs(out_path, exist_ok=True)
            final_file_path = os.path.join(out_path, "influencer_report.md")
        else:
            # If out_path is a specific file path, use it directly
            # Ensure its parent directory exists
            parent_dir = os.path.dirname(out_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            final_file_path = out_path

        # Validate that we can write to the target location
        test_path = os.path.dirname(final_file_path) if os.path.dirname(final_file_path) else "."
        if not os.access(test_path, os.W_OK):
            raise PermissionError(f"Cannot write to directory: {test_path}")

        # Write the file with proper encoding
        with open(final_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content.strip() + "\n")

        # Verify the file was actually created
        if not os.path.exists(final_file_path):
            raise IOError(f"File was not created successfully: {final_file_path}")

        absolute_path = os.path.abspath(final_file_path)
        print(f"✅ Report successfully saved to: {absolute_path}")
        return absolute_path
        
    except Exception as e:
        # Enhanced error handling with fallback options
        print(f"❌ Error saving to {final_file_path if 'final_file_path' in locals() else 'unknown path'}: {e}")
        
        # Try fallback to current directory
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_filename = f"influencer_report_fallback_{timestamp}.md"
            
            with open(fallback_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content.strip() + "\n")
            
            fallback_path = os.path.abspath(fallback_filename)
            print(f"💾 Fallback: Report saved to current directory: {fallback_path}")
            return fallback_path
            
        except Exception as e2:
            print(f"❌ Critical: Could not save report anywhere: {e2}")
            # Return a descriptive error message instead of raising
            return f"ERROR: Could not save report - {str(e)} | Fallback failed - {str(e2)}"


# Initialize tools with enhanced configuration
def get_research_tools():
    """Get all research tools with enhanced settings."""
    novada_google_search_tool = StructuredTool.from_function(
        novada_google_search,
        name="novada_google_search",
        description="Enhanced Google search via NovaDA API. Use for broad influencer discovery, industry reports, and trending topics. Returns structured JSON with organic results.",
    )
    
    # Enhanced Tavily search with more results
    try:
        tavily_search = TavilySearchResults(
            max_results=8,  # Increased from 4
            search_depth="advanced",  # More thorough search
            include_answer=True,
            include_raw_content=True
        )
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize Tavily search: {e}")
        # Create a fallback version
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily_search = TavilySearchResults(max_results=5)
    
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