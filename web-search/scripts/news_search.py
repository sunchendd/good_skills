#!/usr/bin/env python3
"""
Brave News Search API client
"""
import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError


def search_news(query, count=10, api_key=None):
    """
    Search news using Brave Search API
    
    Args:
        query: Search query string
        count: Number of results to return (default: 10, max: 20)
        api_key: Brave Search API key
    
    Returns:
        dict: News search results
    """
    if not api_key:
        api_key = os.environ.get('BRAVE_API_KEY')
    
    if not api_key:
        raise ValueError("API key required. Set BRAVE_API_KEY environment variable or pass via --api-key")
    
    base_url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        'q': query,
        'count': min(count, 20),
        'search_lang': 'en',
        'result_filter': 'news'
    }
    
    url = f"{base_url}?{urlencode(params)}"
    
    headers = {
        'Accept': 'application/json',
        'X-Subscription-Token': api_key
    }
    
    try:
        request = Request(url, headers=headers)
        with urlopen(request) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP Error {e.code}: {error_body}")
    except URLError as e:
        raise Exception(f"URL Error: {e.reason}")


def main():
    parser = argparse.ArgumentParser(description='Search news using Brave Search API')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--count', type=int, default=10, help='Number of results (default: 10, max: 20)')
    parser.add_argument('--api-key', help='Brave Search API key (or set BRAVE_API_KEY env var)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    args = parser.parse_args()
    
    try:
        results = search_news(args.query, args.count, args.api_key)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Format results for readability
            print(f"News results for: {args.query}\n")
            
            if 'news' in results and 'results' in results['news']:
                for i, result in enumerate(results['news']['results'], 1):
                    print(f"{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('url', 'No URL')}")
                    if 'description' in result:
                        print(f"   {result['description']}")
                    if 'age' in result:
                        print(f"   Published: {result['age']}")
                    print()
            else:
                print("No news results found")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
