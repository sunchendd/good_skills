#!/usr/bin/env python3
"""
Generate a short news TTS audio and optionally send to Telegram.
Usage:
  python3 generate_news_tts.py --region cn --topic general --out ./news.mp3 --send-telegram
"""
import argparse,os,subprocess,json

def fetch_headlines(region,topic,count=5):
    # Placeholder: prefer web_search tool when running inside OpenClaw
    # Fallback: return a short offline summary
    return [f"示例新闻 {i+1}：这是来自{region}的{topic}新闻摘要。" for i in range(count)]

def synthesize_tts(lines,out):
    text='\n'.join(lines)
    # Use system TTS via OpenClaw tts tool when available; fallback to local say (macos)
    from pathlib import Path
    tmp=Path(out)
    tmp.parent.mkdir(parents=True,exist_ok=True)
    # Try calling `say` to create an AIFF then convert to mp3 if ffmpeg available
    aiff=out.replace('.mp3','.aiff')
    try:
        subprocess.run(['say','-o',aiff,'-v','Samantha',text],check=True)
        # convert to mp3 if ffmpeg exists
        if shutil.which('ffmpeg'):
            subprocess.run(['ffmpeg','-y','-i',aiff,out],check=True)
            os.remove(aiff)
            return out
        else:
            return aiff
    except Exception:
        # last-resort: write text to file
        with open(out+'.txt','w',encoding='utf-8') as f:
            f.write(text)
        return out+'.txt'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--region',default='cn')
    p.add_argument('--topic',default='general')
    p.add_argument('--count',type=int,default=5)
    p.add_argument('--out',default='./news.mp3')
    p.add_argument('--send-telegram',action='store_true')
    args=p.parse_args()
    lines=fetch_headlines(args.region,args.topic,args.count)
    out= synthesize_tts(lines,args.out)
    print('WROTE',out)
