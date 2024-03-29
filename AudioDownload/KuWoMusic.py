# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from Util.myLogging import *


def get_ts_reqid():
    logger.info("To generate a reqid:\n")
    cmd = '%s %s' % (r'tools\phantomjs.exe',
                        r'js\kuwo_decode.js')
    logger.info("cmd: %s" % cmd)
    f_popen = os.popen(cmd)
    reqid = f_popen.read()
    logger.info("Return value: %s" % reqid)
    f_popen.close()
    return reqid.split()


def get_a_mp3(name, rid, outdir):
    ts, reqId = get_ts_reqid()
    '''format: mp3
    rid: 79914233
    response: url
    type: convert_url3
    br: 128kmp3
    from: web
    t: 1633332140353
    httpsStatus: 1
    reqId: cfc3e221-24e3-11ec-bc82-77d9ebcfed0a
    '''
    textmod = {"format": "mp3",
                    "rid": rid,
                    "response": "url",
                    "type": "convert_url3",
                    "br": "128kmp3",
                    "from": "web",
                    "t": ts,
                    "httpsStatus": "1",
                    "reqId": reqId}
    '''Host: bd.kuwo.cn
    Connection: keep-alive
    Pragma: no-cache
    Cache-Control: no-cache
    Accept: application/json, text/plain, */*
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36
    Referer: http://bd.kuwo.cn/play_detail/79914233
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: _ga=GA1.2.1124756597.1633243187; _gid=GA1.2.1062990606.1633243187; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1633243187,1633243216,1633271355,1633309840; _gat=1; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1633332115; kw_token=BHZYG1FCEU
    '''
    header_dict = {"Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip,deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Connection": "keep-alive",
                        "Host": "bd.kuwo.cn",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Referer": "http://bd.kuwo.cn/play_detail/%s" % rid,
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                        }
    url = 'http://bd.kuwo.cn/url'
    with requests.get(url=url, params=textmod,  headers=header_dict) as req:
        logger.info("get_a_mp3 url req return code: %d" % req.status_code)
        if req.status_code == 200:
            '''{"code": 200, "msg": "success", "url": "https://sy-sycdn.kuwo.cn/7ffbe63701f7a9558dff2746c9d6e1d8/615aabad/resource/n3/21/42/3886230848.mp3"}'''
            logger.info("response: " + req.content)
            j = json.loads(req.content)
            with requests.get(j['url']) as req2:
                logger.info("get mp3 file req2 return code: %d" % req2.status_code)
                if req2.status_code == 200:
                    with open(os.path.join(outdir, "%s.mp3" % name), "wb") as fd:
                        fd.write(req2.content)
                        logger.info("write mp3 [%s] [%s] ok: " % (name, rid))


def get_a_mp3_211102(name, rid, outdir, aid, token):
    ts, reqId = get_ts_reqid()
    '''mid=70821540&type=music&httpsStatus=1&reqId=0458c400-3b88-11ec-b943-65bd542b6391'''
    textmod = {     "mid": rid,
                    "type": "music",
                    "httpsStatus": "1",
                    "reqId": reqId}
    '''Host: bd.kuwo.cn
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    DNT: 1
    Connection: keep-alive
    Referer: http://bd.kuwo.cn/album_detail/10180760
    Cookie: Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1635820495,1635820593; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1635820659; _ga=GA1.2.93070590.1635820496; _gid=GA1.2.2105674867.1635820496; kw_token=94PDYXF8A3U
    Pragma: no-cache
    Cache-Control: no-cache
    '''
    header_dict = {'Host': 'bd.kuwo.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Referer': 'http://bd.kuwo.cn/album_detail/%s' % aid,
                    'Cookie': 'kw_token=%s' % token,
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                   }
    url = 'http://bd.kuwo.cn/api/v1/www/music/playUrl'
    with requests.get(url=url, params=textmod,  headers=header_dict) as req:
        logger.info("get_a_mp3 url req return code: %d" % req.status_code)
        if req.status_code == 200:
            '''{"code":200,"msg":"success","reqId":"e04e5e12ff4f141a0ac2f00472070e77","data":{"url":"https://se-sycdn.kuwo.cn/f9275cf321bb58d2951e2ad860d7e865/6180a817/resource/n3/26/94/3116241848.mp3"},"profileId":"site","curTime":1635821592048,"success":true}'''
            logger.info(b"response: " + req.content)
            j = json.loads(req.content)
            logger.info("mp3 url: %s" % j['data']['url'])
            with requests.get(j['data']['url']) as req2:
                logger.info("get mp3 file req2 return code: %d" % req2.status_code)
                if req2.status_code == 200:
                    with open(os.path.join(outdir, "%s.mp3" % name), "wb") as fd:
                        fd.write(req2.content)
                        logger.info("write mp3 [%s] [%s] ok: " % (name, rid))


