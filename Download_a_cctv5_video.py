# -*- coding:utf-8 -*-
import os, sys, requests
import re
import GetVid.GetVid
import GetSign.GetSign
import GetKey.GetKey
import RedirectOut.RedirectOut
import MergeF4v.MergeF4v
import time
import threading
import chardet
import json
import urllib
import traceback
from Crypto.Cipher import AES


done_file_list = []
all_task_info = {}
to_finish_keys = []
lock = threading.RLock()
path_coding = 'ISO-8859-1'
file_coding = 'Windows-1252'


class getSens(threading.Thread):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""

  def __init__(self, store_dir, target_dir, init_step=5, s_sleep=0.5, retry=3):
    super(getSens, self).__init__()
    self._stop_event = threading.Event()
    self.textmod={ "id": "http://www.iqiyi.com/v_19rrok5n98.html?vfm=2008_aldbd",
                    "type": "auto",
                    "md5": "ab59a7e5488ab5d664e3e74ddce8loij",
                    "siteuser": None,
                    "hd": None,
                    "lg": None}
    self.header_dict = {"Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip,deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Host": "www.1717yun.com",
                "Referer": "http://www.1717yun.com/1717yun/?url=https://www.iqiyi.com/v_19rrf3hzfs.html?vfm=2008_aldbd",
                "User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"

                }
    self.url = 'http://www.1717yun.com/1717yun/url.php'
    self.store_dir = store_dir
    self.target_dir = target_dir
    self.check_dirs = [store_dir, target_dir]
    self.leisure = True
    self.s_sleep = s_sleep
    self.init_step = init_step
    self.retry = retry
    self.sen = None
    self.info = None
    self.sen_info_path = "sens_info.txt"
    self.sen_list = []
    self.sen_no = 0
    self.max_no_a_file = 700

  def stop(self):
    self.leisure = True
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()

  def getAFile(self, url, i):
    req2 = None
    fd = None
    try:
      print "%s [%d]: %s\n" % (self.sen, i, url)
      start_time = time.time()
      req2 = requests.get(url=url)
      print req2.encoding
      print req2.headers
      print req2.reason
      if self.info.has_key('key') and self.info['key']:
        cryptor = AES.new(self.info['key'], AES.MODE_CBC, self.info['key'])
        f_content = cryptor.decrypt(req2.content)
      else:
        f_content = req2.content
      f_size = len(f_content)
      # print req.content
      f_path = os.path.join(self.store_dir, "%s_%d.ts" % (self.sen, i))
      fd = open(f_path, "wb")
      fd.write(f_content)
      fd.close()
      fd = None
      req2.close()
      req2 = None
      end_time = time.time()
      print "file: %s, start: %s, end: %s, rate: %f kb/s\n" % (
            f_path, time.ctime(start_time), time.ctime(end_time), f_size/(end_time - start_time)/1000.0)
    except:
      print "Exception in getAFile\n"
      if fd:
        fd.close()
      if req2:
        req2.close()
      raise

  def getASen(self):
    if not self.sen_list:
      if os.path.exists(self.sen_info_path):
        fd = open(self.sen_info_path, "rb")
        for line in fd:
          line = line.strip()
          if line and not line.startswith('#'):
            print chardet.detect(line)
            line2 = line.decode('utf-8')
            fields = line2.split(" ")
            self.sen_list.append((fields[0], {'m3u8': fields[1].strip(),
                               'name' : fields[2].strip(),
                               'url'  : fields[3].strip(),
                               'key'  : fields[4].strip() if len(fields) > 4 else ''}))
        fd.close()
    if self.sen_list and self.sen_no < len(self.sen_list):
      self.sen_no += 1
      return self.sen_list[self.sen_no-1]
    return None, None

  def sen_number_equal(self, f):
    i = 0
    sth_equal = False
    while i < min(len(f), len(self.sen)):
      if not f[i].isdigit() and not self.sen[i].isdigit():
        return sth_equal
      if f[i] != self.sen[i]:
        return False
      sth_equal = True
      i += 1
    if len(f) > i and f[i].isdigit():
      return False
    return sth_equal

  def getreffromurl(self, url):
    req = requests.get(url)
    print req.encoding
    print req.headers
    print req.reason
    print req.content
    refs=[]
    for line in req.content.split('\n'):
      if line and not line.startswith('#'):
        refs.append(line)
    return refs

  def findout_all_ref(self):
    refs = []
    if os.path.exists(self.info['m3u8']):
      fd = open(self.info['m3u8'], "rb")
      for line in fd:
        line = line.strip()
        if line and not line.startswith('#'):
          refs.append(line)
      fd.close()
    return map(lambda x:"%s%s"%(self.info['url'], x), refs)

  def getRes(self, res):
    res2 = list(res)
    # f_list = map(lambda x:"%s_%d.f4v" % (sen, x), range(len(res)))
    j = 0
    step = self.init_step
    thread_list = []
    while j < len(res):
      for i in range(j, min(j + step, len(res))):
        th = threading.Thread(target=self.getAFile, args=(res[i][1], res[i][0]))
        th.setName("%d" % i)
        th.start()
        thread_list.append(th)
      time.sleep(self.s_sleep)
      for th in thread_list:
        if not th.is_alive():
          th.join()
          thread_list.remove(th)
          res2.remove(res[int(th.getName(), 10)])
      j += step
      step = self.init_step - len(thread_list)
      step = self.init_step - len(thread_list)
    if len(thread_list):
      for th in thread_list:
        print "Remaining thread: [%s]" % list(res[int(th.getName(), 10)])
        th.join(60.0)
        if not th.is_alive():
          thread_list.remove(th)
          res2.remove(res[int(th.getName(), 10)])
        else:
          print "Remaining thread can not be ended: [%s]" % list(res[int(th.getName(), 10)])
    return res2

  def getNotDownload(self):
    fd = open(os.path.join(self.store_dir, "%s.m3u8" % self.sen), 'r')
    res = []
    for i in fd:
      i = i.strip()
      if not i.startswith('#'):
        res.append(i)
    flags = [False]*len(res)
    fd.close()
    f_list = os.listdir(self.store_dir)
    for f in f_list:
      if self.sen_number_equal(f) and f.find('_') != -1 and f.find('.') != -1:
        t_str = f[f.find('_') + 1:f.rfind('.')]
        if t_str.isdigit():
          t_int = int(t_str, 10)
          if t_int < len(flags):
            flags[t_int] = True
    res2 = []
    for i in range(len(flags)):
      if not flags[i]:
        res2.append((i, "".join([self.info['url'], res[i]])))
    print "getNotDownload"
    print res2
    return res2

  def run(self):
    global done_file_list
    req = None
    while not self.stopped():
      try:
        self.sen, self.info = self.getASen()
        if self.sen:
          merge_again = False
          f_list = []
          if not done_file_list.count("%s_%d.ts" % (self.sen, 0)):
            res = self.findout_all_ref()
            print "len: %d" % len(res)
            print "res:"
            print res
            res2 = []
            for i in range(len(res)):
              res2.append((i, res[i]))
            for i in range(self.retry):
              if res2:
                res2 = self.getRes(res2)
          else:
            print "file %s_0.ts exist! So not download again!" % self.sen
          res2 = self.getNotDownload()
          if res2:
            for i in range(self.retry):
              res2 = self.getRes(res2)
            merge_again = True
          if merge_again or not done_file_list.count("%s.mp4" % self.sen):
            if not f_list:
              f_n = 0
              for file in os.listdir(self.store_dir):
                if file.endswith('.ts') and self.sen_number_equal(file):
                  f_n += 1
                  f_list.append(os.path.join(self.store_dir,file))
              #f_list = map(lambda x: os.path.join(self.store_dir, "%s_%d.f4v" % (sen, x)), range(f_n))
            f_list.sort(key=lambda x: int(x[x.rfind('_')+1:x.rfind('.')], 10))
            MergeF4v.MergeF4v.merge(f_list, self.target_dir, False, False)
            print os.path.join(self.target_dir, "%s.mp4" % self.sen)
            print os.path.join(self.target_dir, "%s.mp4" % self.info['name'])
            os.rename(os.path.join(self.target_dir, "%s.mp4" % self.sen),
                      os.path.join(self.target_dir, "%s.mp4" % self.info['name']))
            open(os.path.join(self.target_dir, "%s.mp4" % self.sen), 'wb').close()
          else:
            print "file %s.mp4 exist! So not merge again!" % self.sen
        else:
          print '%s is leisure!' % self.getName()
          print to_finish_keys
          self.stop()
          time.sleep(1)
      except:
        self.stop()
        print "Exception in getSens.run\n"
        if req:
          req.close()
        traceback.print_exc()
        break
    print "getSens.run thread %s end!" % self.getName()


