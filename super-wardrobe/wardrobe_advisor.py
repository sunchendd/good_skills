#!/usr/bin/env python3
"""
Super 衣橱 - 每日穿搭建议
根据杭州实时天气 + DeepSeek AI 生成穿搭方案
"""

import urllib.request
import json
import os
import logging
import datetime
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CITY = "杭州"
CITY_EN = "Hangzhou"

# 用户穿搭偏好（可自定义）
USER_STYLE = """
- 性别：男
- 风格偏好：简约休闲为主，偶尔商务
- 身材：普通体型
- 常备衣物：T恤、衬衫、卫衣、连帽外套、羽绒服、西装、牛仔裤、休闲裤、西裤、运动裤
- 鞋子：白色运动鞋、皮鞋、休闲板鞋、雨靴
- 配件：棒球帽、休闲帽、手表（机械表/运动表）
- 不喜欢：过于鲜艳的颜色，喜欢低调配色（白/灰/黑/藏青/卡其）
"""

WEATHER_CODE_MAP = {
    "113": "晴天", "116": "多云", "119": "阴天", "122": "多云",
    "143": "有雾", "176": "小雨", "179": "小雪", "182": "雨夹雪",
    "185": "冻雨", "200": "雷阵雨", "227": "大雪", "230": "暴雪",
    "248": "浓雾", "260": "冻雾", "263": "毛毛雨", "266": "小雨",
    "281": "冻毛毛雨", "284": "冻毛毛雨", "293": "小雨", "296": "小雨",
    "299": "中雨", "302": "中雨", "305": "大雨", "308": "暴雨",
    "311": "冻雨", "314": "冻雨", "317": "雨夹雪", "320": "小雪",
    "323": "小雪", "326": "小雪", "329": "中雪", "332": "中雪",
    "335": "大雪", "338": "暴雪", "350": "冰雹", "353": "小雨",
    "356": "中到大雨", "359": "暴雨", "362": "雨夹雪", "365": "雨夹雪",
    "368": "小雪", "371": "大雪", "374": "冰雹", "377": "冰雹",
    "386": "雷阵雨", "389": "雷暴", "392": "雷雪", "395": "暴风雪",
}


def fetch_weather() -> dict:
    """获取杭州今日天气"""
    url = f"https://wttr.in/{CITY_EN}?format=j1"
    req = urllib.request.urlopen(url, timeout=15)
    data = json.loads(req.read())
    cur = data['current_condition'][0]
    today = data['weather'][0]
    tomorrow = data['weather'][1] if len(data['weather']) > 1 else today

    # 今日逐时分析
    hourly = today.get('hourly', [])
    max_rain_chance = max(int(h.get('chanceofrain', 0)) for h in hourly) if hourly else 0
    max_snow_chance = max(int(h.get('chanceofsnow', 0)) for h in hourly) if hourly else 0

    weather_code = cur.get('weatherCode', '116')
    weather_desc = WEATHER_CODE_MAP.get(weather_code, cur['weatherDesc'][0]['value'])

    return {
        'temp_now': int(cur['temp_C']),
        'feels_like': int(cur['FeelsLikeC']),
        'temp_max': int(today['maxtempC']),
        'temp_min': int(today['mintempC']),
        'humidity': int(cur['humidity']),
        'wind_kmph': int(cur['windspeedKmph']),
        'weather_desc': weather_desc,
        'rain_chance': max_rain_chance,
        'snow_chance': max_snow_chance,
        'uv_index': int(cur.get('uvIndex', 0)),
        'date': today['date'],
        'sunrise': today['astronomy'][0]['sunrise'],
        'sunset': today['astronomy'][0]['sunset'],
    }


def generate_outfit(weather: dict) -> str:
    """用 DeepSeek 生成穿搭建议"""
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    today = datetime.datetime.now().strftime("%Y年%m月%d日 %A")

    prompt = f"""你是一位专业时尚造型师，请根据今日天气为用户生成完整的穿搭建议。

## 今日天气（浙江杭州）
- 日期：{today}
- 当前气温：{weather['temp_now']}°C（体感 {weather['feels_like']}°C）
- 全天温度：{weather['temp_min']}°C ~ {weather['temp_max']}°C
- 天气状况：{weather['weather_desc']}
- 湿度：{weather['humidity']}%
- 风速：{weather['wind_kmph']} km/h
- 降雨概率：{weather['rain_chance']}%
- 降雪概率：{weather['snow_chance']}%
- 紫外线指数：{weather['uv_index']}

## 用户穿搭偏好
{USER_STYLE}

## 请生成以下穿搭建议：

请用以下结构输出（Markdown格式）：

### 🌤️ 今日天气总结
（一句话概括天气特点和穿衣重点）

### 👔 上衣推荐
（具体款式 + 颜色建议 + 理由）

### 👖 裤子推荐
（具体款式 + 颜色建议 + 理由）

### 👟 鞋子推荐
（推荐款式 + 理由，如果下雨说明）

### 🧢 帽子/配件
（帽子、手表建议）

### 🎨 整体配色方案
（今日推荐配色组合，2-3套方案，说明搭配原则）

### ☂️ 是否带伞
（明确说明：带 / 不带 / 建议带，并给出理由）

### 💡 今日穿搭小贴士
（1-2条实用建议，结合天气特点）

请保持建议实用、具体，语气轻松友好，不要太啰嗦。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        timeout=60,
    )
    return resp.choices[0].message.content


def format_full_newsletter(weather: dict, outfit: str) -> str:
    """组装完整的每日穿搭简报"""
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    now = datetime.datetime.now().strftime("%H:%M")

    weather_emoji = "☀️"
    if weather['rain_chance'] > 60: weather_emoji = "🌧️"
    elif weather['rain_chance'] > 30: weather_emoji = "🌦️"
    elif weather['temp_now'] < 5: weather_emoji = "🥶"
    elif '雪' in weather['weather_desc']: weather_emoji = "❄️"
    elif '雷' in weather['weather_desc']: weather_emoji = "⛈️"
    elif '多云' in weather['weather_desc'] or '阴' in weather['weather_desc']: weather_emoji = "⛅"

    lines = [
        f"# {weather_emoji} Super 衣橱 · 今日穿搭建议",
        f"**{today}** | 浙江杭州 | 生成于 {now}",
        "",
        "---",
        "",
        f"## 🌡️ 今日天气速览",
        f"| 项目 | 数据 |",
        f"|------|------|",
        f"| 当前气温 | {weather['temp_now']}°C（体感 {weather['feels_like']}°C）|",
        f"| 全天温度 | {weather['temp_min']}°C ~ {weather['temp_max']}°C |",
        f"| 天气状况 | {weather['weather_desc']} |",
        f"| 湿度 | {weather['humidity']}% |",
        f"| 降雨概率 | {weather['rain_chance']}% |",
        f"| 风速 | {weather['wind_kmph']} km/h |",
        f"| 日出 / 日落 | {weather['sunrise']} / {weather['sunset']} |",
        "",
        "---",
        "",
        outfit,
        "",
        "---",
        f"*Super 衣橱 · 每日穿搭助手 | {today}*",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    logger.info("👔 Super 衣橱开始运行...")
    weather = fetch_weather()
    logger.info(f"✅ 天气获取成功: {weather['weather_desc']} {weather['temp_min']}~{weather['temp_max']}°C")
    outfit = generate_outfit(weather)
    content = format_full_newsletter(weather, outfit)
    print(content)

    # 保存
    import pathlib
    out_dir = pathlib.Path(__file__).parent / "outfits"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"outfit_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(content, encoding='utf-8')
    logger.info(f"💾 已保存: {fname}")
