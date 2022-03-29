# -*- coding:utf-8 -*-
import os
import requests
import Common.GetSensBase
from Util.myLogging import *
import threading
import re
import pprint
import string
import pickle
from bs4 import BeautifulSoup
from Util.Utility import to_bytes, to_str, decode_hex2str


class HGetSens(Common.GetSensBase.GetSensBase):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""

  def __init__(self, conf=Common.GetSensBase.GetSensBase.default_conf):
    super(HGetSens, self).__init__(conf)
    self.headers_updated = False

  def before_start_download(self):
    if not self.headers_updated:
      url = self.task_list[0][1]
      t1 = url[url.find('://') + 3:]
      self.headers['Host'] = t1[:t1.find('/')]
      self.headers_updated = True

  def gen_m3u8(self, info, sen):
    #hash = info[info.rfind('/') + 1:]
    info = to_str(info)
    sen = to_str(sen)
    u2 = "%s/%s/%s/hd.m3u8" % (
      decode_hex2str(b'68747470733a2f2f71712e6971697969322e62353535622e636f6d3a37373737'),
      info[:2], info)
    logger.info("task url: %s\n" % u2)
    if 0:
      req = requests.get(u2, headers=self.conf['headers'])
      logger.info("req: %s\n" % req)
      if req.status_code != 200:
        raise Exception("findout_all_ref: get m3u8 failed!")
    if 0:
      refs = req.content.split('\n')
      req.close()
      refs = filter(lambda x: not x.startswith('#'), refs)
      refs = refs[1:]
      if len(refs) > 999:
        refs = map(lambda x: "".join([x[1:x.rfind('/')], '/1', x[x.rfind('/')+1:]]) if x.startswith('1http') else x , refs)
    if 0:
      f_name = os.path.join(self.store_dir, "%s.m3u8" % self.sen)
      f1 = open(f_name, "wb")
      f1.write('\n'.join(refs))
      f1.close()
    else:
      cmd = 'ffmpeg -i %s -c copy -y %s.mp4' % (u2, sen)
      logger.info(cmd)
      os.system(cmd)
    self.headers_updated = False


def process_name(s, i):
  s1 = to_str(s)
  s1 = ''.join(filter(lambda x: x in string.printable[:62], s1))
  while s1 and not s1[0].isalpha():
    s1 = s1[1:]
  while s1 and not (s1[-1].isalpha() or s1[-1].isdigit()):
    s1 = s1[:-1]
  if not s1:
    s1 = "tmp%d" % i
  return to_bytes(s1)


def get_info(wd):
  vod_pattern = re.compile(b'<span class="wb1"><a href="([^"]+)" target="_blank">([^<]+)<')
  # wd='%E7%97%B4%E6%B1%89'
  #wd = 'meyd'
  i = 50
  out = []
  if len(sys.argv) > 1:
    i = int(sys.argv[1])
  if len(sys.argv) > 2:
    wd = sys.argv[2]
  url_base = decode_hex2str(b'687474703a2f2f7777772e6a696c657a79322e636f6d3a373737')
  url = '%s/search?wd=%s' % (url_base, wd)
  r1 = requests.get(url)
  logger.info("r1: %s" % r1)
  pgs = 1
  if r1.status_code == 200:
    bs = BeautifulSoup(r1.content, 'html.parser')
    pnav = bs.find('div', class_='pagenav')
    pgs = len(pnav.find_all(text=lambda x: x.isdigit()))
    sps = bs.find_all('span', class_='wb1')
    for sp in sps:
      links = sp.find_all('a')
      if len(links):
        out.append(b"%s %s" % (to_bytes(links[0]['href']), to_bytes(links[0].text.strip())))
  r1.close()
  for pg in range(2, pgs+1):
    url = '%s/search?wd=%s&page=%d' % (url_base, wd, pg)
    r1 = requests.get(url)
    logger.info("r1: %s" % r1)
    if r1.status_code == 200:
      for line in r1.content.split(b"\n"):
        b1 = re.search(vod_pattern, line)
        if b1:
          out.append(b"%s %s" % (b1.group(1), b1.group(2).replace(b' ', b'')))
  logger.info(pprint.pformat(out))
  abc = re.compile(b'id="vsscopy" data-value="([^"]+)"')
  out4 = []
  for f in out:
    f1 = re.split(b"\s+", f)
    req = requests.get('%s%s' % (url_base, f1[0].decode('utf8')))
    logger.info("req: %s" % req)
    a1 = re.search(abc, req.content)
    out4.append((a1.group(1)[a1.group(1).rfind(b"/") + 1:], process_name(f1[1], i)))
    i += 1
    req.close()
  return out4


if __name__ == "__main__":
  setup_logging()
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  conf = {'base_dir': r'F:\store',
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url'],
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_av.txt'),
                         'append_url_before': False,
                         'headers': {
                           'Host': 'qq.iqiyi2.b555b.com:7777',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'zh-CN,zh;q=0.9',
                           'Origin': 'http://youku.letv.player.c24680.com:6688',
                           'x-requested-with': 'XMLHttpRequest',
                         },
          'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
          }

                         }
  if 0:
    th_list = []
    for i in range(2):
      th = HGetSens(conf)
      th_list.append(th)
      th.start()
    for th in th_list:
      th.join()
  else:
    th = HGetSens(conf)
    force_reset = False
    if not force_reset and os.path.isfile(th.conf['sen_info_path']):
      with open(th.conf['sen_info_path'], 'rb') as fd:
        th.info = pickle.load(fd)
    if not th.info:
      th.info = get_info(decode_hex2str(b'5c75373566345c7536633439'))
    with open(th.conf['sen_info_path'], 'wb') as fd:
      pickle.dump(th.info, fd)
    logger.info(pprint.pformat(th.info))
    t_list = []
    th_num = 4
    sen = 4
    j_timeout = 5.0
    for info in th.info:
      t = threading.Thread(target=th.gen_m3u8, args=(info[0], info[1]))
      t_list.append(t)
      #sen += 1
    t_list2 = []
    while t_list:
      if len(t_list2) < th_num:
        i = min(th_num - len(t_list2), len(t_list))
        for t in t_list[:i]:
          t_list2.append(t)
          t.start()
          t_list.remove(t)
      for t in t_list2:
        t.join(j_timeout)
        if not t.is_alive():
          t_list2.remove(t)



