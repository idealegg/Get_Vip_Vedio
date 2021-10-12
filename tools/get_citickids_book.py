# -*- coding:utf-8 -*-
import requests
import os
import sys
import json
from bs4 import BeautifulSoup


def get_a_page(id, src):
    '''
    id=147&source=1
    '''
    textmod = {"id": id,
               "source": src,
               }
    '''GET /zx/book/audio?id=147&source=1 HTTP/1.1
    Host: www.citickids.com
    Connection: keep-alive
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63040026)
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Cookie: XSRF-TOKEN=eyJpdiI6ImRKZERJUE1cL016SlwvR0w4OTJ6UDRSUT09IiwidmFsdWUiOiJuYkRidjU4M0o2cStlV0RGMkdBZ05ZVlwvVzVkR0x5d0RqY2JaYk90QlNpbHdRSlU5K2FDM3hMZWNLdTdtUmJQSjNUcmdRK0xRODREYWFIRGZzamhIYmc9PSIsIm1hYyI6IjdlYmYzNWNlOTcyNGM2N2VlZDZiYTkxZGFiMWMyYTk1ZmM3YzczOWQyOGUyMDYzZmU4Njk1ODMwMjRhNTJmOTcifQ%3D%3D; laravel_session=eyJpdiI6IlE1YWtZdmlTTGl5UjZPYXR2ZFNpSnc9PSIsInZhbHVlIjoidU1sMVM2Y0ppXC9PSzhQSVFrRkhSdWdCeHVzR3ltcjhhTXJTR3BuN1I2MUxCN29CV3NPeXREZnBiekw4dW0zQUdYTTNxaVFoRTJBVkdUNUUrK2xTWGtBPT0iLCJtYWMiOiI2ZmIxOGM2ZjNjYmY0ODZlMTUxZjQyYTAzMjhlZTU2OTk1MmU3NmE0ZWQ4OThmNjNhOTE4Y2E3ODk3OGQ1ZDMzIn0%3D
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
    '''
    header_dict = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Accept-Encoding": "gzip,deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Host": "www.citickids.com",
                        "Cookie": "XSRF-TOKEN=eyJpdiI6ImRKZERJUE1cL016SlwvR0w4OTJ6UDRSUT09IiwidmFsdWUiOiJuYkRidjU4M0o2cStlV0RGMkdBZ05ZVlwvVzVkR0x5d0RqY2JaYk90QlNpbHdRSlU5K2FDM3hMZWNLdTdtUmJQSjNUcmdRK0xRODREYWFIRGZzamhIYmc9PSIsIm1hYyI6IjdlYmYzNWNlOTcyNGM2N2VlZDZiYTkxZGFiMWMyYTk1ZmM3YzczOWQyOGUyMDYzZmU4Njk1ODMwMjRhNTJmOTcifQ%3D%3D; laravel_session=eyJpdiI6IlE1YWtZdmlTTGl5UjZPYXR2ZFNpSnc9PSIsInZhbHVlIjoidU1sMVM2Y0ppXC9PSzhQSVFrRkhSdWdCeHVzR3ltcjhhTXJTR3BuN1I2MUxCN29CV3NPeXREZnBiekw4dW0zQUdYTTNxaVFoRTJBVkdUNUUrK2xTWGtBPT0iLCJtYWMiOiI2ZmIxOGM2ZjNjYmY0ODZlMTUxZjQyYTAzMjhlZTU2OTk1MmU3NmE0ZWQ4OThmNjNhOTE4Y2E3ODk3OGQ1ZDMzIn0%3D",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63040026)",
                        }
    url = 'http://www.citickids.com/zx/book/audio'
    with requests.get(url=url, params=textmod,  headers=header_dict) as req:
        print("get_a_page [%s] [%s] return code: %d" % (id, src, req.status_code))
        if req.status_code == 200:
            print(req.content)
            bs = BeautifulSoup(req.content, "html.parser")
            title_elem = bs.find('div', attrs={"class": "l-slide-tit"})
            title = title_elem.findChild('span').previous.strip()
            print("title: %s " % title)
            cur_dir = os.path.join(outdir, title)
            if not os.path.isdir(cur_dir):
                os.mkdir(os.path.join(outdir, title))
            jpgs = bs.find('ul', attrs={"class": "swiper-wrapper"})
            print("jpgs: %s" % jpgs)
            for index, jpg in enumerate(jpgs.find_all('img')):
                j_name = jpg['src'][jpg['src'].rfind('/')+1:]
                with requests.get(jpg['src']) as req2:
                    print("get_jpg req return code: %d" % req2.status_code)
                    if req2.status_code == 200:
                        with open(os.path.join(cur_dir, "%03d_%s" % (index, j_name)), "wb") as fd:
                            fd.write(req2.content)
                            print("write [%s] jpg [%s] [%s] ok: " % (index, j_name, id))
            mp3 = bs.find('div', attrs={"class": "l-audio-play"})
            print("mp3: %s" % mp3)
            with requests.get(mp3['data-audio']) as req2:
                print("get_mp3 req return code: %d" % req2.status_code)
                if req2.status_code == 200:
                    mp3_name = mp3['data-audio'][mp3['data-audio'].rfind('/') + 1:]
                    with open(os.path.join(cur_dir, mp3_name), "wb") as m3:
                        m3.write(req2.content)
                        print("write MP3 [%s] [%s] ok: " % (mp3_name, id))


if __name__ == "__main__":
    #outdir = r"D:\private\hd\son\LittleBearIsBusy"
    outdir = r"D:\private\hd\son\citickids_others"
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    ids=[
        '/zx/book/audio?id=132',  # 小熊很忙：参观恐龙园
        '/zx/book/audio?id=134',  # 小熊很忙：城堡小骑士
        '/zx/book/audio?id=135',  # 小熊很忙：动物管理员
        '/zx/book/audio?id=136',  # 小熊很忙：工地小帮手
        '/zx/book/audio?id=137',  # 小熊很忙：公园欢乐日
        '/zx/book/audio?id=138',  # 小熊很忙：欢乐农场日
        '/zx/book/audio?id=140',  # 小熊很忙：快乐的假期
        '/zx/book/audio?id=141',  # 小熊很忙：赛车小冠军
        '/zx/book/audio?id=142',  # 小熊很忙：深海潜水员
        '/zx/book/audio?id=143',  # 小熊很忙：圣诞小帮手
        '/zx/book/audio?id=144',  # 小熊很忙：树屋建筑师
        '/zx/book/audio?id=145',  # 小熊很忙：万圣节派对
        '/zx/book/audio?id=146',  # 小熊很忙：小小救护员
        '/zx/book/audio?id=147',  # 小熊很忙：小小消防员
        '/zx/book/audio?id=148',  # 小熊很忙：小小宇航员
        '/zx/book/audio?id=149',  # 小熊很忙：寻宝小海盗
        '/zx/book/audio?id=150',  # 小熊很忙：小小飞行员
        '/zx/book/audio?id=151',  # 小熊很忙：火车小司机
        '/zx/book/audio?id=152',  # 小熊很忙：披萨时间到
        '/zx/book/audio?id=153',  # 小熊很忙：足球小冠军
    ]
    #for id in map(lambda x: int(x.split('=')[1]), ids):
    #ids = range(132)
    ids = range(154, 1000)
    ids.insert(0, 139)
    ids.insert(0, 133)
    for id in ids:
        try:
            get_a_page(id, 1)
        except Exception, e:
            print(e)
