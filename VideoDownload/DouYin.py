# -*- coding:utf-8 -*-
import requests
import json
import os
import time
import re
import string
import hashlib
import pprint
from Util.myLogging import *


"""
params = {
    'sec_uid' : 'MS4wLjABAAAAbtSlJK_BfUcuqyy8ypNouqEH7outUXePTYEcAIpY9rk',
    'count' : '200',
    'min_cursor' : '1612108800000',
    'max_cursor' : '1619251716404',
    'aid' : '1128',
    '_signature' : 'PtCNCgAAXljWCq93QOKsFT7QjR'
}
"""
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"
}


def get_good_name(s, get_file=True):
    replace_char = '-'
    res = []
    if not get_file:
        s = s[:max(min(s.find('('), s.find('（')), 0)]
    for ch in s:
            if u'\u4e00' <= ch <= u'\u9fff' or ch in string.printable[:62]+'_-.':
                res.append(ch)
            elif get_file and res and res[-1] != replace_char:
                res.append(replace_char)
    return ''.join(res).strip('_-')


def get_last_time(d, d2):
    res = d2
    for f in os.listdir(d):
        st = os.stat(os.path.join(d, f))
        if res < st.st_mtime * 1000:
            res = st.st_mtime * 1000
    return res


def remove_dup(d):
    md5s = {}
    stats = {}
    for f in os.listdir(d):
        fp = os.path.join(d, f)
        with open(fp, 'rb') as fd:
            md5 = hashlib.md5(fd.read()).hexdigest()
            st1 = os.stat(os.path.join(d, f))
            if md5 in md5s:
                st2 = stats[md5s[md5]]
                if st1.st_mtime < st2.st_mtime:
                    del stats[md5s[md5]]
                    os.unlink(os.path.join(d, md5s[md5]))
                    logger.info("remove [%s] in [%s]" % (md5s[md5], d))
                    md5s[md5] = f
                    stats[f] = st1
                else:
                    fd.close()
                    os.unlink(os.path.join(d, f))
                    logger.info("remove [%s] in [%s]" % (f, d))
            else:
                md5s[md5] = f
                stats[f] = st1
    return md5s, stats


def reorder(d, stats):
    fs = list(stats.keys())
    fs.sort(key=lambda x: stats[x].st_mtime)
    for i, f in enumerate(fs):
        f2 = re.sub('^\d+_', '', f)
        f2 = "%s_%s" % (i+1, f2)
        if f != f2:
            os.rename(os.path.join(d, f), os.path.join(d, f2))
            logger.info("rename in [%s]\n%s\n%s" % (d, f, f2))