def getExistFile(check_dirs):
  global done_file_list
  for dir in check_dirs:
    print dir
    print os.listdir(dir)
    if done_file_list:
      done_file_list.extend(os.listdir(dir))
    else:
      done_file_list = os.listdir(dir)
  print done_file_list


def all_task_finished(ths):
  global to_finish_keys
  if to_finish_keys:
    return False
  for th in ths:
    if not th.leisure:
      return False
  return True


def GetMaxId():
  global MaxId
  if MaxId != 0:
    MaxId += 1
    return MaxId
  for f in done_file_list:
    f = "%s_." % f
    i = min(f.find("_"), f.find("."))
    id = 0
    try:
      id = int(f[:i])
    except:
      id = 0
    if id > MaxId:
      MaxId = id
  MaxId += 1
  return MaxId

def Generate_A_New_Sen(store_dir):
  #url = 'http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=bce8688d121c44a8846e4b5b19166383&tz=-8&from=000news&idl=32&idlr=32&modifyed=false&url=%s&tsp=1558853289&vn=1540&vc=63101A88ED29C1C4C89A90276812BD5B&uid=277E443320A0441F1C7514AAF4600CA6'
  f_cctv5 = open("cctv5_sens_info.txt")
  target_list = [i for i in f_cctv5]
  f_cctv5.close()
  f_cctv5 = open("sens_info.txt", 'w')
  for i in target_list:
    if i.startswith("#") or i.startswith("--"):
      continue
    print i
    target_url = i.strip()
    req = requests.get(url=target_url)
    j = json.loads(req.content)
    req.close()
    print j
    print j['hls_url']
    print j['title']
    t_host=j['hls_url'][:j['hls_url'].find('/', 7)]
    m3u8_list = requests.get(url=j['hls_url'])
    max_resolution = 0
    print m3u8_list.content
    for line in m3u8_list.content.split("\n"):
      if line and not line.startswith("#"):
        print line
        resolution = int(line[line.rfind('/')+1:-5])
        if resolution > max_resolution:
          m3u8_url = line
    m3u8_list.close()
    s_info = {}
    s_info['id'] = GetMaxId()
    s_info['m3u8'] = os.path.join(store_dir, "%d.m3u8" % s_info['id'])
    f_m3u8 = open(s_info['m3u8'], 'w')
    r_m3u8 = requests.get(url="%s%s"%(t_host, m3u8_url))
    f_m3u8.write(r_m3u8.content)
    f_m3u8.close()
    r_m3u8.close()
    s_info['title'] = j['title'].replace(' ', '_').replace('/', '_')
    s_info['url'] = "%s%s"%(t_host, m3u8_url[:m3u8_url.rfind("/")+1])
    f_cctv5.write(" ".join(["%d"%s_info['id'], s_info['m3u8'], s_info['title'], s_info['url'], "\n"]).encode('utf8'))
  f_cctv5.close()

if __name__ == "__main__":
  RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  store_dir = r"I:\movie\store"
  # store_dir = "D:\\movies\\haizeiwang\\lost"
  target_dir = r"I:\movie\merge"
  MaxId = 0
  getExistFile([store_dir, target_dir])
  Generate_A_New_Sen(store_dir)
  th = getSens(store_dir, target_dir)
  th.start()
  th.join()
