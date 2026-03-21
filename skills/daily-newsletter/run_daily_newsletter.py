#!/usr/bin/env python3
"""
每日早报运行脚本
支持定时任务和手动执行
"""

import schedule
import time
import datetime
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from daily_newsletter import DailyNewsletterGenerator
from newsletter_config import SCHEDULE_CONFIG, DELIVERY_CONFIG

def run_newsletter():
    """运行早报生成"""
    print(f"🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 开始生成早报...")
    
    try:
        generator = DailyNewsletterGenerator()
        newsletter_content = generator.format_newsletter()
        
        # 保存到文件
        if DELIVERY_CONFIG["file"]["enabled"]:
            output_dir = Path(DELIVERY_CONFIG["file"]["output_dir"])
            output_dir.mkdir(exist_ok=True)
            
            filename = f"daily_newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            
            print(f"✅ 早报已保存到: {filepath}")
        
        # 发送通知
        generator.send_notification(filepath)

        # 发送 Bark 推送
        try:
            generator.send_bark_notification(filepath)
        except Exception as e:
            print(f"⚠️ Bark 推送异常: {e}")
        
        print("🎉 早报生成完成！")
        
    except Exception as e:
        print(f"❌ 早报生成失败: {str(e)}")

def setup_schedule():
    """设置定时任务"""
    if not SCHEDULE_CONFIG["enabled"]:
        print("⏰ 定时任务已禁用")
        return
    
    delivery_time = SCHEDULE_CONFIG["delivery_time"]
    
    # 设置每日定时任务
    schedule.every().day.at(delivery_time).do(run_newsletter)
    
    print(f"⏰ 已设置每日 {delivery_time} 自动生成早报")
    
    # 如果是工作日模式，调整调度
    if SCHEDULE_CONFIG["weekdays_only"]:
        schedule.clear()
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            getattr(schedule.every(), day).at(delivery_time).do(run_newsletter)
        print(f"⏰ 已设置工作日 {delivery_time} 自动生成早报")

def run_scheduler():
    """运行调度器"""
    print("🚀 早报调度器启动中...")
    print(f"📅 当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 计划时间: 每日 {SCHEDULE_CONFIG['delivery_time']}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='每日早报系统')
    parser.add_argument('--now', action='store_true', help='立即生成早报')
    parser.add_argument('--schedule', action='store_true', help='启动定时任务')
    parser.add_argument('--test', action='store_true', help='测试模式')
    
    args = parser.parse_args()
    
    if args.now:
        print("🔄 立即生成早报...")
        run_newsletter()
    elif args.schedule:
        setup_schedule()
        run_scheduler()
    elif args.test:
        print("🧪 测试模式 - 生成早报...")
        run_newsletter()
    else:
        print("📋 使用方法:")
        print("  python run_daily_newsletter.py --now      # 立即生成早报")
        print("  python run_daily_newsletter.py --schedule # 启动定时任务")
        print("  python run_daily_newsletter.py --test     # 测试模式")

if __name__ == "__main__":
    main()
