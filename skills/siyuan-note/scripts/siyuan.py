#!/usr/bin/env python3
"""
SiYuan Note API helper script - Enhanced version

Provides utility functions for interacting with SiYuan Note API.
Batch operations, exports, organization features included.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Default configuration
# 本地访问: http://127.0.0.1:6806
# 公网访问: http://your-siyuan.example.com:6806 (替换为你的域名)
DEFAULT_HOST = os.environ.get("SIYUAN_HOST", "http://127.0.0.1:6806")
DEFAULT_TOKEN = os.environ.get("SIYUAN_TOKEN", "")


class SiYuanAPI:
    """SiYuan Note API client with enhanced features"""

    def __init__(self, host=None, token=None):
        self.host = host or DEFAULT_HOST
        self.token = token or DEFAULT_TOKEN

    def call(self, endpoint, data=None, timeout=30):
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
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"code": e.code, "msg": f"HTTP Error {e.code}: {e.reason}", "data": None}
        except urllib.error.URLError as e:
            return {"code": -1, "msg": f"Connection Error: {e.reason}", "data": None}
        except Exception as e:
            return {"code": -1, "msg": str(e), "data": None}

    def test_connection(self):
        """Test connection to SiYuan"""
        result = self.call("/api/system/conf")
        if result.get("code") == 0:
            return True, "Connection successful"
        else:
            return False, result.get("msg", "Unknown error")

    def get_all_notebooks(self):
        """Get list of all notebooks"""
        result = self.call("/api/notebook/lsNotebooks")
        if result.get("code") == 0:
            return result.get("data", {}).get("notebooks", [])
        return []

    def get_documents(self, notebook_id, path="/"):
        """Get documents in a notebook path"""
        result = self.call("/api/filetree/listDocsByPath", {
            "notebook": notebook_id,
            "path": path
        })
        if result.get("code") == 0:
            return result.get("data", {}).get("files", [])
        return []

    def export_document(self, doc_id):
        """Export document as markdown"""
        result = self.call("/api/export/exportMdContent", {"id": doc_id})
        if result.get("code") == 0:
            return result.get("data", {}).get("content", "")
        return None

    def search_documents(self, query, notebook_id=None):
        """Search documents by content"""
        if notebook_id:
            stmt = f"SELECT * FROM blocks WHERE box = '{notebook_id}' AND content LIKE '%{query}%' LIMIT 20"
        else:
            stmt = f"SELECT * FROM blocks WHERE content LIKE '%{query}%' LIMIT 20"

        result = self.call("/api/query/sql", {"stmt": stmt})
        if result.get("code") == 0:
            return result.get("data", [])
        return []

    def get_stats(self):
        """Get notebook statistics"""
        stats = {
            "total_notebooks": 0,
            "total_documents": 0,
            "total_size_kb": 0,
            "notebooks": []
        }

        notebooks = self.get_all_notebooks()
        stats["total_notebooks"] = len(notebooks)

        for nb in notebooks:
            nb_docs = self.get_documents(nb["id"])
            nb_size = sum(doc.get("size", 0) for doc in nb_docs)

            nb_info = {
                "id": nb["id"],
                "name": nb["name"],
                "document_count": len(nb_docs),
                "size_kb": round(nb_size / 1024, 2)
            }

            stats["notebooks"].append(nb_info)
            stats["total_documents"] += len(nb_docs)
            stats["total_size_kb"] += nb_size

        stats["total_size_kb"] = round(stats["total_size_kb"] / 1024, 2)
        return stats

    def export_notebook(self, notebook_id, output_dir, preserve_hierarchy=False):
        """Export all documents from a notebook"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        exported = 0
        failed = 0

        def export_recursive(nb_id, path, base_dir):
            nonlocal exported, failed

            docs = self.get_documents(nb_id, path)

            for doc in docs:
                doc_id = doc["id"]
                doc_name = doc["name"].replace(".sy", ".md")
                doc_path = doc["path"].replace(".sy", "")

                # Get content
                md_content = self.export_document(doc_id)

                if md_content:
                    # Determine output path
                    if preserve_hierarchy and path != "/":
                        rel_path = path.lstrip("/")
                        file_dir = base_dir / rel_path
                        file_dir.mkdir(parents=True, exist_ok=True)
                        file_path = file_dir / doc_name
                    else:
                        file_path = base_dir / doc_name

                    # Write file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    exported += 1
                else:
                    failed += 1

                # Recurse into subfolders
                if doc.get("subFileCount", 0) > 0:
                    export_recursive(nb_id, doc_path, base_dir)

        export_recursive(notebook_id, "/", output_path)

        return {"exported": exported, "failed": failed}

    def export_all_notebooks(self, output_dir):
        """Export all notebooks to directory"""
        stats = {
            "notebooks_exported": 0,
            "total_exported": 0,
            "total_failed": 0,
            "details": []
        }

        notebooks = self.get_all_notebooks()

        for nb in notebooks:
            nb_name = nb["name"]
            nb_id = nb["id"]
            nb_dir = Path(output_dir) / nb_name

            print(f"Exporting: {nb_name}...")

            result = self.export_notebook(nb_id, str(nb_dir), preserve_hierarchy=True)

            stats["notebooks_exported"] += 1
            stats["total_exported"] += result["exported"]
            stats["total_failed"] += result["failed"]

            stats["details"].append({
                "name": nb_name,
                "exported": result["exported"],
                "failed": result["failed"]
            })

        return stats

    def find_duplicates(self):
        """Find potential duplicate documents"""
        duplicates = []

        notebooks = self.get_all_notebooks()

        for nb in notebooks:
            docs = self.get_documents(nb["id"])
            names = {}

            for doc in docs:
                name = doc["name"]
                if name in names:
                    names[name].append(doc)
                else:
                    names[name] = [doc]

            for name, docs_list in names.items():
                if len(docs_list) > 1:
                    duplicates.append({
                        "notebook": nb["name"],
                        "document_name": name,
                        "count": len(docs_list),
                        "ids": [d["id"] for d in docs_list]
                    })

        return duplicates

    def find_documents_by_pattern(self, pattern, notebook_id=None):
        """Find documents by name pattern"""
        matches = []

        if notebook_id:
            notebooks = [self.get_all_notebooks()[0]]  # Get specific
        else:
            notebooks = self.get_all_notebooks()

        for nb in notebooks:
            docs = self.get_documents(nb["id"])

            for doc in docs:
                if pattern.lower() in doc["name"].lower():
                    matches.append({
                        "notebook": nb["name"],
                        "notebook_id": nb["id"],
                        "document_id": doc["id"],
                        "name": doc["name"],
                        "size_kb": round(doc.get("size", 0) / 1024, 2),
                        "modified": doc.get("hMtime", "Unknown")
                    })

        return matches


