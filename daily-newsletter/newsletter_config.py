#!/usr/bin/env python3
"""
早报配置文件
定义用户关注的领域、新闻源、API配置等
"""

# 用户关注的领域配置
USER_INTERESTS = {
    "新闻动态": {
        "keywords": ["科技新闻", "行业动态", "政策解读"],
        "sources": ["36kr", "pingwest", "techcrunch"],
        "priority": "high",
    },
    "产品发布": {
        "keywords": ["新品发布", "产品上市", "功能更新"],
        "sources": ["techcrunch", "36kr", "hacker_news"],
        "priority": "high",
    },
    "技术突破": {
        "keywords": [
            "技术创新",
            "研发突破",
            "专利发布",
            "开源项目",
            "算法优化",
            "性能提升",
            "架构创新",
            "芯片技术",
            "量子计算",
            "新材料",
        ],
        "sources": [
            "techcrunch",
            "hacker_news",
            "36kr",
            "arstechnica",
            "wired",
            "github",
        ],
        "priority": "high",
    },
    "AI推理": {
        "keywords": ["人工智能", "机器学习", "大模型", "推理引擎"],
        "sources": ["techcrunch", "hacker_news", "36kr"],
        "priority": "high",
    },
    "区块链": {
        "keywords": [
            "区块链",
            "加密货币",
            "比特币",
            "以太坊",
            "DeFi",
            "NFT",
            "Web3",
            "数字货币",
            "智能合约",
            "去中心化",
        ],
        "sources": [
            "coindesk",
            "binance_zh",
            "binance_en",
            "techcrunch",
            "36kr",
            "cointelegraph",
            "decrypt",
        ],
        "priority": "high",
    },
    "游戏产业": {
        "keywords": ["游戏开发", "电竞", "游戏发布", "游戏技术"],
        "sources": ["gamesindustry", "techcrunch", "36kr"],
        "priority": "medium",
    },
    "中国科技动态": {
        "keywords": ["国产化", "科技政策", "中国科技", "自主创新"],
        "sources": ["36kr", "pingwest", "techcrunch"],
        "priority": "high",
    },
    "股票黄金投资": {
        "keywords": ["股票", "黄金", "投资", "金融市场", "经济"],
        "sources": ["36kr", "pingwest", "techcrunch"],
        "priority": "medium",
    },
}

