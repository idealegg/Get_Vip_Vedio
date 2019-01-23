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


done_file_list = []
all_task_info = {}
to_finish_keys = []
lock = threading.RLock()
path_coding = 'ISO-8859-1'
file_coding = 'Windows-1252'


class getSens(threading.Thread):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""

  def __init__(self, store_dir, target_dir):
    super(getSens, self).__init__()
    self._stop_event = threading.Event()
    self.textmod={ "xml": "http://www.iqiyi.com/v_19rrok5n98.html?vfm=2008_aldbd",
                    "md5": "ab59a7e5488ab5d664e3e74ddce8loij",
                    "type": "auto",
                    "hd": "cq",
                    "wap": "0",
                    "siteuser": None,
                    "lg": None,
                    "sohuuid": None}
    self.header_dict = {"Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip,deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Host": "all.baiyug.cn:2021",
                "Referer": "http://all.baiyug.cn:2021/vip_all/index.php?url=http://www.iqiyi.com/v_19rrok5ncc.html?vfm=2008_aldbd",
                "User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                "X-Requested-With": "ShockwaveFlash/32.0.0.101"
                }
    self.url = 'http://all.baiyug.cn:2021/vip_all/url.php'
    self.store_dir = store_dir
    self.target_dir = target_dir
    self.check_dirs = [store_dir, target_dir]
    self.leisure = True

  def stop(self):
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()

  def getAFile(self, url, i, sen):
    req2 = None
    fd = None
    try:
      print "%s [%d]: %s\n" % (sen, i, url)
      start_time = time.time()
      req2 = requests.get(url=url)
      print req2.encoding
      print req2.headers
      print req2.reason
      f_size = len(req2.content)
      # print req.content
      f_path = os.path.join(self.store_dir, "%s_%d.f4v" % (sen, i))
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

  def run(self):
    global done_file_list
    req = None
    try:
      while not self.stopped():
        sen, info = self.getASen()
        if sen:
          f_list = []
          if not done_file_list.count("%s_%d.f4v" % (sen, 0)):
            self.textmod['xml'] = info
            self.textmod['md5'] = GetSign.GetSign.GetSign(GetKey.GetKey.GetKey(info))
            self.header_dict['Referer'] = "http://all.baiyug.cn:2021/vip_all/index.php?url=%s" % info
            req = requests.get(url=self.url, params=self.textmod,  headers=self.header_dict)
            print req.encoding
            print req.headers
            print req.reason
            print req.content
            res = re.findall("<!\[CDATA\[(http.*?f4v.*?)\]\]></file>", req.content)
            print "len: %d" % len(res)
            print "res:"
            print res
            #f_list = map(lambda x:"%s_%d.f4v" % (sen, x), range(len(res)))
            thread_list = []
            for i in range(len(res)):
              th = threading.Thread(target=self.getAFile, args=(res[i], i, sen))
              th.start()
              thread_list.append(th)
            for th in thread_list:
              th.join()
            req.close()
            req = None
          else:
            print "file %s_0.f4v exist! So not download again!" % sen
          if not done_file_list.count("%s.mp4" % sen):
            if not f_list:
              f_n = 0
              for file in os.listdir(self.store_dir):
                if file.endswith('.f4v') and int(file[:-8], 10) == int(sen[:-1]):
                  f_n += 1
                  f_list.append(os.path.join(self.store_dir,file))
              #f_list = map(lambda x: os.path.join(self.store_dir, "%s_%d.f4v" % (sen, x)), range(f_n))
            MergeF4v.MergeF4v.merge(f_list, self.target_dir)
          else:
            print "file %s.mp4 exist! So not merge again!" % sen
        else:
          print '%s is leisure!' % self.getName()
          print to_finish_keys
          self.leisure = True
          time.sleep(1)
      print "getSens.run thread %s end!" % self.getName()
    except:
      print "Exception in getSens.run\n"
      if req:
        req.close()
      raise


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
  RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  store_dir = r"C:\Downloads\store"
  # store_dir = "D:\\movies\\haizeiwang\\lost"
  target_dir = r"C:\Downloads\merge"
  thn = 1
  getExistFile([store_dir, target_dir])
  all_task_info = GetVid.GetVid.GetSens()
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