def download_one2(string):
    now_t = time.localtime(time.time())
    now_t2 = int(time.mktime(now_t) * 1000)
    year = list(map(lambda yi: "%04d" % yi, range(2018, now_t.tm_year+1)))
    month = list(map(lambda mo: "%02d" % mo, range(1, 13)))
    shroturl = re.findall('[a-z]+://[\S]+', string, re.I | re.M)[0]
    logger.info(shroturl)
    startpage = requests.get(url=shroturl, headers=headers, allow_redirects=False)
    location = startpage.headers['location']
    logger.info(location)
    sec_uid = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', location, re.M | re.I)[0]
    logger.info(sec_uid)
    getname = requests.get(url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                           headers=headers).text
    userinfo = json.loads(getname)
    logger.info(userinfo)
    name = userinfo['user_info']['nickname']
    logger.info(name)
    name = get_good_name(name, False)
    logger.info(name)
    all_dir = os.listdir(outdir)
    may_be_dir = list(filter(lambda x: x.startswith(name), all_dir))
    if len(may_be_dir):
        #pprint.pprint(may_be_dir)
        logger.info(pprint.pformat(may_be_dir))
        name = may_be_dir[0]
    outdir2 = os.path.join(outdir, name)
    last_time = int(time.mktime(time.strptime(year[0] + '-' + month[0] + '-01 00:00:00', "%Y-%m-%d %H:%M:%S")) * 1000)
    vn = 0
    if not os.path.exists(outdir2):
        os.mkdir(outdir2)
    else:
        logger.info('directory exist')
        last_time = get_last_time(outdir2, last_time)
        vn = len(list(filter(lambda x: x.endswith('.mp4'), os.listdir(outdir2))))
    md5s, stats = remove_dup(outdir2)
    timepool = [x + '-' + y + '-01 00:00:00' for x in year for y in month]
    logger.info(timepool)
    k = len(timepool)
    for i in range(k):
        if i < k - 1:
            logger.info('begintime=' + timepool[i])
            logger.info('endtime=' + timepool[i + 1])
            beginarray = time.strptime(timepool[i], "%Y-%m-%d %H:%M:%S")
            endarray = time.strptime(timepool[i + 1], "%Y-%m-%d %H:%M:%S")
            t1 = int(time.mktime(beginarray) * 1000)
            t2 = int(time.mktime(endarray) * 1000)
            if last_time >= t2:
                continue
            elif last_time > t1:
                t1 = last_time
            logger.info(t1, t2)
            params = {
                'sec_uid': sec_uid,
                'count': 200,
                'min_cursor': t1,
                'max_cursor': t2,
                'aid': 1128,
                '_signature': 'PtCNCgAAXljWCq93QOKsFT7QjR'
            }
            awemeurl = 'https://www.iesdouyin.com/web/api/v2/aweme/post/'
            req = requests.get(url=awemeurl, params=params, headers=headers)
            logger.info(req)
            if req.status_code != 200:
                exit(1)
            data = json.loads(req.content)
            logger.info(data)
            # logger.info(type(data))
            awemenum = len(data['aweme_list'])
            logger.info(awemenum)
            for i in list(range(awemenum))[::-1]:
                videotitle = data['aweme_list'][i]['desc'].replace("?", "").replace("\"", "").replace(":", "")
                #videotitle = re.sub('[| ;,:?()*^.]', '-', videotitle)
                videotitle = get_good_name(videotitle)
                videourl = data['aweme_list'][i]['video']['play_addr']['url_list'][0]
                logger.info(videotitle)
                logger.info(videourl)
                #start = time.time()
                logger.info(shroturl)
                logger.info(b'%s ===>downloading' % videotitle.encode('utf8'))
                try:
                    with requests.get(url=videourl, headers=headers) as req2:
                        logger.info(req2)
                        if req2.status_code == 200:
                            md5 = hashlib.md5(req2.content).hexdigest()
                            if md5 not in md5s:
                                vn += 1
                                vf = '%s_%s.mp4' % (vn, videotitle)
                                vfile = os.path.join(outdir2, vf)
                                with open(vfile, 'wb') as v:
                                    v.write(req2.content)
                                md5s[md5] = vf
                            else:
                                logger.info("skip same file [%s][%s]"%(md5s[md5], md5))
                except Exception as e:
                    logger.info(e)
                    logger.info('download error')
            if t1 < now_t2 <= t2:
                break


def download_one(s):
    over = False
    t = 60 * 5
    while not over:
        try:
            download_one2(s)
            over = True
        except Exception as e:
            logger.info(e)
            time.sleep(t)
            t += 60 * 5