def print_json(data):
    """Pretty print JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("SiYuan Note API Helper - Enhanced Version")
        print("=" * 50)
        print("\nUsage: python3 siyuan.py <command> [args...]")
        print("\nCommands:")
        print("\n  test                          Test connection to SiYuan")
        print("\n  ls-notebooks                  List all notebooks")
        print("  create-notebook <name>        Create a notebook")
        print("  delete-notebook <id>          Delete a notebook")
        print("\n  ls-docs <nb_id> [path]        List documents in notebook")
        print("  create-doc <nb_id> <path>     Create document with markdown")
        print("  delete-doc <id>               Delete document by ID")
        print("\n  search <keyword> [nb_id]      Search content (optional notebook)")
        print("  find <pattern> [nb_id]        Find documents by name pattern")
        print("  find-duplicates               Find potential duplicate documents")
        print("\n  export-md <id> [file]         Export document as markdown")
        print("  export-notebook <id> <dir>    Export all docs in notebook")
        print("  export-all-notebooks <dir>    Export all notebooks to directory")
        print("\n  stats                         Get notebook statistics")
        print("\nEnvironment variables:")
        print("  SIYUAN_HOST   SiYuan host (default: http://127.0.0.1:6806)")
        print("  SIYUAN_TOKEN  SiYuan API token (required)")
        print("\nExamples:")
        print("  python3 siyuan.py test")
        print("  python3 siyuan.py ls-notebooks")
        print("  python3 siyuan.py export-all-notebooks ~/backup")
        print("  python3 siyuan.py stats")
        print("  python3 siyuan.py find-duplicates")
        sys.exit(1)

    api = SiYuanAPI()
    command = sys.argv[1]

    # Connection test
    if command == "test":
        success, msg = api.test_connection()
        if success:
            print(f"✓ {msg}")
            print(f"  Host: {api.host}")
            print(f"  Token: {'*' * len(api.token)}")
        else:
            print(f"✗ {msg}")
            sys.exit(1)

    # List notebooks
    elif command == "ls-notebooks":
        notebooks = api.get_all_notebooks()
        print(f"\nNotebooks: {len(notebooks)}")
        print("-" * 50)
        for nb in notebooks:
            print(f"  📁 {nb['name']:30} ID: {nb['id'][:20]}...")

    # Create notebook
    elif command == "create-notebook":
        if len(sys.argv) < 3:
            print("Error: notebook name required")
            sys.exit(1)
        result = api.call("/api/notebook/createNotebook", {"name": sys.argv[2]})
        if result.get("code") == 0:
            nb_id = result["data"]["notebook"]["id"]
            print(f"✓ Notebook created: {sys.argv[2]}")
            print(f"  ID: {nb_id}")
        else:
            print(f"✗ Failed: {result.get('msg')}")

    # Delete notebook
    elif command == "delete-notebook":
        if len(sys.argv) < 3:
            print("Error: notebook ID required")
            sys.exit(1)
        result = api.call("/api/notebook/removeNotebook", {"notebook": sys.argv[2]})
        if result.get("code") == 0:
            print(f"✓ Notebook deleted: {sys.argv[2]}")
        else:
            print(f"✗ Failed: {result.get('msg')}")

    # List documents
    elif command == "ls-docs":
        if len(sys.argv) < 3:
            print("Error: notebook ID required")
            sys.exit(1)
        nb_id = sys.argv[2]
        path = sys.argv[3] if len(sys.argv) > 3 else "/"

        docs = api.get_documents(nb_id, path)
        print(f"\nDocuments in {path}: {len(docs)}")
        print("-" * 50)
        for doc in docs:
            print(f"  📄 {doc['name']:40} {doc['hSize']:>10}")

    # Create document
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
        if result.get("code") == 0:
            print(f"✓ Document created: {path}")
        else:
            print(f"✗ Failed: {result.get('msg')}")

    # Delete document
    elif command == "delete-doc":
        if len(sys.argv) < 3:
            print("Error: document ID required")
            sys.exit(1)
        result = api.call("/api/filetree/removeDocByID", {"id": sys.argv[2]})
        if result.get("code") == 0:
            print(f"✓ Document deleted: {sys.argv[2]}")
        else:
            print(f"✗ Failed: {result.get('msg')}")

    # Search
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: search keyword required")
            sys.exit(1)
        keyword = sys.argv[2]
        nb_id = sys.argv[3] if len(sys.argv) > 3 else None

        results = api.search_documents(keyword, nb_id)
        print(f"\nSearch Results: '{keyword}' - {len(results)} matches")
        print("-" * 50)
        for r in results[:10]:
            content = r.get("content", "")[:80].replace("\n", " ")
            print(f"  • {content}...")

    # Find by pattern
    elif command == "find":
        if len(sys.argv) < 3:
            print("Error: pattern required")
            sys.exit(1)
        pattern = sys.argv[2]
        nb_id = sys.argv[3] if len(sys.argv) > 3 else None

        matches = api.find_documents_by_pattern(pattern, nb_id)
        print(f"\nMatches: {len(matches)}")
        print("-" * 50)
        for m in matches:
            print(f"  📄 {m['notebook']}/{m['name']:30} {m['size_kb']} KB")

    # Find duplicates
    elif command == "find-duplicates":
        duplicates = api.find_duplicates()
        if not duplicates:
            print("\n✓ No duplicate documents found")
        else:
            print(f"\n⚠ Duplicates Found: {len(duplicates)}")
            print("-" * 50)
            for d in duplicates:
                print(f"  📁 {d['notebook']}: {d['document_name']}")
                print(f"     Count: {d['count']}, IDs: {', '.join([id[:15]+'...' for id in d['ids']])}")

    # Export single document
    elif command == "export-md":
        if len(sys.argv) < 3:
            print("Error: document ID required")
            sys.exit(1)
        doc_id = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else f"{doc_id}.md"

        content = api.export_document(doc_id)
        if content:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Exported to: {output_file}")
        else:
            print(f"✗ Failed to export document")

    # Export notebook
    elif command == "export-notebook":
        if len(sys.argv) < 4:
            print("Error: notebook ID and output directory required")
            sys.exit(1)
        nb_id = sys.argv[2]
        output_dir = sys.argv[3]

        result = api.export_notebook(nb_id, output_dir, preserve_hierarchy=True)
        print(f"\n✓ Export completed:")
        print(f"  Exported: {result['exported']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Output: {output_dir}")

    # Export all notebooks
    elif command == "export-all-notebooks":
        if len(sys.argv) < 3:
            output_dir = f"~/Desktop/siyuan_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            output_dir = sys.argv[2]
        output_dir = os.path.expanduser(output_dir)

        print(f"\nExporting all notebooks to: {output_dir}")
        print("-" * 50)

        stats = api.export_all_notebooks(output_dir)

        print(f"\n✓ Export completed:")
        print(f"  Notebooks: {stats['notebooks_exported']}")
        print(f"  Documents: {stats['total_exported']}")
        print(f"  Failed: {stats['total_failed']}")
        print("\nDetails:")
        for detail in stats['details']:
            print(f"  • {detail['name']}: {detail['exported']} exported, {detail['failed']} failed")

    # Statistics
    elif command == "stats":
        stats = api.get_stats()
        print(f"\n📊 Notebook Statistics")
        print("=" * 50)
        print(f"Total Notebooks: {stats['total_notebooks']}")
        print(f"Total Documents: {stats['total_documents']}")
        print(f"Total Size: {stats['total_size_kb']} KB")
        print("\nDetails:")
        print("-" * 50)
        for nb in stats['notebooks']:
            print(f"  📁 {nb['name']:30} {nb['document_count']:4} docs  {nb['size_kb']:8.2f} KB")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
