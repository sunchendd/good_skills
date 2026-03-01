#!/usr/bin/env python3
"""
中国象棋顾问 - 分析棋盘截图，给出最佳走法
支持：图片路径 / base64 / URL
"""
import sys, os, json, base64, logging
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 中国象棋知识库
CHESS_SYSTEM_PROMPT = """你是一位中国象棋大师，拥有专业级别的棋力和丰富的教学经验。

## 你的能力
1. **识别棋盘**：准确识别棋盘上每个棋子的位置（红方/黑方）
2. **局势分析**：评估当前形势（优势/均势/劣势）
3. **推荐走法**：给出最佳下一步，并解释原因
4. **战术识别**：识别将军、捉子、牵制、闪击等战术
5. **开局/中局/残局**：根据阶段给出针对性建议

## 棋子说明
- 红方：帅、仕、相、马、车、炮、兵
- 黑方：将、士、象、马、车、炮、卒

## 坐标系统
- 列：红方视角从右到左为1-9
- 行：从下到上为1-10（红方底线为1）

## 输出格式（请严格按此格式）
### 🔍 棋盘识别
（简述当前局面，双方棋子分布）

### ⚖️ 局势评估
（当前谁占优势，优势在哪里）

### 🎯 推荐走法
**最佳走法：** XXX → XXX（如：炮二平五）
**战术类型：** （进攻/防守/捉子/将军等）
**理由：** （为什么这样走，50字以内）

### 📋 备选走法
1. 走法A - 简短说明
2. 走法B - 简短说明

### ⚠️ 注意事项
（对手可能的反击，需要防范的威胁）

### 💡 学习要点
（这个局面体现的战术原理，帮助提升棋力）"""


def encode_image(image_path: str) -> str:
    """将本地图片转为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def analyze_chess_position(image_source: str, player_turn: str = "红方", question: str = "") -> str:
    """
    分析棋盘截图
    image_source: 本地路径 或 URL 或 base64字符串
    player_turn: "红方" 或 "黑方"（当前轮到谁走）
    question: 用户的具体问题
    """
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    # 构造图片内容
    if image_source.startswith("http"):
        image_content = {"type": "image_url", "image_url": {"url": image_source}}
    elif os.path.exists(image_source):
        ext = Path(image_source).suffix.lower().lstrip('.')
        if ext == 'jpg': ext = 'jpeg'
        b64 = encode_image(image_source)
        image_content = {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{b64}"}}
    else:
        # 假设是 base64
        image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_source}"}}

    user_text = f"当前轮到【{player_turn}】走棋。"
    if question:
        user_text += f"\n用户问题：{question}"
    else:
        user_text += "\n请分析这个棋盘局面，告诉我最佳的下一步走法。"

    # DeepSeek 支持视觉（deepseek-chat 模型支持图片输入）
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": CHESS_SYSTEM_PROMPT},
                {"role": "user", "content": [
                    image_content,
                    {"type": "text", "text": user_text}
                ]}
            ],
            max_tokens=1500,
            timeout=60,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # fallback: 纯文字模式（当不支持图片时）
        logger.warning(f"视觉API失败，切换文字模式: {e}")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": CHESS_SYSTEM_PROMPT},
                {"role": "user", "content": f"用户发来一张中国象棋棋盘截图，{user_text}\n（图片无法解析，请提示用户描述棋盘状态）"}
            ],
            max_tokens=500,
        )
        return resp.choices[0].message.content


def analyze_from_description(board_desc: str, player_turn: str = "红方") -> str:
    """根据文字描述分析棋局（无图片时）"""
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": CHESS_SYSTEM_PROMPT},
            {"role": "user", "content": f"当前轮到【{player_turn}】走棋。\n棋盘状态描述：\n{board_desc}\n\n请分析并给出最佳走法。"}
        ],
        max_tokens=1500,
        timeout=60,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python chess_advisor.py <图片路径或URL> [红方|黑方] [具体问题]")
        print("示例：python chess_advisor.py screenshot.png 红方")
        sys.exit(1)

    image = sys.argv[1]
    turn = sys.argv[2] if len(sys.argv) > 2 else "红方"
    question = sys.argv[3] if len(sys.argv) > 3 else ""

    print(f"🔍 分析棋盘：{image}（{turn}走）")
    result = analyze_chess_position(image, turn, question)
    print(result)
