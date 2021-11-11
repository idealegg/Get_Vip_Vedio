# -*- coding:utf-8 -*-
import json
import os
import threading
import time
import traceback
import urllib
import Util.GetSign
import Util.GetKey
import Util.MergeF4v
import requests

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

  def stop(self):
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
      f_size = len(req2.content)
      # print req.content
      f_path = os.path.join(self.store_dir, "%s_%d.ts" % (self.sen, i))
      fd = open(f_path, "wb")
      fd.write(req2.content)
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
    global lock
    global to_finish_keys
    key = None
    lock.acquire()
    if to_finish_keys:
      self.leisure = False
      key = to_finish_keys.pop(0)
    lock.release()
    if key:
      return key, all_task_info[key]
    else:
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

  def findout_all_ref(self, content):
    cont = json.loads(content)
    cont['url'] = urllib.unquote(cont['url']).replace('hhttps', 'https')
    url = cont['url']
    index = 0
    for i in range(3):
      index += url.find('/') + 1
      url = url[url.find('/')+1:]
    url = cont['url'][:index-1]
    print url
    refs = self.getreffromurl(cont['url'])
    print refs
    if len(refs) != 1:
      print "The first m3u8 file is empty!"
      return []
    refs = self.getreffromurl("%s%s" % (url, refs[0]))
    return map(lambda x:"%s%s"%(url, x), refs)

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
    for th in thread_list:
      print "Remaining thread: [%s]" % res[i][1]
      th.join()
      res2.remove(res[int(th.getName(), 10)])
    return res2

  def getNotDownload(self):
    fd = open("%s.m3u8" % self.sen, 'r')
    res = [i for i in fd]
    flags = [False]*len(res)
    fd.close()
    f_list = os.listdir(self.store_dir)
    for f in f_list:
      if self.sen_number_equal(f):
        flags[int(f[f.find('_')+1:-3], 10)] = True
    res2 = []
    for i in range(len(flags)):
      if not flags[i]:
        res2.append((i, res[i]))
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
            self.textmod['id'] = self.info
            self.textmod['md5'] = Util.GetSign.GetSign(
                                      Util.GetKey.GetKey(
                                       url='http://www.1717yun.com/1717yun/',
                                       addr=self.info,
                                       host='www.1717yun.com',
                                       ref='http://www.1717yun.com/jx/ty.php?url=&url='))
            self.header_dict['Referer'] = "http://www.1717yun.com/1717yun/?url=%s" % self.info
            req = requests.post(url=self.url, data=self.textmod,  headers=self.header_dict)
            print req.encoding
            print req.headers
            print req.reason
            print req.content
            res = self.findout_all_ref(req.content)
            req.close()
            req = None
            print "len: %d" % len(res)
            print "res:"
            print res
            fd=open("%s.m3u8"%self.sen, 'w')
            fd.write("\n".join(res))
            fd.close()
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
            f_list.sort(key=lambda x: int(x[x.rfind('_')+1:-3], 10))
            Util.MergeF4v.merge(f_list, self.target_dir, False, False)
          else:
            print "file %s.mp4 exist! So not merge again!" % self.sen
        else:
          print '%s is leisure!' % self.getName()
          print to_finish_keys
          self.leisure = True
          time.sleep(1)
      except:
        self.leisure = True
        print "Exception in getSens.run\n"
        if req:
          req.close()
        traceback.print_exc()
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
  done_file_list = map(lambda x: x.decode('ISO-8859-1').replace(u'\xbc\xaf', u'\u96c6'), done_file_list)
  print done_file_list


def all_task_finished(ths):
  global to_finish_keys
  if to_finish_keys:
    return False
  for th in ths:
    if not th.leisure:
      return False
  return True

if __name__ == "__main__":
  Util.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  store_dir = r"F:\store\store"
  # store_dir = "D:\\movies\\haizeiwang\\lost"
  target_dir = r"F:\store\merge"
  url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=2&tn=baiduhome_pg&wd=%E9%A3%8E%E8%B5%B7%E9%95%BF%E6%9E%97&rsv_spt=1&oq=python%2520print&rsv_pq=9fe2cecf0009fcd3&rsv_t=5e590W2QAZ1p0%2FIW8C7sQ4ELeznGgBUqi9aPPYkhkradNgRwRpi39n%2B%2Bkd%2FrMPWls%2BTc&rqlang=cn&rsv_enter=1&rsv_sug3=9&rsv_sug1=6&rsv_sug7=100&bs=python%20print'
  #url = 'https://www.baidu.com/s?wd=%E6%B5%B7%E8%B4%BC%E7%8E%8B&rsv_spt=1&rsv_iqid=0xbffec5ef00005e64&issp=1&f=3&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&oq=python%2520get%25E8%25AF%25B7%25E6%25B1%2582%25E5%25B8%25A6%25E5%258F%2582%25E6%2595%25B0&rsv_t=28a94GR7HpLTzNrPlxmkECd%2FH7%2FxLVUT%2Fl7nNZg2lvXyLYGYmSm%2FWmgmJU%2BHYzdTE192&inputT=5673&rsv_pq=c94fc4ed00034890&rsv_sug3=21&rsv_sug1=22&rsv_sug7=101&rsv_sug2=1&prefixsug=ha&rsp=0&rsv_sug4=7286'
  thn = 1
  getExistFile([store_dir, target_dir])
  all_task_info = Util.GetVid.GetSens(url)
  print all_task_info
  to_finish_keys = all_task_info.keys()
  to_finish_keys.sort(cmp=lambda x,y: cmp(int(x[:-1], 10), int(y[:-1], 10)))
  th_list = []
  for i in range(thn):
    th = getSens(store_dir, target_dir)
    th_list.append(th)
    th.start()
  time.sleep(1)
  while True:
    if all_task_finished(th_list):
      for th in th_list:
        th.stop()
      for th in th_list:
        th.join()
      print "All task completed!"
      break
    else:
      print "sleeping..."
      time.sleep(10)