#!/usr/bin/env python3
"""
GitHub 监控：
1. vllm-project/vllm-ascend 新版本发布
2. deepseek-ai 新代码仓库
发现更新时立即 Bark 通知
"""
import urllib.request, json, os, sys, logging, datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
STATE_FILE = Path(__file__).parent / "state.json"

WATCHES = [
    {"type": "release", "repo": "vllm-project/vllm-ascend", "label": "vLLM-Ascend"},
    {"type": "new_repo", "org": "deepseek-ai", "label": "DeepSeek"},
]


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
    STATE_FILE.write_text(json.dumps(state, indent=2))


def send_bark(title: str, body: str, url: str = None):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(title=title, body=body, url=url, sound="alarm", group="github", isArchive=1)
        logger.info(f"✅ Bark: {title}")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")


def check_vllm_ascend_release(state: dict) -> list[str]:
    alerts = []
    try:
        releases = gh_get("/repos/vllm-project/vllm-ascend/releases?per_page=5")
        if not releases:
            return alerts
        latest = releases[0]
        tag = latest["tag_name"]
        last_known = state.get("vllm_ascend_latest_release")

        if last_known != tag:
            state["vllm_ascend_latest_release"] = tag
            pub = latest.get("published_at", "")[:10]
            body = latest.get("body", "")[:300]
            msg = f"🚀 vLLM-Ascend 新版本发布！\n\n版本：{tag}\n时间：{pub}\n\n{body[:200]}..."
            logger.info(f"🔔 vllm-ascend 新版本: {tag}")
            send_bark(
                title=f"🚀 vLLM-Ascend {tag} 发布",
                body=f"发布时间：{pub}\n{body[:100]}",
                url=latest.get("html_url"),
            )
            alerts.append(f"vLLM-Ascend 新版本：{tag}")
        else:
            logger.info(f"✓ vllm-ascend 无新版本（当前：{tag}）")
    except Exception as e:
        logger.error(f"❌ vllm-ascend 检查失败: {e}")
    return alerts


def check_deepseek_new_repos(state: dict) -> list[str]:
    alerts = []
    try:
        repos = gh_get("/orgs/deepseek-ai/repos?sort=created&per_page=10")
        known_repos = set(state.get("deepseek_known_repos", []))
        new_repos = []
        for r in repos:
            name = r["name"]
            if name not in known_repos:
                known_repos.add(name)
                new_repos.append(r)

        if new_repos:
            state["deepseek_known_repos"] = list(known_repos)
            for r in new_repos:
                created = r.get("created_at", "")[:10]
                desc = r.get("description") or "（暂无描述）"
                logger.info(f"🔔 DeepSeek 新仓库: {r['name']}")
                send_bark(
                    title=f"🆕 DeepSeek 新仓库：{r['name']}",
                    body=f"创建于：{created}\n{desc[:150]}",
                    url=r.get("html_url"),
                )
                alerts.append(f"DeepSeek 新仓库：{r['name']}")
        else:
            logger.info(f"✓ deepseek-ai 无新仓库（已知 {len(known_repos)} 个）")

        # 首次运行：初始化状态，不发通知
        if not state.get("deepseek_known_repos"):
            state["deepseek_known_repos"] = [r["name"] for r in repos]
            logger.info(f"✓ 初始化 deepseek 仓库列表（{len(repos)} 个）")
            alerts.clear()

    except Exception as e:
        logger.error(f"❌ deepseek 检查失败: {e}")
    return alerts


def main():
    logger.info("=" * 50)
    logger.info("🔍 GitHub 监控检查")
    logger.info(f"   时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    state = load_state()
    all_alerts = []
    all_alerts += check_vllm_ascend_release(state)
    all_alerts += check_deepseek_new_repos(state)
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
