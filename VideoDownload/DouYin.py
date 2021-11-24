# -*- coding:utf-8 -*-
import requests
import time
import re
import string
import hashlib
import pprint
import traceback
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

sensitive_words = {
    u'断桥残雪': 'dqcx',
    u'中国医生': 'zgys',
    u'偷拍': 'tp',
}
MAX_NAME_LEN = 108


def walk_a_dir(d):
    return [x for x in os.listdir(d) if x.endswith('.mp4')]


def get_good_name(s, get_file=True):
    replace_char = '-'
    res = []
    if not get_file:
        s = s[:max(min(s.find('('), s.find('（')), len(s))]
    for ch in s:
            if u'\u4e00' <= ch <= u'\u9fff' or ch in string.printable[:62]+'_-.':
                res.append(ch)
            elif get_file and res and res[-1] != replace_char:
                res.append(replace_char)
    ret = ''.join(res).strip('_-')
    for k in sensitive_words:
        ret = ret.replace(k, sensitive_words[k])
    if len(ret) > MAX_NAME_LEN:
        ret = ret[:MAX_NAME_LEN]
    return ret


def get_last_time(d, d2):
    res = d2
    for f in walk_a_dir(d):
        st = os.stat(os.path.join(d, f))
        if res < st.st_mtime * 1000:
            res = st.st_mtime * 1000
    return res


def remove_dup(d):
    md5s = {}
    stats = {}
    for f in walk_a_dir(d):
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

def format_year_month(y, m):
    return '%04d-%02d-01 00:00:00' % (y, m)
    
