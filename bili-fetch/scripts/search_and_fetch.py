#!/usr/bin/env python3
"""
Search Bilibili public API for a keyword, download thumbnails, and write results to JSON.
Usage: python3 search_and_fetch.py --keyword "翻跳 舞蹈" --count 10 --out results.json
"""
import argparse
import json
import os
import requests

def search(keyword, count):
    url='https://api.bilibili.com/x/web-interface/search/type'
    params={'search_type':'video','keyword':keyword,'ps':count}
    r=requests.get(url,params=params,headers={'User-Agent':'Mozilla/5.0'})
    r.raise_for_status()
    data=r.json()
    return data.get('data',{}).get('result',[])

def download_thumbnail(pic_url, outdir, name):
    if pic_url.startswith('//'):
        pic_url='https:'+pic_url
    if pic_url.startswith('http:'):
        pic_url=pic_url.replace('http:','https:')
    fn=os.path.join(outdir,name)
    with requests.get(pic_url,stream=True,headers={'User-Agent':'Mozilla/5.0'}) as r:
        r.raise_for_status()
        with open(fn,'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    return fn

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--keyword',required=True)
    p.add_argument('--count',type=int,default=10)
    p.add_argument('--out',default='results.json')
    p.add_argument('--thumb-dir',default='bili_thumbs')
    args=p.parse_args()
    os.makedirs(args.thumb_dir,exist_ok=True)
    items=search(args.keyword,args.count)
    results=[]
    for i,it in enumerate(items,1):
        title=it.get('title')
        bvid=it.get('bvid') or str(it.get('aid'))
        link=f'https://www.bilibili.com/video/{bvid}'
        pic=it.get('pic')
        try:
            thumb_name=f'{i}_{bvid}.jpg'
            thumb_path=download_thumbnail(pic,args.thumb_dir,thumb_name)
        except Exception as e:
            thumb_path=''
        results.append({'index':i,'title':title,'bvid':bvid,'link':link,'thumb':thumb_path,'desc':it.get('description','')})
    with open(args.out,'w',encoding='utf-8') as f:
        json.dump(results,f,ensure_ascii=False,indent=2)
    print('Wrote',args.out)
