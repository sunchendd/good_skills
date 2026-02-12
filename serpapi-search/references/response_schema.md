# SerpAPI Response Schema Reference

## Common Response Sections

### search_metadata
Contains metadata about the search request and response:
- `id`: Unique search ID
- `status`: "Success" or error status
- `json_endpoint`: URL to retrieve results
- `created_at`, `processed_at`: Timestamps
- `total_time_taken`: Time in seconds

### search_parameters
Echo of the search parameters used:
- `engine`: Search engine ("google")
- `q`: Query string
- `location_requested`, `location_used`: Location parameters
- `hl`: Language code
- `gl`: Country code
- `device`: "desktop" or "mobile"

### search_information
High-level search statistics:
- `organic_results_state`: Result status
- `query_displayed`: How query was displayed
- `total_results`: Total number of results (approximate)
- `time_taken_displayed`: Time shown to users

## Result Sections

### organic_results
Main search results (array):
- `position`: Result position (1-based)
- `title`: Page title
- `link`: URL
- `displayed_link`: Simplified display URL
- `snippet`: Text excerpt
- `date`: Publication date (if available)
- `cached_page_link`: Link to cached version
- `related_pages_link`: Link to related pages
- `sitelinks`: Sub-links under main result
  - `inline`: Array of {title, link}

### knowledge_graph
Featured information box:
- `title`: Entity name
- `type`: Entity type (e.g., "Drink", "Person", "Company")
- `description`: Overview text
- `source`: {name, link} to source (often Wikipedia)
- `header_images`: Array of images
- `people_also_search_for`: Related entities
- Additional fields vary by entity type (books, nutritional info, etc.)

### local_results
Location-based results:
- `places`: Array of local businesses
  - `position`, `title`, `place_id`
  - `rating`, `reviews`, `price`: Business metrics
  - `type`: Business category
  - `address`: Street address
  - `gps_coordinates`: {latitude, longitude}
  - `thumbnail`: Image URL

### related_questions
"People also ask" section (array):
- `question`: Question text
- `snippet`: Answer excerpt
- `title`: Source page title
- `link`: Source URL
- `displayed_link`: Simplified URL

### related_searches
Alternative query suggestions (array):
- `query`: Suggested search term
- `link`: URL to execute that search

### shopping_results
Product listings (array):
- `position`, `title`, `price`, `extracted_price`
- `link`: Purchase URL
- `source`: Merchant name
- `reviews`: Review count
- `rating`: Product rating
- `thumbnail`: Product image URL

### recipes_results
Recipe cards (array):
- `title`, `link`, `source`
- `total_time`: Prep/cook time
- `rating`, `reviews`: User feedback
- `ingredients`: Array of ingredient names
- `thumbnail`: Recipe image

## Pagination

### pagination
Navigation through result pages:
- `current`: Current page number (1-based)
- `next`: URL to next page
- `other_pages`: Map of page number to URL

### serpapi_pagination
Same structure but with SerpAPI URLs instead of Google URLs

## Common Patterns

### Extracting Key Information

**Get organic results only:**
```python
results = search.get_dict()
organic = results.get("organic_results", [])
for result in organic:
    print(f"{result['title']}: {result['link']}")
```

**Check for knowledge graph:**
```python
if "knowledge_graph" in results:
    kg = results["knowledge_graph"]
    print(f"{kg['title']}: {kg.get('description', 'N/A')}")
```

**Get local businesses:**
```python
places = results.get("local_results", {}).get("places", [])
for place in places:
    print(f"{place['title']} - Rating: {place.get('rating', 'N/A')}")
```

### Handling Missing Fields

Not all fields appear in every response. Always use `.get()` with defaults:

```python
# Good
title = result.get("title", "N/A")
rating = place.get("rating", 0)

# Bad (may raise KeyError)
title = result["title"]
```

### Result Sections by Query Type

- **General queries**: organic_results, related_questions, related_searches
- **Local queries** ("coffee near me"): local_results, local_map, organic_results
- **Entity queries** ("Albert Einstein"): knowledge_graph, organic_results
- **Shopping queries** ("buy coffee beans"): shopping_results, organic_results
- **Recipe queries** ("coffee recipe"): recipes_results, organic_results