def get_a_album(aid, pn):
    token = '94PDYXF8A3U'
    ts, reqId = get_ts_reqid()
    '''
    albumId: 10180760
    pn: 3
    rn: 30
    httpsStatus: 1
    reqId: 661f1b50-24e8-11ec-bc82-77d9ebcfed0a
    '''
    textmod = {"albumId": aid,
                    "pn": pn,
                    "rn": "30",
                    "httpsStatus": "1",
                    "reqId": reqId}
    '''GET /api/www/album/albumInfo?albumId=10180760&pn=3&rn=30&httpsStatus=1&reqId=661f1b50-24e8-11ec-bc82-77d9ebcfed0a HTTP/1.1
    Host: bd.kuwo.cn
    Connection: keep-alive
    Pragma: no-cache
    Cache-Control: no-cache
    Accept: application/json, text/plain, */*
    csrf: XYKD98DJX7
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36
    Referer: http://bd.kuwo.cn/album_detail/10180760
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: _ga=GA1.2.1124756597.1633243187; _gid=GA1.2.1062990606.1633243187; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1633243187,1633243216,1633271355,1633309840; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1633332141; _gat=1; kw_token=XYKD98DJX7
    '''
    header_dict = {"Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip,deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Connection": "keep-alive",
                        "csrf": token,
                        "Host": "bd.kuwo.cn",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Referer": "http://bd.kuwo.cn/album_detail/%s" % aid,
                        "Cookie": "kw_token=%s" %token,
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                        }
    url = 'http://bd.kuwo.cn/api/www/album/albumInfo'
    with requests.get(url=url, params=textmod,  headers=header_dict) as req:
        logger.info("get_a_album [%s] [%s] return code: %d" % (aid, pn, req.status_code))
        if req.status_code == 200:
            '''
            {"code":200,"curTime":1633334092077,"data":{"playCnt":87651820,"artist":"贝乐虎","releaseDate":"2020-10-14","album":"贝乐虎儿歌","albumid":10180760,"pay":0,"artistid":949949,"pic":"https://img1.kuwo.cn/star/albumcover/300/12/39/1395023375.jpg","isstar":1,"total":116,"content_type":"0","albuminfo":"贝乐虎儿歌，由贝乐虎兄弟和小伙伴们生动、欢快的演绎，传达健康、阳光、积极的亲子育儿理念。让小朋友娱乐之余学习家庭礼貌，获得音乐和节奏的熏陶，寓教于乐。","lang":"国语","musicList":[{"musicrid":"MUSIC_79914371","barrage":"0","artist":"贝乐虎","mvpayinfo":{"play":0,"vid":0,"down":0},"pic":"https://img1.kuwo.cn/star/albumcover/500/12/39/1395023375.jpg","isstar":1,"rid":79914371,"duration":83,"score100":"47","content_type":"0","track":61,"hasLossless":false,"hasmv":0,"releaseDate":"2020-10-14","album":"贝乐虎儿歌","albumid":10180760,"pay":"0","artistid":949949,"albumpic":"https://img1.kuwo.cn/star/albumcover/500/12/39/1395023375.jpg","originalsongtype":0,"songTimeMinutes":"01:23","isListenFee":false,"pic120":"https://img1.kuwo.cn/star/albumcover/120/12/39/1395023375.jpg","name":"小星星","online":1,"payInfo":{"
            '''
            logger.info(b"response: " + req.content)
            j = json.loads(req.content)
            if "code" in j and j['code'] == 200:
                name = j['data']['album']
                with open(os.path.join(outdir, "%s_%s.txt" % (name, pn)), "wb") as fd:
                    fd.write(req.content)
                album_outdir = os.path.join(outdir, name)
                if not os.path.isdir(album_outdir):
                    os.mkdir(album_outdir)
                for index, mp3 in enumerate(j['data']['musicList']):
                    logger.info("To get %s.mp3 [%s/%s] in [%s]:" % (mp3['name'], index+1, len(j['data']['musicList']), name))
                    get_a_mp3_211102(mp3['name'], mp3['rid'], album_outdir, aid, token)


