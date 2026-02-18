#!/usr/bin/env python3
"""
Brave Web Search API client
"""
import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError


def search_web(query, count=10, api_key=None):
    """
    Search the web using Brave Search API
    
    Args:
        query: Search query string
        count: Number of results to return (default: 10, max: 20)
        api_key: Brave Search API key
    
    Returns:
        dict: Search results
    """
    if not api_key:
        api_key = os.environ.get('BRAVE_API_KEY')
    
    if not api_key:
        raise ValueError("API key required. Set BRAVE_API_KEY environment variable or pass via --api-key")
    
    base_url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        'q': query,
        'count': min(count, 20)  # API max is 20
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
    parser = argparse.ArgumentParser(description='Search the web using Brave Search API')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--count', type=int, default=10, help='Number of results (default: 10, max: 20)')
    parser.add_argument('--api-key', help='Brave Search API key (or set BRAVE_API_KEY env var)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    args = parser.parse_args()
    
    try:
        results = search_web(args.query, args.count, args.api_key)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Format results for readability
            print(f"Search results for: {args.query}\n")
            
            if 'web' in results and 'results' in results['web']:
                for i, result in enumerate(results['web']['results'], 1):
                    print(f"{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('url', 'No URL')}")
                    if 'description' in result:
                        print(f"   {result['description']}")
                    print()
            else:
                print("No results found")
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
