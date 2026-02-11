#!/usr/bin/env python3
"""
Simple grab script for bili-grabber skill.
Default behavior: search Bilibili for a keyword, fetch up to N BV ids, download cover images to result/bili_covers/, and PRINT results to stdout (no JSON/CSV files).
"""
import os,sys,urllib.request,re,json

def fetch_bvs(keyword,limit=10):
    url=f'https://search.bilibili.com/all?keyword={urllib.request.quote(keyword)}'
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        html=r.read().decode('utf-8',errors='ignore')
    bvs=re.findall(r'BV[0-9A-Za-z]+', html)
    seen=[]
    for b in bvs:
        if b not in seen:
            seen.append(b)
        if len(seen)>=limit:
            break
    return seen

def fetch_meta_and_cover(bvid):
    api=f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    try:
        req=urllib.request.Request(api, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            js=json.load(r)
        data=js.get('data',{})
        pic=data.get('pic')
        cover_path=''
        if pic:
            os.makedirs('result/bili_covers', exist_ok=True)
            try:
                req2=urllib.request.Request(pic, headers={'User-Agent':'Mozilla/5.0','Referer':f'https://www.bilibili.com/video/{bvid}'})
                ext=os.path.splitext(pic.split('?')[0])[1] or '.jpg'
                outp=os.path.join('result/bili_covers',f'{bvid}{ext}')
                with urllib.request.urlopen(req2, timeout=20) as rr:
                    open(outp,'wb').write(rr.read())
                cover_path=outp
            except Exception as e:
                cover_path=str(e)
        item={'bvid':bvid,'title':data.get('title'),'owner':data.get('owner',{}).get('name'),'view':data.get('stat',{}).get('view'),'duration':data.get('duration'),'cover_path':cover_path}
        return item
    except Exception as e:
        return {'bvid':bvid,'error':str(e)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--keyword','-k',default='跳舞')
    p.add_argument('--count','-n',type=int,default=10)
    args=p.parse_args()
    bvs=fetch_bvs(args.keyword,args.count)
    results=[]
    for b in bvs:
        meta=fetch_meta_and_cover(b)
        results.append(meta)
        # print in concise format (no JSON/CSV)
        if 'error' in meta:
            print(f"{b} | ERROR: {meta['error']}")
        else:
            print(f"{meta.get('title')} [{b}] by {meta.get('owner')} — views: {meta.get('view')}")
    # end