# 新闻源配置
NEWS_SOURCES = {
    "36kr": {
        "name": "36氪",
        "url": "https://36kr.com/",
        "rss": "https://36kr.com/feed",
        "language": "zh",
        "category": "tech",
    },
    "pingwest": {
        "name": "PingWest",
        "url": "https://www.pingwest.com/",
        "rss": "https://www.pingwest.com/feed",
        "language": "zh",
        "category": "tech",
    },
    "ithome": {
        "name": "IT之家",
        "url": "https://www.ithome.com/",
        "rss": "https://www.ithome.com/rss/",
        "language": "zh",
        "category": "tech",
    },
    "51cto": {
        "name": "51CTO",
        "url": "https://www.51cto.com/",
        "rss": "https://www.51cto.com/rss/",
        "language": "zh",
        "category": "tech",
    },
    "appso": {
        "name": "AppSo",
        "url": "https://www.appso.com/",
        "rss": "https://www.appso.com/feed/",
        "language": "zh",
        "category": "tech",
    },
    "qbitai": {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "rss": "https://www.qbitai.com/feed/",
        "language": "zh",
        "category": "ai",
    },
    "aigc": {
        "name": "AI工具集",
        "url": "https://www.aigc.cn/",
        "rss": "https://www.aigc.cn/feed/",
        "language": "zh",
        "category": "ai",
    },
    "ssdfans": {
        "name": "闪存市场",
        "url": "https://www.ssdfans.com/",
        "rss": "https://www.ssdfans.com/feed/",
        "language": "zh",
        "category": "storage",
    },
    "coindesk": {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/",
        "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "language": "en",
        "category": "crypto",
    },
    "gamesindustry": {
        "name": "GamesIndustry.biz",
        "url": "https://www.gamesindustry.biz/",
        "rss": "https://www.gamesindustry.biz/feed/",
        "language": "en",
        "category": "gaming",
    },
    "binance_zh": {
        "name": "币安中文博客",
        "url": "https://www.binance.com/zh-CN/blog",
        "rss": "https://www.binance.com/zh-CN/blog/rss.xml",
        "language": "zh",
        "category": "crypto",
    },
    "binance_en": {
        "name": "Binance Blog",
        "url": "https://www.binance.com/en/blog",
        "rss": "https://www.binance.com/en/blog/rss.xml",
        "language": "en",
        "category": "crypto",
    },
    "cointelegraph": {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com/",
        "rss": "https://cointelegraph.com/rss",
        "language": "en",
        "category": "crypto",
    },
    "decrypt": {
        "name": "Decrypt",
        "url": "https://decrypt.co/",
        "rss": "https://decrypt.co/feed",
        "language": "en",
        "category": "crypto",
    },
    "theblock": {
        "name": "The Block",
        "url": "https://www.theblock.co/",
        "rss": "https://www.theblock.co/rss.xml",
        "language": "en",
        "category": "crypto",
    },
    "okx_zh": {
        "name": "欧易OKX中文博客",
        "url": "https://www.okx.com/cn/learn",
        "rss": "https://www.okx.com/cn/learn/rss.xml",
        "language": "zh",
        "category": "crypto",
    },
    "okx_en": {
        "name": "OKX Blog",
        "url": "https://www.okx.com/learn",
        "rss": "https://www.okx.com/learn/rss.xml",
        "language": "en",
        "category": "crypto",
    },
    "wired": {
        "name": "Wired",
        "url": "https://www.wired.com/",
        "rss": "https://www.wired.com/feed/rss",
        "language": "en",
        "category": "tech",
    },
    "arstechnica": {
        "name": "Ars Technica",
        "url": "https://arstechnica.com/",
        "rss": "https://arstechnica.com/feed/",
        "language": "en",
        "category": "tech",
    },
    "theverge": {
        "name": "The Verge",
        "url": "https://www.theverge.com/",
        "rss": "https://www.theverge.com/rss/index.xml",
        "language": "en",
        "category": "tech",
    },
    "github": {
        "name": "GitHub Blog",
        "url": "https://github.com/blog",
        "rss": "https://github.com/blog.atom",
        "language": "en",
        "category": "dev",
    },
}

# API配置
API_CONFIG = {
    "newsapi": {
        "api_key": "YOUR_NEWSAPI_KEY",  # 需要申请
        "base_url": "https://newsapi.org/v2/",
        "enabled": False,
    },
    "google_news": {
        "api_key": "YOUR_GOOGLE_NEWS_API_KEY",  # 需要申请
        "base_url": "https://newsapi.org/v2/",
        "enabled": False,
    },
    "rss_feeds": {
        "enabled": True,
        "feeds": [
            # 中文科技媒体
            "https://36kr.com/feed",
            "https://www.pingwest.com/feed",
            "https://www.ithome.com/rss/",
            "https://www.51cto.com/rss/",
            "https://www.appso.com/feed/",
            "https://www.qbitai.com/feed/",
            "https://www.aigc.cn/feed/",
            "https://www.ssdfans.com/feed/",
            "https://www.geekpark.net/rss",
            "https://www.leiphone.com/feed",
            "https://www.ifanr.com/feed",
            "https://www.huxiu.com/rss.xml",
            "https://www.tmtpost.com/rss",
            "https://www.cyzone.cn/rss",
            # 国际科技媒体
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss",
            "https://www.theverge.com/rss/index.xml",
            "https://arstechnica.com/feed/",
            "https://www.engadget.com/rss.xml",
            "https://www.gizmodo.com/rss",
            "https://www.cnet.com/rss/news/",
            "https://www.zdnet.com/rss/",
            # 区块链和加密货币
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://www.binance.com/zh-CN/blog/rss.xml",
            "https://www.binance.com/en/blog/rss.xml",
            "https://www.okx.com/cn/learn/rss.xml",
            "https://www.okx.com/learn/rss.xml",
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
            "https://www.theblock.co/rss.xml",
            # 游戏产业
            "https://www.gamesindustry.biz/feed/",
            "https://www.polygon.com/rss/index.xml",
            "https://kotaku.com/rss",
            "https://www.ign.com/feeds/all",
            # AI和机器学习
            "https://openai.com/blog/rss.xml",
            "https://www.anthropic.com/blog/rss.xml",
            "https://www.deepmind.com/blog/rss.xml",
            # 开发者社区
            "https://github.com/blog.atom",
            "https://stackoverflow.blog/feed/",
            "https://dev.to/feed",
            "https://hackernoon.com/feed",
        ],
    },
}

