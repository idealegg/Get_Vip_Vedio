# -*- coding:utf-8 -*-
import requests
import os
import sys
import json
import re
from bs4 import BeautifulSoup
from urlparse import urlparse, parse_qsl


# npm install crypto-js
header_dict = {"Accept": "*/*",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"Cookie": "_xmLog=h5&09ab4943-c849-4b62-a6c8-7217e00d1691&2.4.7-alpha.3; xm-page-viewid=ximalaya-web; x_xmly_traffic=utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1634638950; Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070=1634638950",
"Host": "www.ximalaya.com",
"Pragma": "no-cache",
"Referer": "https://www.ximalaya.com/ertongjiaoyu/29276844/212766435",
"sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows",
"Sec-Fetch-Dest": "empty",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
"xm-sign": "1739526c9855db5f9234714267a67367(79)1634638952754(79)1634638951785",
}


def replace_name(name):
    return re.sub('[| ;,:]', '-', name)


def get_a_m4a(id, name, outdir, trackUrl, ptype=1):
    textmod = {"id": id,
               "ptype": ptype,
               }
    url = 'https://www.ximalaya.com/revision/play/v1/audio'
    header_dict["Referer"] = 'https://www.ximalaya.com%s'% trackUrl
    with requests.get(url=url, params=textmod, headers=header_dict) as req:
        print("get_a_m4a [%s] return code: %d" % (id, req.status_code))
        if req.status_code == 200:
            print(req.content)
            j = json.loads(req.content)
            if 'ret' in j and j['ret'] == 200:
                mp3_url = j['data']['src']
                with requests.get(url=mp3_url) as req2:
                    print("to download m4a [%s] return code: %d" % (id, req2.status_code))
                    if req2.status_code == 200:
                        with open(os.path.join(outdir, name), 'wb') as fd:
                            fd.write(req2.content)


def decode_url(s):
    cmd = 'node js\XiMaLaYa.js "%s"' % s
    content = ''
    with os.popen(cmd) as fd:
        content = fd.read()
    return content


def get_a_mp3(id, name, outdir, trackUrl, ptype=1):
    textmod = {"device": 'web',
               "trackId": id,
               }
    url = 'https://mobile.ximalaya.com/mobile-playpage/track/v3/baseInfo/1634643489023'
    header_dict["Referer"] = 'https://www.ximalaya.com/'
    with requests.get(url=url, params=textmod, headers=header_dict) as req:
        print("get_a_mp3 [%s] return code: %d" % (id, req.status_code))
        if req.status_code == 200:
            print(req.content)
            j = json.loads(req.content)
            req.close()
            if 'ret' in j and j['ret'] == 0:
                mp3 = filter(lambda x: x['type'] == 'MP3_64', j['trackInfo']['playUrlList'])[0]
                mp3_url = decode_url(mp3['url'])
                print("url: %s" % mp3_url)
                up = urlparse(url)
                with requests.get(url="%s://%s%s"%(up.scheme, up.netloc, up.path), params=dict(parse_qsl(up.query)), headers=header_dict ) as req2:
                    print("to download mp3 [%s] return code: %d" % (id, req2.status_code))
                    if req2.status_code == 200:
                        with open(os.path.join(outdir, "%s.mp3" % name), 'wb') as fd:
                            fd.write(req2.content)


def get_an_album(aid, outdir, num):
    textmod = {"id": aid, 'num': num, 'sort': -1, 'size': 300, 'ptype': 0}
    url = 'https://www.ximalaya.com/revision/play/v1/show'
    with requests.get(url=url, params=textmod, headers=header_dict) as req:
        print("get_an_album [%s] return code: %d" % (id, req.status_code))
        if req.status_code == 200:
            print(req.content)
            j = json.loads(req.content)
            if 'ret' in j and j['ret'] == 200:
                mp3s = j['data']['tracksAudioPlay']
                name = replace_name(mp3s[0]['albumName'])
                a_outdir = os.path.join(outdir, name)
                if not os.path.isdir(a_outdir):
                    os.mkdir(a_outdir)
                with open("%s.json" % a_outdir, 'wb') as fd:
                    fd.write(req.content)
                for mp3 in mp3s:
                    get_a_mp3(mp3['trackId'], replace_name(mp3['trackName']), a_outdir, mp3['trackUrl'])


if __name__ == "__main__":
    outdir = r'E:\hzw\xmly'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    albums = (
        #52905857,
        29276844,)
    for aid in albums:
        for num in range(2, 11):
            get_an_album(aid, outdir, num)