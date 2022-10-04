# -*- coding:utf-8 -*-
import requests
import time
import re
import string
import hashlib
import pprint
import traceback
from apscheduler.schedulers.blocking import BlockingScheduler
from Util.myLogging import *
from pypinyin import lazy_pinyin


"""
# mp42gif: for f in *mp4; do ffmpeg -i "$f" -s 272x480 -b:v 200k -r 15 $i.gif; i=$((i+1)); done
params = {
    'sec_uid' : 'MS4wLjABAAAAbtSlJK_BfUcuqyy8ypNouqEH7outUXePTYEcAIpY9rk',
    'count' : '200',
    'min_cursor' : '1612108800000',
    'max_cursor' : '1619251716404',
    'aid' : '1128',
    '_signature' : 'PtCNCgAAXljWCq93QOKsFT7QjR'
}

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"
}

sensitive_words = [
    u'断桥残雪',
    u'中国医生',
    u'偷',
    u'露',
    u'车',
    u'拍',
    u'女',
]
MAX_NAME_LEN = 80
"""

num_dict={"0":u"零","1":u"一","2":u"二","3":u"三","4":u"四","5":u"五","6":u"六","7":u"七", "8": "八", "9": "九"}

class DouYin:
    def __init__(self, jconf=None):
        if jconf:
            self.jconf = os.path.join('Conf', jconf)
        else:
            self.jconf = os.path.join('Conf', 'douyin.json')
        self.reload()

    def reload(self):
        with open(self.jconf, 'r') as fjconf:
            self.conf = json.load(fjconf)
        self.outdir = self.conf['outdir']
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        self.shorturls = self.conf['shorturls']
        self.checked = set()
        self.checked2 = {}
        self.dup1 = []
        self.dup2 = []
        self.news = []
        self.newsid = []
        self.dir_uid_map = {}
        user_info_json = self.conf['user_info_json']
        self.dir_uid_file = os.path.join(self.outdir, user_info_json)
        if os.path.isfile(self.dir_uid_file):
            dir_uid_fd = open(self.dir_uid_file, 'r')
            self.dir_uid_map = json.load(dir_uid_fd)
            dir_uid_fd.close()
        self.dir_names = {}
        list(map(lambda x: self.dir_names.update({self.dir_uid_map[x]['name']:x}), self.dir_uid_map))
        self.update_url_name_map()

    def get_req(self, url, **kwargs):
        retry = self.conf['request_retry']
        req = None
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.conf['request_timeout']
        while retry > 0:
            try:
                req = requests.get(url, **kwargs)
            except Exception as e:
                logger.info("Exception in req [%s]: %s" % (url, e))
            finally:
                retry -= 1
            if req:
                # logger.info(dir(req))
                if req.status_code == 200:
                    break
        return req

    def walk_a_dir(self, d):
        return [x for x in os.listdir(d) if x.endswith('.mp4') or x.endswith('.jpg')]

    def replace_sensitive(self, s, k):
        s1 = s.replace(k, "".join(lazy_pinyin(k)))
        #if s1.find('69') != -1:
        #    s1 = s1.replace('69', 'liujiu')
        return s1


    def get_good_name(self, s, get_file=True):
        '''⒈CJK扩充集A 3400→4DB5
        ⒉康熙字典214部首 2F00→2FD5
        ⒊CJK部首扩充 2E80→2EF3
        ⒋汉字结构符 2FF0→2FF8
        ⒌藏文 0F00→0FCF
        ⒍彝文 A000→A4C6
        ⒎蒙文 1800→18A9
        8. CJK Unified Ideographs  4E00→9FA5
        '''
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
        for k in self.conf['sensitive_words']:
            ret = self.replace_sensitive(ret, k)
        if len(ret) > self.conf['MAX_NAME_LEN']:
            ret = ret[:self.conf['MAX_NAME_LEN']-4] + ret[len(ret)-4:]
        return ret

    def get_last_time(self, d, d2):
        res = d2
        for f in self.walk_a_dir(d):
            st = os.stat(os.path.join(d, f))
            if res < st.st_mtime * 1000:
                res = st.st_mtime * 1000
        return res

    def remove_mp3(self, d):
        logger.debug("enter remove_mp3")
        for f in os.listdir(d):
            if f.endswith('.mp4'):
                fp = os.path.join(d, f)
                fo = os.popen('avconv -i %s 2>&1|grep -c "Stream #"' % fp)
                sn = fo.read()
                fo.close()
                if sn.strip() == "1":
                    os.unlink(fp)
                    logger.info("To remove a mp3 file [%s]" % fp)

    def remove_dup(self, d):
        logger.debug("enter remove_dup")
        md5s = {}
        stats = {}
        for f in self.walk_a_dir(d):
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

    def reorder(self, d, stats):
        logger.debug("enter reorder")
        fs = list(stats.keys())
        fs.sort(key=lambda x: stats[x].st_mtime)
        last_num = "-1"
        i = 0
        for f in fs:
            new_num = f[:f.find('_')]
            f2 = re.sub('^\d+_', '', f)
            if last_num != new_num or f.endswith('.mp4'):
                i += 1
            f2 = "%s_%s" % (i, f2)
            if f != f2:
                same_num = 2
                t = os.path.splitext(f2)
                while os.path.isfile(os.path.join(d, f2)):
                    f2 = "%s_%s%s" % (t[0], same_num, t[1])
                    same_num += 1
                os.rename(os.path.join(d, f), os.path.join(d, f2))
                logger.info("rename in [%s]\n%s\n%s" % (d, f, f2))
            last_num = new_num
        return i

    def format_year_month(self, y, m):
        return '%04d-%02d-01 00:00:00' % (y, m)

    def string_time_to_msec(self, s):
        return int(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")) * 1000)

    def get_jpgs(self, aid, name):
        vfs = []
        url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s' % aid
        r = self.get_req(url, headers=self.conf['headers'])
        num = 1
        if r.status_code == 200:
            j = json.loads(r.content)
            for item in j['item_list']:
                for im in item['images']:
                    durls = list(filter(lambda x: x.count('jpeg?'), im['url_list']))
                    vfs.append((durls[0] if durls else im['url_list'][0], "%s_%s.jpg" % (name, num)))
                    num += 1
        return vfs

    def get_sec(self, input_s):
        input_url = 'https://v.douyin.com/%s/' %  input_s
        req_start_page = self.get_req(url=input_url, headers=self.conf['headers'], allow_redirects=False)
        location = req_start_page.headers['location']
        s = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', location, re.M | re.I)[0]
        print(s)
        return s

    def download_one2(self, input_s):
        now_t = time.localtime(time.time())
        now_t2 = int(time.mktime(now_t) * 1000)
        year = list(range(2018, now_t.tm_year+1))
        month = list(range(1, 13))
        is_sec_uid = len(input_s) != 7
        if is_sec_uid:
            sec_uid = input_s
            input_url = input_s
        else:
            input_url = 'https://v.douyin.com/%s/' %  input_s
            logger.info(input_url)
            req_start_page = self.get_req(url=input_url, headers=self.conf['headers'], allow_redirects=False)
            if req_start_page.status_code != 302:
                logger.error('get start page failed! [%s][%s]' % (input_url, req_start_page))
                return
            location = req_start_page.headers['location']
            logger.info(location)
            sec_uid = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', location, re.M | re.I)[0]
        logger.info(sec_uid)
        req_name = self.get_req(url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                               headers=self.conf['headers'])
        if req_name.status_code != 200:
            logger.error('get name failed! [%s][%s]' % (req_name.url, req_name))
            return
        user_info = json.loads(req_name.text)
        logger.info(user_info)
        uid = user_info['user_info']['uid']
        if uid in self.dir_uid_map:
            name = self.dir_uid_map[uid]['name']
            if not ''.join(filter(lambda ch: u'\u4e00' <= ch <= u'\u9fff' or ch in string.printable[:62], name)):
                name = uid
                self.dir_uid_map[uid]['name'] = uid
            for su in self.dir_uid_map[uid]['shorturl']:
                if su not in self.shorturls:
                    self.dir_uid_map[uid]['shorturl'].remove(su)
            if input_s not in self.dir_uid_map[uid]['shorturl']:
                self.dir_uid_map[uid]['shorturl'].append(input_s)
                logger.error('uid [%s] to dual short: [%s]' % (uid, self.dir_uid_map[uid]['shorturl']))
            if 'sec_uid' not in self.dir_uid_map[uid]:
                self.dir_uid_map[uid]['sec_uid'] = sec_uid
            elif sec_uid != self.dir_uid_map[uid]['sec_uid']:
                logger.error("sec id diff! [%s][%s][%s], old: [%s], new: [%s]" %
                             (uid, name, input_s, self.dir_uid_map[uid]['sec_uid'], sec_uid))
        else:
            name = user_info['user_info']['nickname']
            logger.info(name)
            name = self.get_good_name(name, False)
            if not ''.join(filter(lambda ch: u'\u4e00' <= ch <= u'\u9fff' or ch in string.printable[:62], name)):
                name = uid
            same_num = 2
            origin_good_name = name
            while name in self.dir_names and self.dir_names[name] != uid:
                name = "%s_%s" % (origin_good_name, same_num)
                same_num += 1
            self.dir_names[name] = uid
            self.dir_uid_map[uid] = user_info['user_info']
            self.dir_uid_map[uid]['name'] = name
            self.dir_uid_map[uid]['shorturl'] = [input_s]
            self.dir_uid_map[uid]['sec_uid'] = sec_uid
        logger.info(name)
        #return
        #all_dir = os.listdir(outdir)
        #may_be_dir = list(filter(lambda x: x.startswith(name), all_dir))
        #if len(may_be_dir):
            #logger.info(pprint.pformat(may_be_dir))
            #name = may_be_dir[0]
        out_dir_anchor = os.path.join(self.outdir, name)
        last_time = self.string_time_to_msec(self.format_year_month(year[0], month[0]))
        #vn = 0
        if not os.path.exists(out_dir_anchor):
            os.mkdir(out_dir_anchor)
        else:
            logger.info('directory exist')
            #last_time = get_last_time(out_dir_anchor, last_time)
            #vn = len(walk_a_dir(out_dir_anchor))
        if self.conf['remove_mp3']:
            self.remove_mp3(out_dir_anchor)
        md5s, stats = self.remove_dup(out_dir_anchor)
        vn = self.reorder(out_dir_anchor, stats) + 1
        #vn = max(map(lambda x: int(x[:x.find('_')]), stats.keys()))
        if stats and not self.conf['check_all']:
            last_time = max(max(map(lambda x: x.st_mtime * 1000, stats.values())), last_time)
        self.dir_uid_map[uid]['last_last_time'] = last_time
        self.dir_uid_map[uid]['last_total_count'] = len(stats)
        time_pool = [self.format_year_month(x, y) for x in year for y in month]
        time_pool.append(self.format_year_month(year[-1]+1, month[0]))
        logger.info(time_pool)
        k = len(time_pool)
        logger.info('begin download videos')
        for i in range(k):
            if i < k - 1:
                t1 = self.string_time_to_msec(time_pool[i])
                t2 = self.string_time_to_msec(time_pool[i + 1])
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
                req = self.get_req(url=list_url, params=params, headers=self.conf['headers'])
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
                    try:
                        videotitle = data['aweme_list'][i]['desc'].replace("?", "").replace("\"", "").replace(":", "")
                        #videotitle = re.sub('[| ;,:?()*^.]', '-', videotitle)
                        videotitle = self.get_good_name(videotitle)
                        videourl = data['aweme_list'][i]['video']['play_addr']['url_list'][0]
                        logger.info(videotitle)
                        logger.info(videourl)
                        #start = time.time()
                        logger.info('%s %s' % (input_url, user_info['user_info']['nickname']))
                        logger.info(b'%s ===>downloading' % videotitle.encode('utf8'))
                        vfs =[]
                        if not data['aweme_list'][i]['video']['vid'].strip():
                            vfs = self.get_jpgs(data['aweme_list'][i]['aweme_id'], "%s_%s" % (vn, videotitle))
                            #vfs.append((data['aweme_list'][i]['video']['cover']['url_list'][0], '%s_%s_cover.jpg' % (vn, videotitle)))
                            #vfs.append((data['aweme_list'][i]['video']['origin_cover']['url_list'][0], '%s_%s_origin_cover.jpg' % (vn, videotitle)))
                        else:
                            vfs.append((videourl, '%s_%s.mp4' % (vn, videotitle)))
                        skipped = True
                        for vf in vfs:
                            with self.get_req(url=vf[0], headers=self.conf['headers']) as req2:
                                logger.info(req2)
                                if req2.status_code == 200:
                                    md5 = hashlib.md5(req2.content).hexdigest()
                                    if md5 not in md5s:
                                        vfile = os.path.join(out_dir_anchor, vf[1])
                                        with open(vfile, 'wb') as v:
                                            v.write(req2.content)
                                        md5s[md5] = vf[1]
                                        self.news.append(vfile)
                                        if name not in self.newsid:
                                            self.newsid.append(name)
                                        skipped = False
                                    else:
                                        logger.warning("skip same file [%s][%s]"%(md5s[md5], md5))
                        if not skipped:
                            vn += 1
                    except Exception as e:
                        logger.error('download error: %s' % e)
                        logger.error(traceback.format_exc())
                if t1 < now_t2 <= t2:
                    break
        if name not in self.checked2:
            self.checked2[name] = input_s
        else:
            self.dup2.append((name, input_s, self.checked2[name]))

    def download_one(self, s):
        over = False
        t = 60 * 5
        while not over:
            try:
                self.download_one2(s)
                #break
                over = True
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                time.sleep(t)
                t += 60 * 5

    def update_url_name_map(self):
        f = os.path.join(self.outdir, self.conf['url_name_map'])
        fd = open(f, 'wb')
        outs = []
        for url in self.shorturls:
            for k in self.dir_uid_map:
                if self.dir_uid_map[k]['shorturl'][0] == url:
                    outs.append('%s %s %s %s' % (url, self.dir_uid_map[k]['name'], self.dir_uid_map[k]['nickname'],
                       self.dir_uid_map[k]['sec_uid'] if "sec_uid" in self.dir_uid_map[k] else ""))
                    break
        fd.write('\n'.join(outs).encode('utf8'))
        fd.close()

    def do_work(self):
        self.reload()
        #exit(0)
        begin_t = time.time()
        shorturls = self.shorturls
        if "first_several_only" in self.conf and self.conf["first_several_only"]:
            shorturls = self.shorturls[:self.conf["first_several_only"]]
        for short_url in shorturls:
            if short_url not in self.checked:
                self.download_one(short_url)
                self.checked.add(short_url)
                #break
            else:
                self.dup1.append(short_url)
        dir_uid_fd = open(self.dir_uid_file, 'w')
        json.dump(self.dir_uid_map, dir_uid_fd)
        dir_uid_fd.close()
        self.update_url_name_map()
        logger.info(pprint.pformat(self.news))
        logger.info(len(self.news))
        logger.info(self.newsid)
        logger.info("%s/%s" % (len(self.newsid), len(shorturls)))
        logger.info(pprint.pformat(self.dup1))
        logger.info(pprint.pformat(self.dup2))
        end_t = time.time()
        logger.info("time cost: %s seconds" % (end_t - begin_t))

    def get_file_type(self, f):
        fd = open(f, 'rb')
        buf = fd.read(8)
        fd.close()
        if buf[4:] != b'ftyp':
            return '.jpg'
        else:
            return '.mp4'

    def check_sensitive(self):
        num_dict2 = {}
        for k in num_dict:
            num_dict2[num_dict[k]] = k
        self.outdir = self.conf['outdir']
        logger.debug("enter check_sensitive")
        for d in os.listdir(self.outdir):
            logger.debug("enter %s" % d)
            outdir = os.path.join(self.outdir, d)
            if os.path.isdir(outdir):
                for f in os.listdir(outdir):
                    logger.debug("check %s" % f)
                    fp = os.path.join(outdir, f)
                    if os.path.isfile(fp):
                        #new_name = "".join(map(lambda x: num_dict2[x] if x in num_dict2 else x, f))
                        new_name = f
                        if not f.endswith('.jpg') and not f.endswith('.mp4'):
                            index = f.find('.')
                            if index != -1:
                                new_name = f[:index]
                            new_name += self.get_file_type(fp)
                        new_name = self.get_good_name(new_name)
                        new_fp = os.path.join(outdir, new_name)
                        if new_name != f:
                            same_num = 2
                            origin_new_fp = new_fp
                            while os.path.isfile(new_fp):
                                new_fp = "".join([origin_new_fp[:-7], "_%s" % same_num, origin_new_fp[-4:]])
                                same_num += 1
                            os.rename(fp, new_fp)
                            logger.info("rename %s to %s" % (fp, new_fp) )


if __name__ == "__main__":
    setup_logging()
    dy = DouYin()
    #dy = DouYin('cd_buy_house.json')
    if dy.conf['check_sensitive']:
        dy.check_sensitive()
        exit(0)
    if dy.conf['run_immediate']:
        dy.do_work()
    if dy.conf['run_scheduler']:
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 600
        }
        scheduler = BlockingScheduler(job_defaults=job_defaults, timezone='Asia/Shanghai')
        job = scheduler.add_job(dy.do_work, 'cron', hour=23, minute=50)
        #scheduler.modify_job(job.id, misfire_grace_time=600)
        scheduler.start()