# 早报格式配置
NEWSLETTER_CONFIG = {
    "title": "🌅 每日科技早报",
    "sections": [
        "🤖 AI推理与机器学习",
        "🔗 区块链与加密货币",
        "🎮 游戏产业动态",
        "🇨🇳 中国科技动态",
        "💰 投资与金融市场",
        "🚀 技术突破与创新",
        "📦 产品发布与新品",
    ],
    "max_articles_per_section": 3,
    "include_summary": True,
    "include_source": True,
    "include_timestamp": True,
}

# 内容平衡配置
CONTENT_BALANCE_CONFIG = {
    # 各分类新闻数量上限
    "category_limits": {
        "AI推理": 6,  # 适中数量
        "区块链": 8,  # 增加区块链权重
        "游戏产业": 8,  # 增加游戏产业权重
        "中国科技": 6,  # 增加中国科技
        "投资金融": 6,  # 增加投资金融
        "技术突破": 8,  # 增加技术突破
        "产品发布": 8,  # 增加产品发布
        "新闻动态": 5,  # 增加默认分类
    },
    # 分类权重调整（用于新闻获取时的优先级）
    "category_weights": {
        "区块链": 1.5,  # 提高区块链权重
        "游戏产业": 1.4,  # 提高游戏产业权重
        "AI推理": 1.2,
        "技术突破": 1.3,
        "产品发布": 1.1,
        "中国科技": 1.0,
        "投资金融": 1.0,
        "新闻动态": 0.8,
    },
    # 摘要配置
    "summary_config": {
        "min_length": 150,  # 最小摘要长度
        "max_length": 200,  # 最大摘要长度
        "target_length": 175,  # 目标长度
        "include_key_data": True,  # 包含关键数据
        "highlight_core_points": True,  # 突出核心观点
    },
    # 新闻重要性评分配置
    "importance_scoring": {
        "enabled": True,
        "factors": {
            "title_quality": 0.2,  # 标题质量
            "summary_completeness": 0.25,  # 摘要完整性
            "source_reliability": 0.2,  # 来源可靠性
            "content_relevance": 0.2,  # 内容相关性
            "data_richness": 0.15,  # 数据丰富度
        },
        "thresholds": {
            "high_quality": 0.8,  # 高质量阈值
            "good_quality": 0.6,  # 良好质量阈值
            "minimum_quality": 0.2,  # 最低质量阈值（大幅降低）
        },
    },
}

# 发送配置
DELIVERY_CONFIG = {
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_password",
    },
    "wechat": {"enabled": False, "webhook_url": "YOUR_WECHAT_WEBHOOK_URL"},
    "file": {"enabled": True, "output_dir": "./newsletters/", "format": "txt"},
}

# 时间配置
SCHEDULE_CONFIG = {
    "delivery_time": "09:00",  # 每日早9点
    "timezone": "Asia/Shanghai",
    "weekdays_only": False,  # 是否只在工作日发送
    "enabled": True,
}
