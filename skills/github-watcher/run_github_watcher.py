#!/usr/bin/env python3
"""
GitHub 监控：
1. vllm-project/vllm 和 vllm-ascend 新版本发布
2. deepseek-ai 新代码仓库
3. vllm-project/vllm 和 vllm-ascend 有价值的新 PR
发现更新时立即 Bark 通知
"""
import urllib.request, json, os, sys, logging, datetime, re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
STATE_FILE = Path(__file__).parent / "state.json"

# PR 价值判断关键词
PR_KEYWORDS = [
    "speculative", "spec_decode", "spec decode", "eagle", "mtp",
    "kv_cache", "kv cache", "kv-cache", "prefix cach", "attention",
    "flash attention", "paged attention", "chunked prefill",
]
PR_VALUE_LABELS = {"feature", "enhancement", "new feature"}
PR_MIN_LINES = 200  # 变更行数超过此值视为有价值

# 监控 Release 的仓库列表
RELEASE_WATCH_REPOS = [
    {"repo": "vllm-project/vllm", "label": "vLLM"},
    {"repo": "vllm-project/vllm-ascend", "label": "vLLM-Ascend"},
]

# 监控 PR 的仓库列表
PR_WATCH_REPOS = [
    "vllm-project/vllm",
    "vllm-project/vllm-ascend",
]


def strip_md(text: str, max_len: int = 200) -> str:
    """去除 Markdown 标记，提取纯文本摘要"""
    if not text:
        return ""
    # 去掉 HTML 注释、代码块
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    # 去掉图片、链接，保留链接文字
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    # 去掉标题 # 号、加粗/斜体
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', text)
    # 去掉 checkbox
    text = re.sub(r'- \[[ xX]\]', '-', text)
    # 压缩空行，每行 strip
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and not l.startswith('<!--')]
    text = ' '.join(lines)
    # 压缩多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len] + ('…' if len(text) > max_len else '')


def extract_release_highlights(body: str, max_len: int = 200) -> str:
    """从 release notes 提取关键变更点（bullet points）"""
    if not body:
        return ""
    lines = body.splitlines()
    bullets = []
    for line in lines:
        line = line.strip()
        # 取 bullet 行（- 或 * 开头），跳过 checkbox
        if re.match(r'^[-*]\s+', line) and not re.match(r'^[-*]\s+\[[ xX]\]', line):
            clean = re.sub(r'^[-*]\s+', '', line)
            clean = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', clean)  # 链接文字
            clean = re.sub(r'[*_`]', '', clean).strip()
            if clean:
                bullets.append(f"• {clean}")
        if sum(len(b) for b in bullets) > max_len:
            break
    if bullets:
        result = '\n'.join(bullets)
        return result[:max_len] + ('…' if len(result) > max_len else '')
    # 没有 bullet 则退回纯文本
    return strip_md(body, max_len)


def gh_get(path: str) -> dict | list:
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "openclaw-github-watcher",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def send_bark(title: str, body: str, url: str = None):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(title=title, body=body, url=url, sound="alarm", group="github", isArchive=1)
        logger.info(f"✅ Bark: {title}")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")


def check_releases(state: dict) -> list[str]:
    alerts = []
    latest_releases: dict = state.setdefault("latest_releases", {})
    for watch in RELEASE_WATCH_REPOS:
        repo, label = watch["repo"], watch["label"]
        state_key = repo.replace("/", "_")
        try:
            releases = gh_get(f"/repos/{repo}/releases?per_page=5")
            if not releases:
                continue
            latest = releases[0]
            tag = latest["tag_name"]
            last_known = latest_releases.get(state_key)

            if last_known is None:
                latest_releases[state_key] = tag
                logger.info(f"✓ 初始化 {label} release 状态（当前：{tag}）")
            elif last_known != tag:
                latest_releases[state_key] = tag
                pub = latest.get("published_at", "")[:10]
                highlights = extract_release_highlights(latest.get("body", ""), max_len=220)
                logger.info(f"🔔 {label} 新版本: {tag}")
                send_bark(
                    title=f"🚀 {label} {tag} 发布",
                    body=f"📅 {pub}\n{highlights}" if highlights else f"📅 {pub}",
                    url=latest.get("html_url"),
                )
                alerts.append(f"{label} 新版本：{tag}")
            else:
                logger.info(f"✓ {label} 无新版本（当前：{tag}）")
        except Exception as e:
            logger.error(f"❌ {label} release 检查失败: {e}")
    return alerts


