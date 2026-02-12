#!/usr/bin/env python3
"""
SerpAPI Search Script
Performs Google searches using the SerpAPI service and returns structured results.
"""

import sys
import json
import os
from typing import Dict, Any, Optional

def search_google(query: str, api_key: str, location: Optional[str] = None, 
                  hl: str = "en", gl: str = "us", num: int = 10) -> Dict[str, Any]:
    """
    Perform a Google search using SerpAPI.
    
    Args:
        query: Search query string
        api_key: SerpAPI API key
        location: Optional location (e.g., "Austin, Texas, United States")
        hl: Language code (default: "en")
        gl: Country code (default: "us")
        num: Number of results (default: 10)
    
    Returns:
        Dictionary containing search results
    """
    try:
        from serpapi import GoogleSearch
    except ImportError:
        print("Error: serpapi package not installed. Run: pip install google-search-results", file=sys.stderr)
        sys.exit(1)
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "hl": hl,
        "gl": gl,
        "num": num
    }
    
    if location:
        params["location"] = location
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    return results


def format_results(results: Dict[str, Any], include_sections: Optional[list] = None) -> str:
    """
    Format search results into readable text.
    
    Args:
        results: Raw SerpAPI results dictionary
        include_sections: List of sections to include (e.g., ['organic_results', 'knowledge_graph'])
                         If None, includes all available sections
    
    Returns:
        Formatted string of results
    """
    output = []
    
    # Search information
    if "search_information" in results:
        info = results["search_information"]
        output.append(f"Search Results for: {results.get('search_parameters', {}).get('q', 'N/A')}")
        output.append(f"Total results: {info.get('total_results', 'N/A'):,}")
        output.append("-" * 80)
        output.append("")
    
    # Knowledge graph
    if (not include_sections or "knowledge_graph" in include_sections) and "knowledge_graph" in results:
        kg = results["knowledge_graph"]
        output.append("=== KNOWLEDGE GRAPH ===")
        output.append(f"Title: {kg.get('title', 'N/A')}")
        output.append(f"Type: {kg.get('type', 'N/A')}")
        if "description" in kg:
            output.append(f"Description: {kg['description']}")
        output.append("")
    
    # Organic results
    if (not include_sections or "organic_results" in include_sections) and "organic_results" in results:
        output.append("=== ORGANIC RESULTS ===")
        for i, result in enumerate(results["organic_results"], 1):
            output.append(f"{i}. {result.get('title', 'N/A')}")
            output.append(f"   URL: {result.get('link', 'N/A')}")
            if "snippet" in result:
                output.append(f"   {result['snippet']}")
            output.append("")
    
    # Local results
    if (not include_sections or "local_results" in include_sections) and "local_results" in results:
        places = results["local_results"].get("places", [])
        if places:
            output.append("=== LOCAL RESULTS ===")
            for place in places:
                output.append(f"• {place.get('title', 'N/A')}")
                output.append(f"  Address: {place.get('address', 'N/A')}")
                output.append(f"  Rating: {place.get('rating', 'N/A')} ({place.get('reviews', 0)} reviews)")
                output.append("")
    
    # Related questions
    if (not include_sections or "related_questions" in include_sections) and "related_questions" in results:
        output.append("=== RELATED QUESTIONS ===")
        for q in results["related_questions"]:
            output.append(f"Q: {q.get('question', 'N/A')}")
            if "snippet" in q:
                output.append(f"A: {q['snippet']}")
            output.append("")
    
    return "\n".join(output)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Search Google using SerpAPI")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--api-key", help="SerpAPI API key (or set SERPAPI_API_KEY env var)")
    parser.add_argument("--location", help="Location for search (e.g., 'Austin, Texas')")
    parser.add_argument("--hl", default="en", help="Language code (default: en)")
    parser.add_argument("--gl", default="us", help="Country code (default: us)")
    parser.add_argument("--num", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--sections", nargs="+", 
                       choices=["organic_results", "knowledge_graph", "local_results", "related_questions"],
                       help="Specific sections to include in formatted output")
    
    args = parser.parse_args()
    
    # Get API key from argument or environment
    api_key = args.api_key or os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        print("Error: API key required. Use --api-key or set SERPAPI_API_KEY environment variable", 
              file=sys.stderr)
        sys.exit(1)
    
    # Perform search
    results = search_google(
        query=args.query,
        api_key=api_key,
        location=args.location,
        hl=args.hl,
        gl=args.gl,
        num=args.num
    )
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results, include_sections=args.sections))


if __name__ == "__main__":
    main()
