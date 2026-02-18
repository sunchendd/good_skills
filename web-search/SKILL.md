---
name: brave-search
description: Perform web, news, and image searches using Brave Search API. Use when the user asks to search the web, look up current information, find news articles, search for images, or phrases like "search for", "look up", "find information about", "检索", "搜索". Returns raw search results including titles, URLs, and descriptions.
---

# Brave Search

Perform web searches, news searches, and image searches using Brave Search API.

## Quick Start

Set the API key as an environment variable before running searches:

```bash
export BRAVE_API_KEY='YOUR_API_KEY'
```

## Web Search

Use `scripts/web_search.py` for general web searches:

```bash
# Basic search
python3 scripts/web_search.py "search query"

# Specify number of results (max 20)
python3 scripts/web_search.py "search query" --count 10

# Get raw JSON output
python3 scripts/web_search.py "search query" --json

# Pass API key directly
python3 scripts/web_search.py "search query" --api-key YOUR_KEY
```

The script outputs formatted results with titles, URLs, and descriptions.

## News Search

Use `scripts/news_search.py` for news-specific searches:

```bash
# Search for news articles
python3 scripts/news_search.py "topic" --count 10

# Get raw JSON output
python3 scripts/news_search.py "topic" --json
```

Returns news articles with publication dates and descriptions.

## Image Search

Use `scripts/image_search.py` for image searches:

```bash
# Search for images
python3 scripts/image_search.py "query" --count 10

# Get raw JSON output
python3 scripts/image_search.py "query" --json
```

Returns image URLs, thumbnails, and source information.

## API Reference

For detailed API documentation including query parameters, response structures, and error codes, see [references/api_reference.md](references/api_reference.md).

## Workflow

1. Identify the search type (web, news, or images) based on user request
2. Export BRAVE_API_KEY if not already set
3. Run the appropriate script with the user's query
4. Return the formatted results to the user
