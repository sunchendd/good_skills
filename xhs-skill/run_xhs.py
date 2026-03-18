#!/usr/bin/env python3
"""
run_xhs.py — 小红书 (XHS) 检索与发布 Skill (MCP 接口/CLI 封装)

依赖：已在系统中安装 `xhs-mcp` 或兼容的 MCP 服务（支持 `xhs-mcp search|view|publish`）

用法：
  python run_xhs.py search "关键词"
  python run_xhs.py view <note_id>
  python run_xhs.py publish --title "标题" --content file:content.md --images img1.jpg img2.jpg --tags tag1 tag2 [--dry-run]

实现策略：优先调用 CLI `xhs-mcp`（系统安装的 MCP 服务器客户端），若不存在 CLI，则尝试用 mcporter 或直接 HTTP 调用本地 MCP server。
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# 尝试导入 shared（如果你已完成 shared 提取）
try:
    from shared.config import cfg
    from shared.bark import bark_notify
    from shared.siyuan import SiyuanClient
except Exception:
    cfg = None
    bark_notify = None
    SiyuanClient = None

XHS_CLI = shutil.which('xhs-mcp') or shutil.which('xhs-mcp-cli') or shutil.which('xhs')
MCP_CLI = shutil.which('mcporter')


def run_cmd(cmd: List[str], capture=True):
    try:
        if capture:
            r = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return r.stdout
        else:
            subprocess.run(cmd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print('Command failed:', ' '.join(cmd), file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        raise


def search_keyword(q: str, limit: int = 20):
    """使用 xhs-mcp CLI 搜索关键词，返回 JSON 列表"""
    if XHS_CLI:
        cmd = [XHS_CLI, 'search', '--query', q, '--limit', str(limit), '--json']
        out = run_cmd(cmd)
        try:
            return json.loads(out)
        except Exception:
            # 有些实现把 JSON 打包到最后一行
            for line in out.splitlines()[::-1]:
                try:
                    return json.loads(line)
                except Exception:
                    continue
            raise
    elif MCP_CLI:
        # mcporter call <server.tool>
        cmd = [MCP_CLI, 'call', 'xiaohongshu.search', f'query:{q}', f'limit:{limit}', '--output', 'json']
        out = run_cmd(cmd)
        return json.loads(out)
    else:
        raise RuntimeError('没有找到 xhs-mcp 或 mcporter CLI，请先安装 xhs-mcp 或配置 MCP server')


def view_note(note_id: str):
    if XHS_CLI:
        cmd = [XHS_CLI, 'view', '--id', note_id, '--json']
        out = run_cmd(cmd)
        try:
            return json.loads(out)
        except Exception:
            for line in out.splitlines()[::-1]:
                try:
                    return json.loads(line)
                except Exception:
                    continue
            raise
    elif MCP_CLI:
        cmd = [MCP_CLI, 'call', 'xiaohongshu.get_note', f'id:{note_id}', '--output', 'json']
        out = run_cmd(cmd)
        return json.loads(out)
    else:
        raise RuntimeError('没有找到 xhs-mcp 或 mcporter CLI，请先安装 xhs-mcp 或配置 MCP server')


def publish_note(title: str, content: str, images: List[str], tags: List[str], dry_run: bool = False):
    """发布笔记：content 支持直接文本或 file:path 指定从文件读取"""
    if content.startswith('file:'):
        fp = content.split(':', 1)[1]
        content = Path(fp).read_text(encoding='utf-8')

    if dry_run:
        print('DRY RUN — 将要发布的笔记：')
        print('标题:', title)
        print('标签:', tags)
        print('图片:', images)
        print('内容:
', content[:1000])
        return {'ok': True, 'dry_run': True}

    if XHS_CLI:
        cmd = [XHS_CLI, 'publish', '--title', title, '--content', content]
        if tags:
            cmd += ['--tags', ','.join(tags)]
        for img in images:
            cmd += ['--image', img]
        out = run_cmd(cmd)
        try:
            return json.loads(out)
        except Exception:
            return {'raw': out}
    elif MCP_CLI:
        args = ['title:' + shlex.quote(title), 'content:' + shlex.quote(content), 'tags:' + shlex.quote(','.join(tags))]
        for i, img in enumerate(images):
            args.append(f'image{i}:' + shlex.quote(img))
        cmd = [MCP_CLI, 'call', 'xiaohongshu.publish'] + args + ['--output', 'json']
        out = run_cmd(cmd)
        return json.loads(out)
    else:
        raise RuntimeError('没有找到 xhs-mcp 或 mcporter CLI，请先安装 xhs-mcp 或配置 MCP server')


def save_to_siyuan(title: str, content: str, path: Optional[str] = None):
    if not SiyuanClient:
        print('思源未配置，跳过保存')
        return None
    client = SiyuanClient(host=cfg.siyuan_host, token=cfg.siyuan_token)
    doc_name = (path or title[:10]).strip("/").split("/")[-1]
    res = client.create_automation_doc(
        feature_name="内容创作",
        report_name="无语哥日报",
        doc_name=doc_name,
        markdown=content,
        title=title,
    )
    return res


def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(prog='run_xhs')
    sub = p.add_subparsers(dest='cmd')

    s = sub.add_parser('search')
    s.add_argument('query')
    s.add_argument('--limit', type=int, default=20)

    v = sub.add_parser('view')
    v.add_argument('id')

    pub = sub.add_parser('publish')
    pub.add_argument('--title', required=True)
    pub.add_argument('--content', required=True, help='文本或 file:path')
    pub.add_argument('--images', nargs='*', default=[])
    pub.add_argument('--tags', nargs='*', default=[])
    pub.add_argument('--dry-run', action='store_true')

    args = p.parse_args(argv)
    if args.cmd == 'search':
        out = search_keyword(args.query, args.limit)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.cmd == 'view':
        out = view_note(args.id)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.cmd == 'publish':
        out = publish_note(args.title, args.content, args.images or [], args.tags or [], dry_run=args.dry_run)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        p.print_help()


if __name__ == '__main__':
    main()
