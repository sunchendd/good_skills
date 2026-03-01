#!/usr/bin/env python3
"""
统一 CLI 入口 - 运行所有自建 skill
用法：
  python run.py arxiv-daily          # 运行单个 skill
  python run.py all                  # 运行全部
  python run.py --list               # 列出所有 skill
  python run.py --no-send arxiv-daily  # 只生成不发送
  python run.py --test vibe-daily    # 测试模式
"""
import sys
import os
import importlib
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── skill 注册表 ─────────────────────────────────────────────────────────────
SKILLS: dict[str, dict] = {
    "arxiv-daily": {
        "module": "arxiv-daily.run_arxiv_daily",
        "desc": "🔬 arXiv AI 论文每日精选",
    },
    "bili-daily": {
        "module": "bili-daily.run_bili_daily",
        "desc": "📺 B站+小红书 AI 视频精选",
    },
    "daily-digest": {
        "module": "daily-digest.run_daily_digest",
        "desc": "📅 每日日志聚合 → 思源笔记",
    },
    "daily-newsletter": {
        "module": "daily-newsletter.run_daily_newsletter",
        "desc": "🌅 每日科技早报",
    },
    "github-watcher": {
        "module": "github-watcher.run_github_watcher",
        "desc": "🔍 GitHub 监控（vLLM-Ascend/DeepSeek）",
    },
    "super-fitness": {
        "module": "super-fitness.run_fitness",
        "desc": "💪 Super 健身 · 每日任务",
    },
    "super-wardrobe": {
        "module": "super-wardrobe.run_wardrobe",
        "desc": "👔 Super 衣橱 · 每日穿搭",
    },
    "vibe-daily": {
        "module": "vibe-daily.run_vibe_daily",
        "desc": "🚀 Vibe Coding 日报",
    },
    "weekly-report": {
        "module": "weekly-report.run_weekly_report",
        "desc": "📋 每周工作周报",
    },
    "wuyu-xiaohongshu": {
        "module": "wuyu-xiaohongshu.run_wuyu",
        "desc": "😤 无语哥 · 小红书内容",
    },
}


def load_skill(name: str):
    """动态加载 skill 模块"""
    info = SKILLS[name]
    # 将 "arxiv-daily.run_arxiv_daily" → 导入路径需要处理 -
    # 由于目录名有 -，用 importlib 手动加载
    parts = info["module"].split(".")
    dir_name, file_name = parts[0], parts[1]
    module_path = ROOT / dir_name / f"{file_name}.py"
    
    spec = importlib.util.spec_from_file_location(info["module"], module_path)
    mod = importlib.util.module_from_spec(spec)
    # 把 skill 目录也加入 sys.path，以便内部相对导入
    skill_dir = str(ROOT / dir_name)
    if skill_dir not in sys.path:
        sys.path.insert(0, skill_dir)
    spec.loader.exec_module(mod)
    return mod


def run_skill(name: str, no_send: bool = False, test: bool = False):
    """运行单个 skill"""
    logger.info(f"{'='*60}")
    logger.info(f"▶ 运行 {name}: {SKILLS[name]['desc']}")
    logger.info(f"{'='*60}")
    
    # 注入命令行参数
    original_argv = sys.argv[:]
    sys.argv = [name]
    if no_send:
        sys.argv.append("--no-send")
    if test:
        sys.argv.append("--test")
    
    t0 = time.time()
    try:
        mod = load_skill(name)
        if hasattr(mod, "main"):
            mod.main()
        else:
            logger.error(f"❌ {name} 没有 main() 函数")
    except Exception as e:
        logger.error(f"❌ {name} 运行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.argv = original_argv
    
    elapsed = time.time() - t0
    logger.info(f"⏱️ {name} 耗时 {elapsed:.1f}s")


def main():
    args = sys.argv[1:]
    
    no_send = "--no-send" in args
    test = "--test" in args
    list_mode = "--list" in args
    
    # 过滤 flags
    skill_names = [a for a in args if not a.startswith("--")]
    
    if list_mode or not skill_names:
        if list_mode:
            print("\n📋 可用 Skills:")
            print("-" * 50)
            for name, info in SKILLS.items():
                print(f"  {name:<22} {info['desc']}")
            print("-" * 50)
            print(f"\n共 {len(SKILLS)} 个 skill")
        else:
            print(__doc__)
        return
    
    if "all" in skill_names:
        skill_names = list(SKILLS.keys())
    
    # 验证 skill 名称
    for name in skill_names:
        if name not in SKILLS:
            print(f"❌ 未知 skill: {name}")
            print(f"   可用: {', '.join(SKILLS.keys())}")
            sys.exit(1)
    
    t_total = time.time()
    for name in skill_names:
        run_skill(name, no_send=no_send, test=test)
    
    if len(skill_names) > 1:
        logger.info(f"\n🎉 全部完成！共 {len(skill_names)} 个 skill，总耗时 {time.time()-t_total:.1f}s")


if __name__ == "__main__":
    main()
