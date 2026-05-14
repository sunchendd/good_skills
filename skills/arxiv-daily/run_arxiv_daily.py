#!/usr/bin/env python3
"""
arXiv AI 论文每日精选 - 主入口
用法：
  python run_arxiv_daily.py           # 正常运行
  python run_arxiv_daily.py --test    # 测试模式（仅抓20篇）
  python run_arxiv_daily.py --no-send # 只生成，不发送
"""

import sys
import os
import logging
import datetime
from pathlib import Path

# 将当前目录加入路径
sys.path.insert(0, str(Path(__file__).parent))

from arxiv_fetcher import fetch_arxiv_papers, select_papers_with_deepseek, format_newsletter, save_newsletter, load_history, save_history
from email_sender import EmailSender
from bark_client import bark_notify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    test_mode = "--test" in sys.argv
    no_send = "--no-send" in sys.argv
    max_fetch = 10 if test_mode else 15
    max_output = 3  # 每日推送论文数量

    logger.info("=" * 60)
    logger.info("🔬 arXiv AI 论文每日精选 开始运行")
    logger.info(f"   模式: {'测试' if test_mode else '正常'} | 最大抓取: {max_fetch} | 输出: {max_output}")
    logger.info("=" * 60)

    import time
    t0 = time.time()

    # 0. 加载历史，去重
    history = load_history()
    logger.info(f"📚 已加载 {len(history)} 篇历史论文")

    # 1. 抓取
    papers = fetch_arxiv_papers(max_results=max_fetch)
    if not papers:
        logger.error("❌ 未抓取到论文，退出")
        sys.exit(1)

    # 去除历史重复
    papers = [p for p in papers if p['link'] not in history]
    logger.info(f"🔍 去重后剩余 {len(papers)} 篇")
    if not papers:
        logger.warning("⚠️ 全是历史重复论文，退出")
        sys.exit(0)

    # 2. 精选（DeepSeek）
    selected = select_papers_with_deepseek(papers)
    selected = selected[:max_output]  # 只取评分最高的 top N
    if not selected:
        logger.error("❌ 未精选到论文，退出")
        sys.exit(1)

    # 3. 格式化
    content = format_newsletter(selected)

    # 4. 保存
    filepath = save_newsletter(content)

    # 更新历史
    new_ids = {p['link'] for p in selected}
    history.update(new_ids)
    save_history(history)
    logger.info(f"📚 已更新历史（+{len(new_ids)} 篇，总计 {len(history)}）")

    # 5. 打印摘要
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    print("\n" + "=" * 60)
    print(content[:3000])  # 打印前3000字用于日志
    if len(content) > 3000:
        print(f"\n... (共 {len(selected)} 篇，已截断显示)")
    print("=" * 60)

    if no_send:
        logger.info("⏭️  --no-send 模式，跳过发送")
        return

    # 6. 发送邮件
    logger.info("📧 发送邮件...")
    subject = f"🔬 arXiv AI 论文精选 {today}（{len(selected)}篇）"
    sender = EmailSender()
    sender.send(content, subject)

    # 7. Bark 推送
    logger.info("🔔 发送 Bark 推送...")
    try:
        top3 = selected[:3]
        paper_lines = [f"今日精选 {len(selected)} 篇"]
        for i, p in enumerate(top3, 1):
            zh = p.get("zh_title") or p.get("en_title", "")
            score = p.get("score", 0)
            paper_lines.append(f"{i}. [{score:.2f}] {zh[:35]}")
        bark_notify(
            title=f"🔬 arXiv AI 论文精选 {today}",
            body="\n".join(paper_lines),
            sound="minuet",
            group="arxiv",
        )
        logger.info("✅ Bark 推送已发送")
    except Exception as e:
        logger.warning(f"⚠️ Bark 推送失败: {e}")

    elapsed = time.time() - t0
    logger.info(f"\n🎉 完成！共精选 {len(selected)} 篇，耗时 {elapsed:.1f}s")
    logger.info(f"📁 文件: {filepath}")


if __name__ == "__main__":
    main()
