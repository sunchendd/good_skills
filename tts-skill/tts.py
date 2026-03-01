#!/usr/bin/env python3
"""
TTS 文字转语音 - 基于 edge-tts (微软神经网络TTS，免费)
支持：中文多音色、情感语气、语速调节、输出MP3
"""
import asyncio, edge_tts, sys, os, argparse, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ── 音色预设 ──────────────────────────────────────────────────────────────────
VOICES = {
    # 普通话女声
    "xiaoxiao":  {"id": "zh-CN-XiaoxiaoNeural",  "desc": "晓晓·温柔亲切·适合播报/故事"},
    "xiaoyi":    {"id": "zh-CN-XiaoyiNeural",     "desc": "晓伊·活泼甜美·适合娱乐"},
    "yunxia":    {"id": "zh-CN-YunxiaNeural",     "desc": "云夏·沉稳大气·适合新闻"},
    # 普通话男声
    "yunxi":     {"id": "zh-CN-YunxiNeural",      "desc": "云希·自然流畅·适合读文章"},
    "yunyang":   {"id": "zh-CN-YunyangNeural",    "desc": "云扬·专业播音·适合正式场合"},
    "yunjian":   {"id": "zh-CN-YunjianNeural",    "desc": "云健·运动激情·适合体育/励志"},
    # 方言
    "xiaobei":   {"id": "zh-CN-liaoning-XiaobeiNeural", "desc": "晓北·东北方言·搞笑日常"},
    "xiaoni":    {"id": "zh-CN-shaanxi-XiaoniNeural",   "desc": "晓妮·陕西方言·特色内容"},
    # 英文
    "jenny":     {"id": "en-US-JennyNeural",      "desc": "Jenny·英文女声·自然"},
    "guy":       {"id": "en-US-GuyNeural",        "desc": "Guy·英文男声·播报"},
    # 默认
    "default":   {"id": "zh-CN-XiaoxiaoNeural",  "desc": "默认·晓晓"},
}

# 情感/风格映射（SSML style）
STYLES = {
    "neutral":      None,
    "chat":         "chat",           # 随意聊天
    "news":         "newscast",       # 新闻播报
    "newscast-casual": "newscast-casual",
    "customer":     "customerservice",# 客服
    "excited":      "excited",        # 兴奋
    "friendly":     "friendly",       # 友好
    "lyrical":      "lyrical",        # 抒情
    "poetry":       "poetry-reading", # 朗诵诗歌
    "sad":          "sad",            # 悲伤
    "angry":        "angry",          # 愤怒
    "fearful":      "fearful",        # 恐惧
    "disgruntled":  "disgruntled",    # 不满
    "serious":      "serious",        # 严肃
    "depressed":    "depressed",      # 沮丧
    "gentle":       "gentle",         # 温和
    "affectionate": "affectionate",   # 深情
    "embarrassed":  "embarrassed",    # 尴尬
}


async def synthesize(
    text: str,
    voice_name: str = "xiaoxiao",
    style: str = "neutral",
    rate: str = "+0%",      # "-10%" ~ "+20%"
    pitch: str = "+0Hz",
    output_path: str = None,
    play: bool = False,
) -> str:
    voice_info = VOICES.get(voice_name, VOICES["default"])
    voice_id = voice_info["id"]

    if output_path is None:
        import tempfile, datetime
        tmp_dir = Path(tempfile.gettempdir()) / "tts_output"
        tmp_dir.mkdir(exist_ok=True)
        output_path = str(tmp_dir / f"tts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")

    style_id = STYLES.get(style)

    if style_id:
        # 使用 SSML 注入情感
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
    xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='zh-CN'>
    <voice name='{voice_id}'>
        <mstts:express-as style='{style_id}'>
            <prosody rate='{rate}' pitch='{pitch}'>{text}</prosody>
        </mstts:express-as>
    </voice>
</speak>"""
        communicate = edge_tts.Communicate(text, voice_id)
        communicate.ssml = ssml
        # edge_tts 直接用SSML
        communicate = edge_tts.Communicate.__new__(edge_tts.Communicate)
        communicate.__init__(text, voice_id, rate=rate, pitch=pitch)
        try:
            # Try with style via direct SSML
            communicate2 = edge_tts.Communicate(ssml, voice_id)
        except:
            communicate2 = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
        try:
            await communicate2.save(output_path)
        except Exception:
            communicate3 = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
            await communicate3.save(output_path)
    else:
        communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
        await communicate.save(output_path)

    logger.info(f"✅ TTS 生成: {output_path} ({voice_id}, style={style})")

    if play:
        os.system(f"afplay '{output_path}'")

    return output_path


def list_voices():
    print("\n🎙️ 可用音色列表：\n")
    print(f"{'名称':<12} {'音色ID':<40} {'描述'}")
    print("-" * 80)
    for name, info in VOICES.items():
        if name != "default":
            print(f"{name:<12} {info['id']:<40} {info['desc']}")
    print(f"\n🎭 情感风格：{', '.join(STYLES.keys())}")
    print(f"\n📝 用法示例：")
    print(f"  python tts.py '你好，今天天气不错' -v yunyang -s news")
    print(f"  python tts.py '这也太离谱了吧！' -v xiaobei -s excited -r +20%")
    print(f"  python tts.py --file input.txt -v xiaoxiao -o output.mp3 --play")


def main():
    parser = argparse.ArgumentParser(description="TTS 文字转语音")
    parser.add_argument("text", nargs="?", help="要转换的文字")
    parser.add_argument("-v", "--voice", default="xiaoxiao", help="音色名称（见 --list）")
    parser.add_argument("-s", "--style", default="neutral", help="情感风格（见 --list）")
    parser.add_argument("-r", "--rate", default="+0%", help="语速 例如 -20%% 到 +50%%")
    parser.add_argument("-p", "--pitch", default="+0Hz", help="音调 例如 -50Hz 到 +50Hz")
    parser.add_argument("-o", "--output", default=None, help="输出文件路径(.mp3)")
    parser.add_argument("-f", "--file", default=None, help="从文件读取文字")
    parser.add_argument("--play", action="store_true", help="生成后自动播放")
    parser.add_argument("--list", action="store_true", help="列出所有音色和风格")
    args = parser.parse_args()

    if args.list:
        list_voices()
        return

    text = args.text
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    if not text:
        parser.print_help()
        return

    output = asyncio.run(synthesize(
        text=text,
        voice_name=args.voice,
        style=args.style,
        rate=args.rate,
        pitch=args.pitch,
        output_path=args.output,
        play=args.play,
    ))
    print(f"✅ 音频已保存: {output}")
    print(f"   播放命令: afplay '{output}'")


if __name__ == "__main__":
    main()
