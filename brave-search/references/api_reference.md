# Brave Search API Reference

## Base URLs

- Web Search: `https://api.search.brave.com/res/v1/web/search`
- Image Search: `https://api.search.brave.com/res/v1/images/search`

## Authentication

All requests require the `X-Subscription-Token` header with your API key.

```bash
X-Subscription-Token: YOUR_API_KEY
```

## Web Search

### Endpoint
```
GET https://api.search.brave.com/res/v1/web/search
```

### Query Parameters

- `q` (required): Search query string
- `count` (optional): Number of results (default: 10, max: 20)
- `search_lang` (optional): Language code (e.g., 'en', 'zh')
- `country` (optional): Country code for regional results
- `safesearch` (optional): 'off', 'moderate', or 'strict'
- `freshness` (optional): 'pd' (past day), 'pw' (past week), 'pm' (past month), 'py' (past year)
- `result_filter` (optional): Filter results by type (e.g., 'news', 'videos')

### Response Structure

```json
{
  "web": {
    "results": [
      {
        "title": "Page title",
        "url": "https://example.com",
        "description": "Page description snippet",
        "age": "Published date",
        "language": "en"
      }
    ]
  },
  "news": {
    "results": [...]
  }
}
```

## Image Search

### Endpoint
```
GET https://api.search.brave.com/res/v1/images/search
```

### Query Parameters

- `q` (required): Search query string
- `count` (optional): Number of results (default: 10, max: 20)
- `safesearch` (optional): 'off', 'moderate', or 'strict'

### Response Structure

```json
{
  "results": [
    {
      "title": "Image title",
      "url": "https://source-page.com",
      "properties": {
        "url": "https://image-url.com/image.jpg"
      },
      "thumbnail": {
        "src": "https://thumbnail-url.com"
      },
      "source": "Source website"
    }
  ]
}
```

## Rate Limits

- Free tier: 1 request per second
- Check your API dashboard for your specific rate limits

## Error Codes

- 400: Bad Request - Invalid parameters
- 401: Unauthorized - Invalid or missing API key
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error