def check_deepseek_new_repos(state: dict) -> list[str]:
    alerts = []
    try:
        repos = gh_get("/orgs/deepseek-ai/repos?sort=created&per_page=10")
        known_repos = set(state.get("deepseek_known_repos", []))

        if not known_repos:
            # 首次运行：初始化，不发通知
            state["deepseek_known_repos"] = [r["name"] for r in repos]
            logger.info(f"✓ 初始化 deepseek 仓库列表（{len(repos)} 个）")
            return alerts

        new_repos = [r for r in repos if r["name"] not in known_repos]
        if new_repos:
            for r in new_repos:
                known_repos.add(r["name"])
                created = r.get("created_at", "")[:10]
                desc = r.get("description") or "（暂无描述）"
                lang = r.get("language") or "—"
                stars = r.get("stargazers_count", 0)
                topics = "  ".join(r.get("topics", [])[:4])
                summary_lines = [desc[:120]]
                if topics:
                    summary_lines.append(f"🏷 {topics}")
                summary_lines.append(f"⭐ {stars}  🔤 {lang}  📅 {created}")
                logger.info(f"🔔 DeepSeek 新仓库: {r['name']}")
                send_bark(
                    title=f"🆕 DeepSeek：{r['name']}",
                    body="\n".join(summary_lines),
                    url=r.get("html_url"),
                )
                alerts.append(f"DeepSeek 新仓库：{r['name']}")
            state["deepseek_known_repos"] = list(known_repos)
        else:
            logger.info(f"✓ deepseek-ai 无新仓库（已知 {len(known_repos)} 个）")
    except Exception as e:
        logger.error(f"❌ deepseek 新仓库检查失败: {e}")
    return alerts


def is_valuable_pr(pr: dict) -> tuple[bool, str]:
    """判断 PR 是否有价值，返回 (是否有价值, 原因)"""
    title = pr.get("title", "").lower()
    labels = {lb["name"].lower() for lb in pr.get("labels", [])}

    # 关键词命中
    for kw in PR_KEYWORDS:
        if kw in title:
            return True, f"关键词：{kw}"

    # 标签命中
    hit = labels & PR_VALUE_LABELS
    if hit:
        return True, f"标签：{', '.join(hit)}"

    # 变更行数（需要额外 API 调用，暂用 changed_files 估算）
    changed_files = pr.get("changed_files", 0)
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    total_lines = additions + deletions
    if total_lines >= PR_MIN_LINES:
        return True, f"大型变更：+{additions}/-{deletions} 行"

    return False, ""


def check_valuable_prs(state: dict) -> list[str]:
    alerts = []
    known_prs: dict = state.get("known_prs", {})

    for repo in PR_WATCH_REPOS:
        try:
            # 获取最近 20 条 open PR（按创建时间倒序）
            prs = gh_get(f"/repos/{repo}/pulls?state=open&sort=created&direction=desc&per_page=20")
            repo_known = set(known_prs.get(repo, []))
            is_init = repo not in known_prs

            new_valuable = []
            for pr in prs:
                pr_num = pr["number"]
                if pr_num in repo_known:
                    continue
                repo_known.add(pr_num)
                if not is_init:
                    valuable, reason = is_valuable_pr(pr)
                    if valuable:
                        new_valuable.append((pr, reason))

            known_prs[repo] = list(repo_known)

            if is_init:
                logger.info(f"✓ 初始化 {repo} PR 状态（已知 {len(repo_known)} 个）")
            elif new_valuable:
                for pr, reason in new_valuable:
                    author = pr.get("user", {}).get("login", "unknown")
                    title = pr["title"]
                    pr_url = pr.get("html_url", "")
                    additions = pr.get("additions", 0)
                    deletions = pr.get("deletions", 0)
                    changed_files = pr.get("changed_files", 0)
                    pr_summary = strip_md(pr.get("body", ""), max_len=150)
                    body_lines = [title]
                    if pr_summary:
                        body_lines.append(pr_summary)
                    body_lines.append(f"👤 {author}  📂 {changed_files}文件  +{additions}/-{deletions}")
                    body_lines.append(f"💡 {reason}")
                    logger.info(f"🔔 {repo} 新值得关注 PR #{pr['number']}: {title}")
                    send_bark(
                        title=f"🔥 {repo.split('/')[-1]} PR #{pr['number']}",
                        body="\n".join(body_lines),
                        url=pr_url,
                    )
                    alerts.append(f"{repo} PR #{pr['number']}: {title}")
            else:
                logger.info(f"✓ {repo} 无新值得关注 PR")
        except Exception as e:
            logger.error(f"❌ {repo} PR 检查失败: {e}")

    state["known_prs"] = known_prs
    return alerts


def main():
    logger.info("=" * 50)
    logger.info("🔍 GitHub 监控检查")
    logger.info(f"   时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    state = load_state()
    all_alerts = []
    all_alerts += check_releases(state)
    all_alerts += check_deepseek_new_repos(state)
    all_alerts += check_valuable_prs(state)
    save_state(state)

    if all_alerts:
        logger.info(f"📢 共 {len(all_alerts)} 条更新通知已发送")
        for a in all_alerts:
            print(f"  ✅ {a}")
    else:
        logger.info("✓ 无新动态")
    print("DONE")


if __name__ == "__main__":
    main()
