---
name: patent-search
description: >-
  Patent search via Google Patents (Serper.dev API). Search by keyword, inventor, assignee, or patent number. Use when checking patentability, analyzing competitors' patent portfolios, assessing infringement risks, or researching technology landscapes. Triggered by "专利检索", "patent search", "查专利", "专利布局", or any patent-related query.
---

# Patent Search

Search Google Patents via [Serper.dev API](https://google.serper.dev/patents). Returns patent metadata including title, inventors, assignees, filing/publication dates, abstract, and PDF links.

## Quick Start

```bash
# Keyword search
python3 scripts/patent_finder.py --keywords "machine learning" --limit 10

# Search by patent number
python3 scripts/patent_finder.py --patent "CN117453242A"

# JSON output for programmatic use
python3 scripts/patent_finder.py --keywords "孙晨东" --limit 20 --export json
```

## Workflow

When a user requests patent search:

1. **Confirm intent** - Clarify: inventor lookup, competitor analysis, technology landscape, or infringement check
2. **Build query** - Extract keywords, inventor names, or company names from the request
3. **Execute search** - Run `patent_finder.py` with appropriate arguments
4. **Filter results** - Remove noise (matching text but not inventor/assignee), categorize by assignee
5. **Generate report** - Output findings in a structured format (see Report Template below)

## Scripts

### `scripts/patent_finder.py`

High-level CLI with analysis and export. Use for end-user queries.

```
--keywords / -k    Search query (supports Chinese, inventor names, company names)
--patent  / -p     Look up by patent number
--limit   / -l     Max results (default 20, per-page max ~10)
--page    / -pg    Starting page (default 1)
--export  / -e     Output format: console (default), json, csv
```

### `scripts/google_patents_search.py`

Low-level API wrapper. Use programmatically in Python.

```python
from google_patents_search import GooglePatentsSearch, _api_get
searcher = GooglePatentsSearch()
results = searcher.search("keyword", limit=10, page=1)
```

## Search Tips

| Goal | Query Pattern |
|------|---------------|
| Inventor lookup | `"full name"` (quotes improve precision) |
| Company patents | `"company name"` |
| Cross-reference | Space-separated: `"inventor" "company"` |
| Patent details | `--patent CN123456789A` |

For very large results sets, increase `--limit` (auto-paginates in 10-result increments).

## Report Template

Structure findings as:

```markdown
# Patent Search Report: [Topic]

## Summary
- Total found: N
- By assignee: [breakdown]
- By year: [breakdown]

## Key Patents
[Table: patent_id, title, inventor, assignee, filing_date]

## Analysis
- Technology domains observed
- Key inventors / competitors
- Timeline trends
```

## Rate Limits

Serper.dev free tier has request limits. If queries return empty, wait a few seconds and retry. Set `SERPER_API_KEY` environment variable before running.