def string_time_to_msec(s):
    return int(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")) * 1000)

def download_one2(input_s):
    now_t = time.localtime(time.time())
    now_t2 = int(time.mktime(now_t) * 1000)
    year = list(range(2018, now_t.tm_year+1))
    month = list(range(1, 13))
    input_url = 'https://v.douyin.com/%s/' %  input_s
    logger.info(input_url)
    req_start_page = requests.get(url=input_url, headers=headers, allow_redirects=False)
    if req_start_page.status_code != 302:
        logger.error('get start page failed! [%s][%s]' % (input_url, req_start_page))
        return
    location = req_start_page.headers['location']
    logger.info(location)
    sec_uid = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', location, re.M | re.I)[0]
    logger.info(sec_uid)
    req_name = requests.get(url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                           headers=headers)
    if req_name.status_code != 200:
        logger.error('get name failed! [%s][%s]' % (req_name.url, req_name))
        return
    user_info = json.loads(req_name.text)
    logger.info(user_info)
    uid = user_info['user_info']['uid']
    if uid in dir_uid_map:
        name = dir_uid_map[uid]['name']
        if input_s not in dir_uid_map[uid]['shorturl']:
            dir_uid_map[uid]['shorturl'].append(input_s)
            logger.error('uid [%s] to dual short: [%s]' % (uid, dir_uid_map[uid]['shorturl']))
    else:
        name = user_info['user_info']['nickname']
        logger.info(name)
        name = get_good_name(name, False)
        dir_uid_map[uid] = user_info['user_info']
        dir_uid_map[uid]['name'] = name
        dir_uid_map[uid]['shorturl'] = [input_s]
    logger.info(name)
    #return
    #all_dir = os.listdir(outdir)
    #may_be_dir = list(filter(lambda x: x.startswith(name), all_dir))
    #if len(may_be_dir):
        #logger.info(pprint.pformat(may_be_dir))
        #name = may_be_dir[0]
    out_dir_anchor = os.path.join(outdir, name)
    last_time = string_time_to_msec(format_year_month(year[0], month[0]))
    vn = 0
    if not os.path.exists(out_dir_anchor):
        os.mkdir(out_dir_anchor)
    else:
        logger.info('directory exist')
        #last_time = get_last_time(out_dir_anchor, last_time)
        vn = len(walk_a_dir(out_dir_anchor))
    md5s, stats = remove_dup(out_dir_anchor)
    if stats:
        last_time = max(max(map(lambda x: x.st_mtime * 1000, stats.values())), last_time)
    time_pool = [format_year_month(x, y) for x in year for y in month]
    time_pool.append(format_year_month(year[-1]+1, month[-1]))
    logger.info(time_pool)
    k = len(time_pool)
    for i in range(k):
        if i < k - 1:
            t1 = string_time_to_msec(time_pool[i])
            t2 = string_time_to_msec(time_pool[i + 1])
            if last_time >= t2:
                continue
            elif last_time > t1:
                t1 = last_time
            logger.info("begin time=%s[%s], end time=%s[%s]" %(time_pool[i], t1, time_pool[i + 1], t2))
            params = {
                'sec_uid': sec_uid,
                'count': 200,
                'min_cursor': t1,
                'max_cursor': t2,
                'aid': 1128,
                '_signature': 'PtCNCgAAXljWCq93QOKsFT7QjR'
            }
            list_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/'
            req = requests.get(url=list_url, params=params, headers=headers)
            logger.info(req)
            if req.status_code != 200:
                logger.error("get list error: [%s][%s][%s][%s]" % (name, input_s, list_url, params))
                return
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
                logger.info(input_url)
                logger.info(b'%s ===>downloading' % videotitle.encode('utf8'))
                try:
                    with requests.get(url=videourl, headers=headers) as req2:
                        logger.info(req2)
                        if req2.status_code == 200:
                            md5 = hashlib.md5(req2.content).hexdigest()
                            if md5 not in md5s:
                                vn += 1
                                vf = '%s_%s.mp4' % (vn, videotitle)
                                vfile = os.path.join(out_dir_anchor, vf)
                                with open(vfile, 'wb') as v:
                                    v.write(req2.content)
                                md5s[md5] = vf
                                news.append(vfile)
                            else:
                                logger.warning("skip same file [%s][%s]"%(md5s[md5], md5))
                except Exception as e:
                    logger.error('download error: %s' % e)
                    logger.error(traceback.format_exc())
            if t1 < now_t2 <= t2:
                break
    if name not in checked2:
        checked2[name] = input_s
    else:
        dup2.append((name, input_s, checked2[name]))


def download_one(s):
    over = False
    t = 60 * 5
    while not over:
        try:
            download_one2(s)
            #break
            over = True
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            time.sleep(t)
            t += 60 * 5


if __name__ == "__main__":
    setup_logging()
    outdir = r'E:\hzw\DouYin'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    shorturls = [
        "RVkk72M",
        "RVkh8L5",
        "RVk89Cs",
        "RVkd6UH",
        "RVBY8Ne",
        "RVBDCTn",
        "RVB6Nkn",
        "RVBM796",
        #"RVB8K2G",
        "RVBJjLp",
        "RVB2xpN",
        "RVBkjaw",
        "RVBNaP3",
        "RVBjTVY",
        "RVBk6mA",
        #"RVBATWa",
        "RVBAAFe",
        "RVB6cS1",
        #'RaxaW6R',
        #'RaxHDpn',
        #'RaxfjKB',
        'RaxBbbG',
        'RaxFW11',
        'RaxmCoH',
        'Rax54AY',
        'Raxjtmg',
        'RaxUXeJ',
        'Raxk3kC',
        'RaxtXmA',
        'RaxpMLK',
    "RfesPp3",
    "Rfd2n3x",
    "RfdFLTv",
    "RfdtdVk",
    "RfRJQ5U",
    "RfRJqm1",
    "RfdwbdX",
    "Rfd3sSV",
    #"RfdpAde",
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
    #'RBET8HL',
    'RBE9xXq',
    'RBEq3GS',
    'RBE4S8k',
    'RBEEvE8',
    'RBEGeek',
    'RBEsxgN',
    'RBEsF3Q',
    'RBEp8jK',
    #'RBEgng4',
    'RBEvLK7',
    'RBEWW7t',
    'RBE4kfx',
    'RBE7us1',
    #'RBEptSn',
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
    'RyBAG3r',
    'RyBAG7w',
    'RyBG1SP',
    'RyBU9yB',
    'RyBaoCY',
    #'RyByhFm',
    #'RyBpBha',
    #'RyBm48U',
    ]
    #shorturls = ['Rh7G7kx']
    checked = set()
    checked2 = {}
    dup1 = []
    dup2 = []
    news = []
    dir_uid_map = {}
    dir_uid_file = os.path.join(outdir, 'user_info.json')
    if os.path.isfile(dir_uid_file):
        dir_uid_fd = open(dir_uid_file, 'r')
        dir_uid_map = json.load(dir_uid_fd)
        dir_uid_fd.close()
    begin_t = time.time()
    for short_url in shorturls:
        if short_url not in checked:
            download_one(short_url)
            checked.add(short_url)
            #break
        else:
            dup1.append(short_url)
    dir_uid_fd = open(dir_uid_file, 'w')
    json.dump(dir_uid_map, dir_uid_fd)
    dir_uid_fd.close()
    logger.info(pprint.pformat(dup1))
    logger.info(pprint.pformat(dup2))
    logger.info(pprint.pformat(news))
    logger.info(len(news))
    end_t = time.time()
    logger.info("time cost: %s seconds" % (end_t - begin_t))