def parse_a_album(url, name):
    with requests.get(url) as req:
        logger.info("get_a_album req return code: %d" % req.status_code)
        if req.status_code == 200:
            bs = BeautifulSoup(req.content, "html.parser")
            ns = bs.find_all(attrs={"class": "name"})
            '''<a class="name" data-v-1344465b="" href="/play_detail/70647080" title="Old MacDo
nald Had a Farm">Old MacDonald Had a Farm</a>'''
            info = map(lambda x: " ".join([x['href'], x['title']]), ns)
            logger.info(info)
            with open(os.path.join(outdir, name), "wb") as fd:
                fd.write("\n".join(info).encode('utf8'))
            for mp3 in ns:
                get_a_mp3(mp3['title'], mp3['href'].replace("/play_detail/", ''), outdir)


def get_pages(aid):
    with requests.get("http://bd.kuwo.cn/album_detail/%s"%aid) as req:
        logger.info("get_pages req return code: %d" % req.status_code)
        if req.status_code == 200:
            bs = BeautifulSoup(req.content, "html.parser")
            ns = bs.find_all('ul', attrs={'class': 'flex_c', 'data-v-1344465b': None})
            '''[<ul class="flex_c" data-v-9fcc0c74=""><li data-v-9fcc0c74="" style="background:
            #FFDF1F;"><span class="notCursor currentPage" data-v-9fcc0c74="">1</span></li><l
            i data-v-9fcc0c74=""><span data-v-9fcc0c74="">2</span></li><li data-v-9fcc0c74="
            "><span data-v-9fcc0c74="">3</span></li><li data-v-9fcc0c74=""><span data-v-9fcc
            0c74="">4</span></li></ul>]
            '''
            logger.info("pages info1: %s" % ns)
            if len(ns) == 1:
                lis = ns[0].find_all('span')
                logger.info("pages info2: %s" % lis)
                return len(lis)
    logger.info("pages return default value 1")
    return 1


def get_album():
    #aid=20092293
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    #get_a_mp3(u"两只老虎", 79914233)
    #parse_a_album("http://bd.kuwo.cn/album_detail/10180760", u"贝乐虎儿歌")
    for aid in (10180760,):
        pages = get_pages(aid)
        for p in range(pages):
            logger.info("[Album %s][Page %s/%s]:" % (aid, p+1, pages))
            get_a_album(aid, p+1)


def get_file():
    rids=[
           [574584, u"欢乐颂"],
           ]
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    # get_a_mp3(u"两只老虎", 28861525)
    for rid in rids:
        get_a_mp3(rid[1], rid[0], outdir)


if __name__ == "__main__":
    setup_logging()
    outdir = r"I:\temp\xx\child_songs"
    if 1:
        get_file()
    else:
        get_album()