if __name__ == "__main__":
    setup_logging()
    outdir = r'E:\hzw\DouYin'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    shorturls = [
    "RfesPp3",
    "Rfd2n3x",
    "RfdFLTv",
    "RfdtdVk",
    "RfRJQ5U",
    "RfRJqm1",
    "RfdwbdX",
    "Rfd3sSV",
    "RfdpAde",
    "Rfdq5L1",
    "RfdqWKa",
    "RfdvCLX",
    "RfdVYro",
    "RfdCSDk",
    "RfdWdAe",
    "RfRJcX8",
    "Rfd4M7N",
    "RfReCE6",
    "RfdnUVS",
    "RfRSRMr",
    'RhnwkwN',
    'RhW2j6g',
    'RhWjYvW',
    'RhW1MSY',
    'RhWdXaN',
    'Rh7Ab8R',
    'Rh765QE',
    'Rh7uy2P',
    'Rh74BWN',
    'Rh7yvqV',
    'Rh7ySdt',
    'Rh7MBUW',
    'Rh7jG5r',
    'Rh7nAw3',
    'Rh7vTt3',
    'Rh7wKqU',
    'Rh7GVRj',
    'Rhv1pUt',
    'Rh7TQQY',
    'Rh7tWfR',
    'Rh7GN8h',
    'Rh7EGmE',
    'Rh7gUvQ',
    'Rh7nt9r',
    'Rhvechf',
    'RhvdaSW',
    'Rh77Pvp',
    'Rh7G7kx',
    'Rh7KFcx',
    'Rh7GFw8',
    'RBKfm4E',
    'RBKA3Ge',
    'RBK2nXK',
    'RBKB9B6',
    'RBKAGM9',
    'RBKCK6J',
    'RBK2Ltf',
    'RBKpvpe',
    'RBKVD6q',
    'RBKnYsM',
    'RBKv3xb',
    'RBKGYXP',
    'RBK7xeo',
    'RBKWwjp',
    'RBE1HVY',
    'RBKt2p6',
    'RBKvnVJ',
    'RBKnWhQ',
    'RBKWPdX',
    'RBKEwqM',
    'RBKwFHu',
    'RBEd9DP',
    'RBEdQSu',
    'RBEkWb5',
    'RBEhBSQ',
    'RBEhD5p',
    'RBE2uJA',
    'RBE6hBe',
    'RBEULcY',
    'RBE5UQy',
    'RBE8jU5',
    'RBEhV6q',
    'RBEH6Kw',
    'RBEaDWY',
    'RBEFWxj',
    'RBEjb9Q',
    'RBE8KPo',
    'RBENLvA',
    'RBESPcM',
    'RBEmbNf',
    'RBEmxL3',
    'RBE85aE',
    'RBEyuRW',
    'RBE4vXr',
    'RBE4CJj',
    'RBET8HL',
    'RBE9xXq',
    'RBEq3GS',
    'RBE4S8k',
    'RBEEvE8',
    'RBEGeek',
    'RBEsxgN',
    'RBEsF3Q',
    'RBEp8jK',
    'RBEgng4',
    'RBEvLK7',
    'RBEWW7t',
    'RBE4kfx',
    'RBE7us1',
    'RBEptSn',
    'RBEvKtY',
    'RBEELEf',
    'RBE7FXw',
    'RU235da',
    'RU2bFHG',
    'RU2CHbY',
    'RU2GUJ8',
    'RU2GEqU',
    'RU2HYqn',
    'RU2HTsf',
    'RU2QnS5',
    'RU2xjkx',
    'RU2p2yx',
    'RU2npsc',
    'RU24F19',
    'RU2aEm4',
    'RU2HoUg',
    'RU2bRWT',
    'RU2TpPH',
    'RU2ngN8',
    'RU2ghLf',
    'RU24noy',
    'RU2vV1V',
    'RU29Pwe',
    'RU2Xa7f',
    'RU2tbRS',
    'RU2GTKH',
    'RU2chuL',
    'RU2GcFj',
    'RU2C8ev',
    'RU2sSro',
    'RU2cg3m',
    'RU2uXXE',
    'RU2vcer',
    'RU2pGJu',
    'RU2afF1',
    'RU2smNa',
    'RU2C9mw',
    'RU2VyQw',
    'RU2anj9',
    'RU2GbML',
    'RU2qPfB',
    'RU2bpoC',
    'RU2H3HL',
    'RU2Xmeb',
    'RyBgY7e',
    'RyB9gNG',
    'RyBtGVJ',
    'RyBtGVJ',
    'RyBAG3r',
    'RyBAG7w',
    'RyBG1SP',
    'RyBU9yB',
    'RyBaoCY',
    'RyByhFm',
    'RyBpBha',
    'RyBm48U',
    ]
    shorturls2 = set(shorturls)
    for shorturl in shorturls2:
        download_one('https://v.douyin.com/%s/' % shorturl)