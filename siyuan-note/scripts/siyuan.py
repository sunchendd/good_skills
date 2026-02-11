#!/usr/bin/env python3
"""
SiYuan Note API helper script

Provides utility functions for interacting with SiYuan Note API.
Reads configuration from environment variables or command line.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

# Default configuration
DEFAULT_HOST = os.environ.get("SIYUAN_HOST", "http://127.0.0.1:6806")
DEFAULT_TOKEN = os.environ.get("SIYUAN_TOKEN", "")


class SiYuanAPI:
    """SiYuan Note API client"""

    def __init__(self, host=None, token=None):
        self.host = host or DEFAULT_HOST
        self.token = token or DEFAULT_TOKEN

    def call(self, endpoint, data=None):
        """Make API call to SiYuan"""
        url = f"{self.host}{endpoint}"
        headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

        request_data = json.dumps(data) if data else "{}"

        try:
            req = urllib.request.Request(
                url, data=request_data.encode("utf-8"), headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            return {"code": -1, "msg": str(e), "data": None}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 siyuan.py <command> [args...]")
        print("\nCommands:")
        print("  ls-notebooks              List all notebooks")
        print("  create-notebook <name>    Create a notebook")
        print("  delete-notebook <id>      Delete a notebook")
        print("  create-doc <notebook> <path> <markdown>")
        print("                            Create document with markdown")
        print("  delete-doc <id>           Delete document by ID")
        print("  search <query>            Search content")
        print("  export-md <id>            Export document as markdown")
        print("\nEnvironment variables:")
        print("  SIYUAN_HOST   SiYuan host (default: http://127.0.0.1:6806)")
        print("  SIYUAN_TOKEN  SiYuan API token (required)")
        sys.exit(1)

    api = SiYuanAPI()
    command = sys.argv[1]

    if command == "ls-notebooks":
        result = api.call("/api/notebook/lsNotebooks")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "create-notebook":
        if len(sys.argv) < 3:
            print("Error: notebook name required")
            sys.exit(1)
        result = api.call("/api/notebook/createNotebook", {"name": sys.argv[2]})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "delete-notebook":
        if len(sys.argv) < 3:
            print("Error: notebook ID required")
            sys.exit(1)
        result = api.call("/api/notebook/removeNotebook", {"notebook": sys.argv[2]})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "create-doc":
        if len(sys.argv) < 4:
            print("Error: notebook ID and path required")
            sys.exit(1)
        notebook = sys.argv[2]
        path = sys.argv[3]
        markdown = sys.argv[4] if len(sys.argv) > 4 else ""
        result = api.call(
            "/api/filetree/createDocWithMd",
            {"notebook": notebook, "path": path, "markdown": markdown},
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "delete-doc":
        if len(sys.argv) < 3:
            print("Error: document ID required")
            sys.exit(1)
        result = api.call("/api/filetree/removeDocByID", {"id": sys.argv[2]})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: search query required")
            sys.exit(1)
        stmt = f"SELECT * FROM blocks WHERE content LIKE '%{sys.argv[2]}%' LIMIT 10"
        result = api.call("/api/query/sql", {"stmt": stmt})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "export-md":
        if len(sys.argv) < 3:
            print("Error: document ID required")
            sys.exit(1)
        result = api.call("/api/export/exportMdContent", {"id": sys.argv[2]})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
