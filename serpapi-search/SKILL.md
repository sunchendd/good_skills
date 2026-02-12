---
name: serpapi-search
description: Perform Google searches and retrieve structured search results using SerpAPI. Use when the user needs to search Google for information, get current web results, find local businesses, check knowledge graphs, or retrieve any information requiring live Google search. Triggers include "search Google for", "find information about", "look up", "what are the latest", or any query requiring current web data.
---

# SerpAPI Search

Search Google and retrieve structured, parseable results using the SerpAPI service.

## Quick Start

Use the search script to perform Google searches:

```bash
scripts/search.py "your search query" --api-key YOUR_KEY
```

The API key can also be set via environment variable:

```bash
export SERPAPI_API_KEY="ceac1888ee08e1e41d3ae9a2176c888ad05a85955c8e0580b95b7ae4262a824a"
scripts/search.py "coffee shops near me"
```

## Python Integration

For programmatic access:

```python
from serpapi import GoogleSearch

params = {
    "engine": "google",
    "q": "your search query",
    "api_key": "YOUR_API_KEY",
    "hl": "en",  # Language
    "gl": "us",  # Country
    "num": 10    # Number of results
}

search = GoogleSearch(params)
results = search.get_dict()

# Access different result sections
organic = results.get("organic_results", [])
knowledge_graph = results.get("knowledge_graph", {})
local_places = results.get("local_results", {}).get("places", [])
related_questions = results.get("related_questions", [])
```

## Common Use Cases

### Information Lookup
Search for factual information and get structured results:
```bash
scripts/search.py "Python programming best practices" --json
```

### Local Search
Find businesses and places with location-specific results:
```bash
scripts/search.py "coffee shops" --location "Austin, Texas"
```

### Research Queries
Get comprehensive results including knowledge graphs and related questions:
```bash
scripts/search.py "climate change" --json | jq '.knowledge_graph, .related_questions'
```

### Specific Sections Only
Extract only the sections you need:
```bash
scripts/search.py "restaurants" --sections organic_results local_results
```

## Response Structure

SerpAPI returns structured JSON with multiple sections:

- **organic_results**: Main web search results (title, link, snippet)
- **knowledge_graph**: Featured information box for entities
- **local_results**: Location-based business listings
- **related_questions**: "People also ask" section
- **shopping_results**: Product listings
- **recipes_results**: Recipe cards
- **related_searches**: Alternative query suggestions

For detailed schema documentation, see [references/response_schema.md](references/response_schema.md).

## Script Options

The search script supports these options:

- `--api-key`: SerpAPI API key (or set SERPAPI_API_KEY env var)
- `--location`: Location for local results (e.g., "Austin, Texas")
- `--hl`: Language code (default: en)
- `--gl`: Country code (default: us)
- `--num`: Number of results (default: 10)
- `--json`: Output raw JSON instead of formatted text
- `--sections`: Include specific sections only

## Installation

Requires the `google-search-results` package:

```bash
pip install google-search-results
```

On systems with externally-managed Python environments (macOS, some Linux distributions):

```bash
pip3 install --break-system-packages google-search-results
# or use a virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install google-search-results
```

## API Key

The skill uses the API key: `ceac1888ee08e1e41d3ae9a2176c888ad05a85955c8e0580b95b7ae4262a824a`

Set it as an environment variable to avoid passing it explicitly:

```bash
export SERPAPI_API_KEY="ceac1888ee08e1e41d3ae9a2176c888ad05a85955c8e0580b95b7ae4262a824a"
```
