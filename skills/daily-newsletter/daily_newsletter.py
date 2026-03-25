#!/usr/bin/env python3
"""
个性化每日早报生成器
关注领域：新闻动态、产品发布、技术突破、AI推理、区块链、游戏产业、中国科技动态、股票黄金投资
"""

import requests
import json
import datetime
from typing import List, Dict, Set
import os
from pathlib import Path
import feedparser
import re
from bs4 import BeautifulSoup
import time
import hashlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from newsletter_config import CONTENT_BALANCE_CONFIG

class DailyNewsletterGenerator:
    def __init__(self):
        self.interests = [
            "新闻动态", "产品发布", "技术突破", "AI推理", 
            "区块链", "游戏产业", "中国科技动态", "股票黄金投资"
        ]
        self.news_sources = {
            "tech_crunch": "https://techcrunch.com/",
            "hacker_news": "https://news.ycombinator.com/",
            "36kr": "https://36kr.com/",
            "pingwest": "https://www.pingwest.com/",
            "coindesk": "https://www.coindesk.com/",
            "game_industry": "https://www.gamesindustry.biz/"
        }
        # 新闻去重和分类管理
        self.seen_news = set()  # 已处理的新闻指纹
        self.news_by_category = defaultdict(list)  # 按分类存储新闻
        self.news_quality_scores = {}  # 新闻质量评分
        # 初始化 DeepSeek 翻译客户端（从环境变量 DEEPSEEK_API_KEY 读取，未配置则跳过）
        self._init_deepseek()
        # 读取日期范围（用于限定抓取新闻的时间窗口）
        self._date_filter_enabled = False
        self._start_date = None  # datetime.date
        self._end_date = None    # datetime.date
        self._load_date_range_from_env()
        
    def get_current_date(self) -> str:
        """获取当前日期"""
        return datetime.datetime.now().strftime("%Y年%m月%d日")
    
    def generate_news_fingerprint(self, title: str, summary: str, source: str = "", url: str = "") -> str:
        """生成新闻指纹用于去重（加入来源与URL以提升准确性）"""
        base = f"{title.strip()}|{summary.strip()}|{source.lower().strip()}|{url.strip()}"
        return hashlib.md5(base.encode('utf-8')).hexdigest()
    
    def calculate_news_quality(self, news: Dict) -> float:
        """计算新闻质量评分 - 增强版，特别优化技术新闻识别"""
        config = CONTENT_BALANCE_CONFIG['importance_scoring']
        factors = config['factors']
        score = 0.0
        
        # 技术白皮书/研究报告额外加分
        if any(word in news.get('title', '') + news.get('summary', '') 
               for word in ['白皮书', '技术报告', '研究报告', '论文']):
            score += 0.15  # 额外质量加分
        
        # 1. 标题质量评分 (20%)
        title = news.get('title', '')
        title_len = len(title)
        if title_len > 20:
            score += factors['title_quality'] * 0.6
        if title_len > 50:
            score += factors['title_quality'] * 0.4
            
        # 2. 摘要完整性评分 (25%)
        summary = news.get('summary', '')
        summary_len = len(summary)
        summary_config = CONTENT_BALANCE_CONFIG['summary_config']
        
        # 摘要长度评分
        if summary_len >= summary_config['min_length']:
            score += factors['summary_completeness'] * 0.5
        if summary_len >= summary_config['target_length']:
            score += factors['summary_completeness'] * 0.3
        if summary_len >= summary_config['max_length']:
            score += factors['summary_completeness'] * 0.2
            
        # 3. 来源可靠性评分 (20%)
        source = news.get('source', '').lower()
        trusted_sources = [
            '36氪', 'pingwest', 'ithome', '51cto', 'qbitai', '量子位', '机器之心', 'AI科技评论',
            '新智元', '极客公园', 'InfoQ', 'CSDN', '开源中国', 'SegmentFault',
            'DeepSeek', '深度求索', '智源社区', 'AI前线',
            'coindesk', 'binance', 'techcrunch', 'hacker news', 'wired', 'arstechnica', 'theverge'
        ]
        if any(trusted in source for trusted in trusted_sources):
            score += factors['source_reliability']
            
        # 4. 内容相关性评分 (20%)
        # 检查是否包含关键数据和核心观点
        key_data_indicators = ['价格', '融资', '投资', '发布', '上市', '技术', '创新', '突破', '专利', '研发', '金额', '数量', '百分比', '增长', '下降']
        if any(indicator in summary for indicator in key_data_indicators):
            score += factors['content_relevance'] * 0.6
            
        # 专业领域内容加分
        professional_keywords = [
            'AI', '人工智能', '机器学习', '深度学习', '大模型', 'LLM', 'GPT', 'ChatGPT', 
            '计算机视觉', 'NLP', '自然语言处理', '神经网络', '生成式AI', '多模态',
            'DeepSeek', 'OCR', '文本识别', '混元', '文心一言', '通义千问',
            '技术突破', '产品发布', '新品', '发布会', '白皮书', '技术报告'
        ]
        if any(keyword in summary for keyword in professional_keywords):
            score += factors['content_relevance'] * 0.4
            
        # 5. 数据丰富度评分 (15%)
        # 检查摘要中的数据丰富度
        data_indicators = ['元', '万', '亿', '%', '美元', '人民币', '用户', '市场', '营收', '利润', '增长', '下降']
        data_count = sum(1 for indicator in data_indicators if indicator in summary)
        if data_count >= 2:
            score += factors['data_richness'] * 0.6
        if data_count >= 4:
            score += factors['data_richness'] * 0.4
            
        # 避免低质量内容
        generic_phrases = [
            '关于', '最新动态', '重要新闻摘要', '这是关于', '8点1氪', '今日热点导览', 
            'TOP3大新闻', '文丨', '编辑丨', '作者 |', '编辑 |', '36氪获悉', '消息', '据悉',
            '爱范儿', 'ifanr'
        ]
        if any(phrase in summary for phrase in generic_phrases):
            score -= 0.2
            
        # 避免综合新闻和混杂内容
        if '8点1氪' in title or '今日热点' in title:
            score -= 0.3
            
        return min(max(score, 0.0), 1.0)
    
    def optimize_summary(self, news: Dict) -> str:
        """优化摘要质量 - 统一长度，突出关键数据"""
        original_summary = news.get('summary', '')
        summary_config = CONTENT_BALANCE_CONFIG['summary_config']
        
        # 如果摘要太短，尝试从标题和内容中提取更多信息
        if len(original_summary) < summary_config['min_length']:
            title = news.get('title', '')
            # 尝试从标题中提取关键信息
            if len(title) > 20:
                enhanced_summary = f"{title}。{original_summary}"
            else:
                enhanced_summary = original_summary
        else:
            enhanced_summary = original_summary
            
        # 确保摘要长度在目标范围内
        target_length = summary_config['target_length']
        if len(enhanced_summary) > summary_config['max_length']:
            # 截断到最大长度，保留关键信息
            enhanced_summary = enhanced_summary[:summary_config['max_length']]
            # 尝试在句号处截断
            last_period = enhanced_summary.rfind('。')
            if last_period > target_length:
                enhanced_summary = enhanced_summary[:last_period + 1]
        elif len(enhanced_summary) < summary_config['min_length']:
            # 如果仍然太短，添加通用描述
            enhanced_summary += "。该新闻涉及相关领域的最新发展动态。"
            
        return enhanced_summary

    def _init_deepseek(self):
        """初始化 DeepSeek 客户端（可选，缺少依赖或密钥则禁用翻译功能）"""
        self.deepseek_client = None
        try:
            import os
            api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
            if not api_key:
                return
            # 延迟导入，避免未安装 openai 库时报错中断
            from openai import OpenAI
            self.deepseek_client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        except Exception:
            # 静默失败，不影响主流程
            self.deepseek_client = None

    def _load_date_range_from_env(self):
        """从环境变量加载日期范围，格式 YYYY-MM-DD（闭区间）"""
        start = os.environ.get("NEWS_START_DATE", "").strip()
        end = os.environ.get("NEWS_END_DATE", "").strip()
        if not start or not end:
            # 默认过滤“今天”和“昨天”的新闻
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            self._start_date = yesterday
            self._end_date = today
            self._date_filter_enabled = True
            print(f"🗓️ 默认仅抓取 {yesterday} 至 {today} 的新闻")
            return
        try:
            self._start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            self._end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            if self._start_date > self._end_date:
                # 交换，保证 start <= end
                self._start_date, self._end_date = self._end_date, self._start_date
            self._date_filter_enabled = True
            print(f"🗓️ 抓取日期范围: {self._start_date} 至 {self._end_date}（含首尾）")
        except Exception as e:
            print(f"⚠️ 日期范围解析失败，忽略过滤: {e}")
            self._date_filter_enabled = False
            self._start_date = None
            self._end_date = None

    def _is_within_range(self, dt: datetime.datetime) -> bool:
        """判断给定时间是否在配置的日期范围内（按本地日期比较，闭区间）"""
        if not self._date_filter_enabled or not dt:
            return True
        local_date = dt.date()
        return self._start_date <= local_date <= self._end_date

    def _extract_entry_datetime(self, entry):
        """从 feedparser entry 提取发布时间（优先 published_parsed/updated_parsed）"""
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                return datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
            if hasattr(entry, "updated_parsed") and entry.updated_parsed:
                return datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
        except Exception:
            pass
        # 尝试从字符串字段解析 ISO 格式
        try:
            if hasattr(entry, "published") and entry.published:
                return datetime.datetime.fromisoformat(str(entry.published))
        except Exception:
            pass
        try:
            if hasattr(entry, "updated") and entry.updated:
                return datetime.datetime.fromisoformat(str(entry.updated))
        except Exception:
            pass
        return None

    def _fetch_and_parse_article_date(self, url: str) -> datetime.datetime:
        """在 RSS 无发布时间时，尝试抓取文章页面解析发布时间"""
        if not url:
            return None
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; NewsletterBot/1.0; +https://example.com)"
            }
            resp = requests.get(url, timeout=8, headers=headers)
            if resp.status_code >= 400 or not resp.text:
                return None
            soup = BeautifulSoup(resp.text, "html.parser")

            # 常见 meta/property
            candidates = []
            # OpenGraph / Article
            for prop in ["article:published_time", "article:modified_time", "og:updated_time", "og:published_time"]:
                tag = soup.find("meta", attrs={"property": prop})
                if tag and tag.get("content"):
                    candidates.append(tag["content"])
            # 常见 name
            for name in ["pubdate", "publishdate", "date", "timestamp"]:
                tag = soup.find("meta", attrs={"name": name})
                if tag and tag.get("content"):
                    candidates.append(tag["content"])
            # <time datetime="...">
            t = soup.find("time")
            if t and t.get("datetime"):
                candidates.append(t["datetime"])

            # 尝试解析候选字符串
            def try_parse(dt_str: str):
                for fmt in [
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%a, %d %b %Y %H:%M:%S %Z",
                ]:
                    try:
                        return datetime.datetime.strptime(dt_str.strip(), fmt)
                    except Exception:
                        pass
                # 兜底：ISO-like
                try:
                    return datetime.datetime.fromisoformat(dt_str.strip().replace("Z", "+00:00"))
                except Exception:
                    return None

            for c in candidates:
                dt = try_parse(c)
                if dt:
                    # 转为本地日期比较（去掉 tz）
                    if dt.tzinfo:
                        dt = dt.astimezone().replace(tzinfo=None)
                    return dt

            # 正则在正文中匹配日期（风险较高，仅做兜底）
            m = re.search(r"(20\\d{2}-\\d{1,2}-\\d{1,2})(?:[ T](\\d{1,2}:\\d{2}:\\d{2}))?", resp.text)
            if m:
                s = m.group(1) + (" " + m.group(2) if m.group(2) else "")
                dt = try_parse(s)
                if dt:
                    if dt.tzinfo:
                        dt = dt.astimezone().replace(tzinfo=None)
                    return dt

            return None
        except Exception:
            return None

    def _is_english_text(self, text: str) -> bool:
        """粗略英文检测：ASCII 比例 + 英文常见词命中"""
        if not text:
            return False
        s = text.strip()
        ascii_chars = sum(1 for ch in s if ord(ch) < 128)
        ratio = ascii_chars / max(len(s), 1)
        common_words = ["the", "and", "or", "with", "for", "from", "is", "are", "this", "that", "of"]
        lower = s.lower()
        hit = sum(1 for w in common_words if w in lower)
        return ratio >= 0.85 or hit >= 2

    def _is_international_source(self, source: str) -> bool:
        """根据来源判断是否为国际英文媒体"""
        if not source:
            return False
        src = source.lower()
        international = [
            "techcrunch", "wired", "the verge", "arstechnica", "engadget", "gizmodo",
            "cnet", "zdnet", "cointelegraph", "decrypt", "the block", "polygon", "kotaku", "ign",
            "stackoverflow", "github", "hackernoon"
        ]
        return any(name in src for name in international)

    def _needs_translation(self, news: Dict) -> bool:
        """是否需要翻译为中文"""
        if not getattr(self, "deepseek_client", None):
            return False
        title = news.get("title", "")
        summary = news.get("summary", "")
        source = news.get("source", "")
        # 英文文本或国际英文媒体则尝试翻译
        return self._is_english_text(title + " " + summary) or self._is_international_source(source)

    def translate_en_to_zh(self, text: str) -> str:
        """调用 DeepSeek 将英文翻译为简体中文，失败则返回原文"""
        if not text or not getattr(self, "deepseek_client", None):
            return text
        try:
            resp = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个精确的中文翻译助手，只翻译为简体中文，保持关键信息与数字不变，简洁自然。"},
                    {"role": "user", "content": f"请将以下内容翻译为简体中文：\n{text}"}
                ],
                stream=False
            )
            return resp.choices[0].message.content.strip() if resp and resp.choices else text
        except Exception:
            return text
    
    def classify_news(self, news: Dict) -> str:
        """智能分类新闻"""
        title = news.get('title', '').lower()
        summary = news.get('summary', '').lower()
        content = f"{title} {summary}"
        
        # 定义分类关键词 - 大幅优化分类规则
        category_keywords = {
            'AI推理': [
                'ai', '人工智能', '机器学习', '大模型', 'gpt', 'chatgpt', '智能', '算法', 
                '混元', 'rag', '深度学习', '神经网络', '自然语言处理', 'nlp', '计算机视觉',
                '语音识别', '机器翻译', '智能助手', '对话系统', '生成式ai', '多模态'
            ],
            '区块链': [
                '区块链', '比特币', '以太坊', '加密货币', 'defi', 'nft', '币安', 'binance', 
                'okx', '欧易', 'crypto', '数字货币', '虚拟货币', '挖矿', '共识机制', '智能合约', 
                '去中心化', 'web3', '元宇宙', '数字资产', 'token', 'coin', 'wallet', '交易所', 
                '钱包', '交易', '投资', 'defi', 'staking', '流动性', '跨链'
            ],
            '游戏产业': [
                '游戏', '电竞', '手游', '游戏开发', '游戏产业', 'game', 'gaming', '电玩展', 
                '游戏展', '游戏引擎', '游戏设计', '游戏美术', '游戏策划', '游戏运营',
                '游戏测试', '游戏发行', '游戏平台', 'steam', 'epic', 'playstation', 'xbox'
            ],
            '产品发布': [
                '发布', '新品', '上市', '推出', '产品', '新功能', '汽车', '车型', '比亚迪', 
                '方程豹', '手机', '电脑', '平板', '耳机', '音响', '相机', '无人机', '智能家居',
                '智能穿戴', '智能手表', '智能眼镜', 'vr', 'ar', 'mr'
            ],
            '技术突破': [
                '技术', '突破', '创新', '研发', '专利', '技术突破', '开源', '模型', '算法',
                '芯片', '处理器', '半导体', '量子计算', '量子通信', '5g', '6g', '物联网',
                '边缘计算', '云计算', '大数据', '数据库', '操作系统', '编程语言', '框架',
                '架构', '性能优化', '安全技术', '加密技术', '生物技术', '新材料'
            ],
            '投资金融': [
                '投资', '融资', '股票', '黄金', '金融', '市场', '资金', '创业', '金沙江', 
                'pre-a轮', 'a轮', 'b轮', 'c轮', 'ipo', '上市', '估值', '风投', '私募',
                '基金', '债券', '期货', '期权', '外汇', '保险', '银行', '支付', 'fintech'
            ],
            '中国科技': [
                '中国', '国产', '自主', '科技政策', '国产化', '国际民航', '理事国', '华为',
                '小米', '腾讯', '阿里巴巴', '百度', '字节跳动', '京东', '美团', '滴滴',
                '国产替代', '自主可控', '科技自立', '创新驱动', '数字化转型'
            ]
        }
        
        # 特殊分类规则 - 处理具体案例
        if '比亚迪' in content or '方程豹' in content or '汽车' in content:
            return '产品发布'
        if '电玩展' in content or '游戏展' in content or '游戏' in content:
            return '游戏产业'
        if '混元' in content or 'rag' in content or 'ai' in content or '人工智能' in content:
            return 'AI推理'
        if '金沙江' in content or 'pre-a轮' in content or '融资' in content or '投资' in content:
            return '投资金融'
        if '国际民航' in content or '理事国' in content or '中国' in content:
            return '中国科技'
        if '区块链' in content or '比特币' in content or '加密货币' in content or 'okx' in content or '欧易' in content or 'binance' in content or '币安' in content:
            return '区块链'
        if '技术' in content or '突破' in content or '创新' in content or '研发' in content:
            return '技术突破'
        
        # 计算每个分类的匹配度
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return '新闻动态'  # 默认分类
    
    def fetch_rss_news(self, rss_url: str, max_results: int = 5) -> List[Dict]:
        """从RSS源获取新闻（带超时控制）"""
        try:
            # 设置超时时间为10秒
            import socket
            socket.setdefaulttimeout(10)
            
            feed = feedparser.parse(rss_url)
            news_list = []
            
            for entry in feed.entries[:max_results]:
                # 抽取发布时间并按需要过滤
                pub_dt = self._extract_entry_datetime(entry)
                if self._date_filter_enabled:
                    # 若缺少发布时间，尝试从文章页面自动解析
                    if not pub_dt and entry.get('link'):
                        pub_dt = self._fetch_and_parse_article_date(entry.get('link'))
                    # 不在范围内则跳过
                    if not pub_dt or not self._is_within_range(pub_dt):
                        continue  # 超出范围直接跳过

                # 清理HTML标签
                summary = BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text()
                title = BeautifulSoup(entry.get('title', ''), 'html.parser').get_text()

                # 统一 published_at 输出
                published_at = (
                    pub_dt.isoformat(timespec="seconds")
                    if pub_dt else entry.get('published', datetime.datetime.now().isoformat())
                )
                
                news_list.append({
                    "title": title,
                    "summary": summary[:400] + "..." if len(summary) > 400 else summary,  # 增加摘要长度到400字
                    "source": feed.feed.get('title', 'RSS Feed'),
                    "url": entry.get('link', ''),
                    "published_at": published_at
                })
            
            return news_list
        except Exception as e:
            print(f"RSS解析错误: {e}")
            return []
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """搜索相关新闻"""
        # RSS源列表 - 仅保留有效源（移除返回0条的源）
        rss_sources = [
            # 中文科技媒体（有效源）
            "https://36kr.com/feed",
            "https://www.ithome.com/rss/",
            "https://www.qbitai.com/feed/",
            "https://www.geekpark.net/rss",
            "https://www.leiphone.com/feed",
            "https://www.tmtpost.com/rss",
            "https://www.jiqizhixin.com/rss",  # 机器之心
            "https://www.52ai.com/rss",       # AI科技评论
            "https://www.aqniu.com/rss",      # 安全牛
            "https://www.infoq.cn/feed",      # InfoQ中文
            "https://www.oschina.net/news/rss",
            "https://segmentfault.com/blogs/rss",
            
            # 国际科技媒体（有效源）
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss",
            "https://www.theverge.com/rss/index.xml",
            "https://arstechnica.com/feed/",
            "https://www.cnet.com/rss/news/",
            
            # 区块链和加密货币（有效源）
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
            "https://www.theblock.co/rss.xml",
            
            # 游戏产业（有效源）
            "https://www.gamesindustry.biz/feed/",
            "https://www.polygon.com/rss/index.xml",
            
            # AI和机器学习（有效源）
            "https://openai.com/blog/rss.xml",
            "https://www.deepmind.com/blog/rss.xml",
            
            # 开发者社区（有效源）
            "https://stackoverflow.blog/feed/",
            "https://dev.to/feed",
            "https://hackernoon.com/feed"
        ]
        
        all_news = []
        
        # 多线程并发抓取RSS源 - 大幅提升速度
        print(f"📡 开始从 {len(rss_sources)} 个新闻源并发抓取数据...")
        
        def fetch_single_source(rss_url):
            """单个RSS源抓取函数"""
            try:
                news = self.fetch_rss_news(rss_url, 10)
                return rss_url, news, None
            except Exception as e:
                return rss_url, [], str(e)
        
        # 使用线程池并发处理（12核优化 + 超时控制）
        with ThreadPoolExecutor(max_workers=24) as executor:
            # 提交所有任务
            future_to_url = {executor.submit(fetch_single_source, url): url for url in rss_sources}
            
            completed = 0
            for future in as_completed(future_to_url):
                completed += 1
                url, news, error = future.result()
                
                if error:
                    print(f"  [{completed}/{len(rss_sources)}] ❌ {url[:50]}... 失败: {error}")
                else:
                    all_news.extend(news)
                    print(f"  [{completed}/{len(rss_sources)}] ✅ {url[:50]}... 获取 {len(news)} 条")
        
        print(f"🎯 并发抓取完成！共获取 {len(all_news)} 条原始新闻")
        
        # 去重和质量过滤 - 优化质量要求
        print(f"🔍 开始去重和质量过滤...")
        unique_news = []
        
        # 第一步：去重和摘要优化
        filtered_news = []
        for i, news in enumerate(all_news):
            if i % 20 == 0:
                print(f"  去重进度: {i}/{len(all_news)} ({i/len(all_news)*100:.1f}%)")
                
            fingerprint = self.generate_news_fingerprint(news['title'], news['summary'], news.get('source', ''), news.get('url', ''))
            if fingerprint not in self.seen_news:
                # 优化摘要质量
                news['summary'] = self.optimize_summary(news)
                filtered_news.append(news)
                self.seen_news.add(fingerprint)
        
        print(f"📝 去重完成！剩余 {len(filtered_news)} 条待处理")
        
        # 第二步：计算质量评分和初步过滤
        print(f"📊 开始质量评分...")
        for news in filtered_news:
            quality_score = self.calculate_news_quality(news)
            
            # 应用质量门槛
            thresholds = CONTENT_BALANCE_CONFIG['importance_scoring']['thresholds']
            if quality_score >= thresholds['minimum_quality']:
                news['quality_score'] = quality_score
                unique_news.append(news)
        
        print(f"✨ 初步过滤完成！获得 {len(unique_news)} 条高质量新闻")
        
        # 按质量评分排序
        unique_news.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return unique_news[:max_results]
    
    def collect_and_classify_news(self) -> Dict[str, List[Dict]]:
        """收集并智能分类所有新闻 - 优化内容平衡"""
        start_time = time.time()
        print(f"🚀 开始收集和分类新闻...")
        
        # 清空之前的数据
        self.seen_news.clear()
        self.news_by_category.clear()
        
        # 获取所有新闻 - 增加数量以支持内容平衡
        all_news = self.search_news("科技 技术 AI 区块链 游戏 投资 中国", 200)  # 提升到200条以增加覆盖
        
        # 智能分类
        print(f"📊 开始智能分类 {len(all_news)} 条新闻...")
        for i, news in enumerate(all_news):
            if i % 10 == 0:
                print(f"  分类进度: {i}/{len(all_news)} ({i/len(all_news)*100:.1f}%)")
            category = self.classify_news(news)
            self.news_by_category[category].append(news)
        
        # 显示分类统计
        print(f"📈 分类统计:")
        for category, news_list in self.news_by_category.items():
            print(f"  {category}: {len(news_list)} 条")
        
        # 应用内容平衡策略
        print(f"⚖️ 应用内容平衡策略...")
        self.apply_content_balance()
        
        elapsed = time.time() - start_time
        print(f"✅ 收集分类完成！耗时: {elapsed:.2f}秒")
        
        return dict(self.news_by_category)
    
    def apply_content_balance(self):
        """应用内容平衡策略"""
        category_limits = CONTENT_BALANCE_CONFIG['category_limits']
        
        # 对每个分类应用数量限制
        for category, limit in category_limits.items():
            if category in self.news_by_category:
                # 按质量评分排序，保留最高质量的新闻
                self.news_by_category[category].sort(
                    key=lambda x: x.get('quality_score', 0), 
                    reverse=True
                )
                # 限制数量
                self.news_by_category[category] = self.news_by_category[category][:limit]
        
        # 如果某些分类新闻不足，尝试从其他分类补充
        self.balance_categories()
    
    def balance_categories(self):
        """平衡各分类新闻数量"""
        category_limits = CONTENT_BALANCE_CONFIG['category_limits']
        category_weights = CONTENT_BALANCE_CONFIG['category_weights']
        
        # 检查哪些分类需要更多新闻
        under_represented = []
        for category, limit in category_limits.items():
            current_count = len(self.news_by_category.get(category, []))
            if current_count < limit * 0.5:  # 如果少于50%的目标数量
                under_represented.append((category, limit - current_count))
        
        # 如果某些分类新闻过多，可以重新分配
        over_represented = []
        for category, limit in category_limits.items():
            current_count = len(self.news_by_category.get(category, []))
            if current_count > limit:
                over_represented.append((category, current_count - limit))
        
        # 记录平衡调整
        print(f"内容平衡调整: 不足分类 {len(under_represented)} 个, 过多分类 {len(over_represented)} 个")
    
    def generate_ai_news(self) -> List[Dict]:
        """生成AI推理相关新闻"""
        return self.news_by_category.get('AI推理', [])[:3]
    
    def generate_blockchain_news(self) -> List[Dict]:
        """生成区块链相关新闻"""
        return self.news_by_category.get('区块链', [])[:3]
    
    def generate_gaming_news(self) -> List[Dict]:
        """生成游戏产业新闻"""
        return self.news_by_category.get('游戏产业', [])[:3]
    
    def generate_china_tech_news(self) -> List[Dict]:
        """生成中国科技动态"""
        return self.news_by_category.get('中国科技', [])[:3]
    
    def generate_investment_news(self) -> List[Dict]:
        """生成投资相关新闻"""
        return self.news_by_category.get('投资金融', [])[:3]
    
    def generate_tech_breakthrough_news(self) -> List[Dict]:
        """生成技术突破新闻"""
        return self.news_by_category.get('技术突破', [])[:3]
    
    def generate_product_launch_news(self) -> List[Dict]:
        """生成产品发布新闻"""
        return self.news_by_category.get('产品发布', [])[:3]
    
    def format_newsletter(self) -> str:
        """格式化早报内容"""
        # 先收集并分类所有新闻
        self.collect_and_classify_news()
        
        date = self.get_current_date()
        
        newsletter = f"""# 🌅 每日科技早报 - {date}

## 📰 今日重点关注领域
• 新闻动态 • 产品发布 • 技术突破 • AI推理  
• 区块链 • 游戏产业 • 中国科技动态 • 股票黄金投资

---

"""
        
        # 定义分类显示顺序和图标 - 按权重排序
        categories = [
            ('区块链', '🔗', '区块链与加密货币'),      # 提高权重
            ('游戏产业', '🎮', '游戏产业动态'),        # 提高权重
            ('AI推理', '🤖', 'AI推理与机器学习'),      # 降低权重
            ('技术突破', '🚀', '技术突破与创新'),
            ('产品发布', '📦', '产品发布与新品'),
            ('中国科技', '🇨🇳', '中国科技动态'),
            ('投资金融', '💰', '投资与金融市场')
        ]
        
        total_news_count = 0
        
        for category_key, icon, display_name in categories:
            news_list = self.news_by_category.get(category_key, [])
            if not news_list:
                continue
                
            # 应用分类数量限制
            category_limits = CONTENT_BALANCE_CONFIG['category_limits']
            max_articles = category_limits.get(category_key, 3)
            news_list = news_list[:max_articles]
                
            newsletter += f"""## {icon} {display_name}
*共 {len(news_list)} 条新闻*

"""
            
            # 显示新闻，应用摘要优化和按需翻译
            for i, news in enumerate(news_list, 1):
                # 获取质量指示器
                quality_score = news.get('quality_score', 0)
                thresholds = CONTENT_BALANCE_CONFIG['importance_scoring']['thresholds']
                
                if quality_score >= thresholds['high_quality']:
                    quality_indicator = "🔥"
                elif quality_score >= thresholds['good_quality']:
                    quality_indicator = "⭐"
                else:
                    quality_indicator = ""
                
                # 对要展示的英文新闻进行翻译
                if self._needs_translation(news):
                    print(f"    🌐 翻译展示新闻: {news.get('title', '')[:30]}...")
                    news['title'] = self.translate_en_to_zh(news.get('title', ''))
                    news['summary'] = self.translate_en_to_zh(news.get('summary', ''))
                
                # 使用优化后的摘要
                optimized_summary = news.get('summary', '')
                
                newsletter += f"""
### {i}. {quality_indicator} [{news['title']}]({news['url']})
**来源**: {news['source']}  
**摘要**: {optimized_summary}

"""
            
            total_news_count += len(news_list)
        
        # 统计信息 - 显示内容平衡效果
        category_stats = []
        balance_info = []
        category_limits = CONTENT_BALANCE_CONFIG['category_limits']
        
        for category_key, icon, display_name in categories:
            count = len(self.news_by_category.get(category_key, []))
            limit = category_limits.get(category_key, 3)
            if count > 0:
                category_stats.append(f"{icon} {display_name}: {count}条")
                # 计算平衡度
                balance_ratio = count / limit if limit > 0 else 0
                if balance_ratio >= 0.8:
                    balance_status = "✅"
                elif balance_ratio >= 0.5:
                    balance_status = "⚠️"
                else:
                    balance_status = "❌"
                balance_info.append(f"{icon} {balance_status}")
        
        newsletter += f"""---

## 📊 今日数据概览
- **总新闻数**: {total_news_count}条
- **分类统计**: {' | '.join(category_stats)}
- **内容平衡**: {' | '.join(balance_info)}
- **生成时间**: {datetime.datetime.now().strftime('%H:%M:%S')}

## 💡 使用说明
- 🔥 高质量新闻 (≥80%) | ⭐ 优质新闻 (≥60%)
- 摘要长度统一为150-200字，突出关键数据
- 内容平衡优化，避免单一类别过度集中
- 智能去重，避免重复内容

---
*📧 个性化早报系统 v3.0 | 🤖 基于AI的智能新闻聚合与内容平衡优化*
"""
        
        return newsletter
    
    def save_newsletter(self, content: str):
        """保存早报到文件"""
        out_dir = Path("newsletters")
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"daily_newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = out_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 早报已保存到: {filepath.absolute()}")
        return filepath
    
    def send_notification(self, newsletter_path: Path):
        """发送通知（邮件）"""
        print("📱 发送邮件通知中...")
        try:
            from email_sender import EmailSender
            import os
            
            # 从环境变量获取邮箱授权码
            email_password = os.getenv('QQ_EMAIL_PASSWORD')
            if not email_password:
                print("⚠️ 未设置QQ_EMAIL_PASSWORD环境变量，跳过邮件发送")
                return False
            
            sender = EmailSender()
            sender.set_credentials(email_password)
            
            success = sender.send_newsletter(newsletter_path)
            if success:
                print("✅ 邮件通知已发送")
                return True
            else:
                print("❌ 邮件发送失败")
                return False
                
        except Exception as e:
            print(f"❌ 邮件发送异常: {e}")
            return False

    def send_bark_notification(self, newsletter_path: Path):
        """发送 Bark 推送通知"""
        print("🔔 发送 Bark 推送中...")
        try:
            from bark_client import bark_notify

            # 从文件内容提取各分类第一条标题作为摘要
            import re as _re
            try:
                raw = newsletter_path.read_text(encoding="utf-8")
                # 找所有 h3 级别标题（新闻条目）
                headlines = _re.findall(r'^###\s+(.+)', raw, _re.MULTILINE)
                total = len(headlines)
                # 取前 3 条去掉 markdown 符号
                top = [_re.sub(r'[*_`]', '', h).strip()[:40] for h in headlines[:3]]
                summary = "\n".join(f"• {h}" for h in top)
                body = f"今日 {total} 条资讯\n{summary}" if top else f"今日早报已生成"
            except Exception:
                body = f"今日早报已生成 {datetime.datetime.now().strftime('%H:%M')}"
            title = f"📰 每日科技早报 {datetime.datetime.now().strftime('%m/%d')}"
            resp = bark_notify(title=title, body=body, sound="minuet", autoCopy=1, copy="打开文件查看详情")

            # 正确的成功判断：ok 或 response.code == 200 或 HTTP status_code < 400
            ok = bool((resp or {}).get("ok"))
            response_code = ((resp or {}).get("response") or {}).get("code")
            status_code = (resp or {}).get("status_code")

            print(f"🔍 Bark 返回: ok={ok}, status_code={status_code}, response={resp.get('response')}")

            if ok or response_code == 200 or (isinstance(status_code, int) and status_code < 400):
                print("✅ Bark 推送已发送")
                return True

            # 简单重试一次（网络抖动时）
            print("↻ 尝试重试 Bark 推送一次...")
            resp2 = bark_notify(title=title, body=body, sound="minuet", autoCopy=1, copy="打开文件查看详情")
            ok2 = bool((resp2 or {}).get("ok"))
            response_code2 = ((resp2 or {}).get("response") or {}).get("code")
            status_code2 = (resp2 or {}).get("status_code")
            print(f"🔍 重试返回: ok={ok2}, status_code={status_code2}, response={resp2.get('response')}")

            if ok2 or response_code2 == 200 or (isinstance(status_code2, int) and status_code2 < 400):
                print("✅ Bark 推送重试成功")
                return True

            print(f"❌ Bark 推送失败：{resp2}")
            return False
        except Exception as e:
            print(f"❌ Bark 推送异常: {e}")
            return False

def main():
    """主函数"""
    start_time = time.time()
    print("🌅 开始生成每日早报...")
    
    generator = DailyNewsletterGenerator()
    
    # 生成早报内容
    print("📝 开始格式化早报内容...")
    newsletter_content = generator.format_newsletter()
    
    # 保存到文件
    print("💾 保存早报文件...")
    filepath = generator.save_newsletter(newsletter_content)
    
    # 显示早报内容
    print("\n" + "="*60)
    print(newsletter_content)
    print("="*60)
    
    # 发送邮件通知
    generator.send_notification(filepath)

    # 发送 Bark 推送通知
    generator.send_bark_notification(filepath)
    
    total_time = time.time() - start_time
    print(f"\n🎉 每日早报生成完成！总耗时: {total_time:.2f}秒")
    print(f"📁 文件位置: {filepath.absolute()}")

if __name__ == "__main__":
    main()
