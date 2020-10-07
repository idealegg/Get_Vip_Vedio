# -*- coding:utf-8 -*-
import os, sys, requests
import re
import RedirectOut.RedirectOut
import MergeF4v.MergeF4v
import time
import threading
import chardet
import traceback
from Crypto.Cipher import AES
import shutil


default_conf = {
  'base_dir': r'C:\store',
  'check_downloaded_retry': 3,
  'session_number': 4,
  'threading_num': 8,
  'wait_session_sleep_time': 0.5,
  'sen_field_name': ['sen', 'name', 'url', 'key'],
  'headers': {},
  'sen_info_path': 'sens_info.txt',
  'request_timeout': 10.0,
  'request_retry': 10,
  'skip_request_error': False,
  'download_timeout': 60.0,
  'append_url_before': True,
  'remove_ts': True,
}


class GetSensBase(threading.Thread):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""
  conf = default_conf
  store_dir = ''
  target_dir = ''
  sen_list = []
  sen_no = 0
  done_file_list = []
  sen_lock = threading.Lock()
  merge_lock = threading.Lock()
  base_sen_id = 0
  rename_lock = threading.Lock()

  def __init__(self, conf=default_conf):
    super(GetSensBase, self).__init__()
    self._stop_event = threading.Event()
    GetSensBase.conf.update(conf)
    GetSensBase.store_dir = os.path.join(self.conf['base_dir'], 'store')
    GetSensBase.target_dir = os.path.join(self.conf['base_dir'], 'merge')
    self.sen = None
    self.info = None
    self.sessions = []
    self.session_used = []
    self.session_lock = threading.Lock()
    self.task_lock = threading.Lock()
    self.thread_list = []
    self.task_list = []
    self.total_task_num = 0
    self.cur_task_num = 0
    self.headers = {}
    self.headers.update(self.conf['headers'])
    self.req_session = requests.Session()

  def get_req(self, url, **kwargs):
    retry = self.conf['request_retry']
    req = None
    if 'timeout' not in kwargs:
      kwargs['timeout'] = self.conf['request_timeout']
    while retry > 0:
      try:
        req = self.req_session.get(url, **kwargs)
      except Exception, e:
        print "Exception in req [%s]: %s" % (url, e)
      finally:
        retry -= 1
      if req:
        #print dir(req)
        if req.status_code == 200:
          break
    return req


  def check_dir(self):
    if not os.path.isdir(self.conf['base_dir']):
      os.mkdir(self.conf['base_dir'])
    if not os.path.isdir(self.store_dir):
      os.mkdir(self.store_dir)
    if not os.path.isdir(self.target_dir):
      os.mkdir(self.target_dir)

  def set_headers(self, header=None):
    if header:
      self.headers = header
    else:
      self.headers = self.conf['headers']

  @classmethod
  def get_exist_file(cls):
    if cls.done_file_list:
      return
    for dir in [cls.store_dir, cls.target_dir]:
      print dir
      print os.listdir(dir)
      if cls.done_file_list:
        cls.done_file_list.extend(os.listdir(dir))
      else:
        cls.done_file_list = os.listdir(dir)
    print cls.done_file_list

  def init_session(self):
    self.sessions = []
    self.session_used = []
    for i in range(self.conf['session_number']):
      self.sessions.append(requests.Session())
      self.session_used.append(False)

  def close_session(self):
    if self.sessions:
      for session in self.sessions:
        session.close()
      self.session_used = [False] * len(self.session_used)
    self.sessions = []
    self.session_used = []

  def get_a_session(self):
    ret = None
    while not ret:
      self.session_lock.acquire()
      t1 = filter(lambda x: not x, self.session_used)
      if t1:
        i = self.session_used.index(t1[0])
        self.session_used[i] = True
        ret = self.sessions[i]
      self.session_lock.release()
      if not ret:
        time.sleep(self.conf['wait_session_sleep_time'])
      else:
        return ret

  def release_a_session(self, s):
    self.session_lock.acquire()
    i = self.sessions.index(s)
    self.session_used[i] = False
    self.session_lock.release()

  def stop(self):
    self._stop_event.set()

  def stopped(self):
    return self._stop_event.is_set()

  def get_task(self):
    ret = (0, '')
    self.task_lock.acquire()
    if self.task_list:
      ret = self.task_list.pop(0)
      self.cur_task_num = len(self.task_list)
    self.task_lock.release()
    return ret

  def before_do_task(self):
    pass

  def before_start_download(self):
    pass

  def before_download_file(self):
    pass

  def do_task(self):
    fd = None
    session = None
    url = ''
    i = 0
    try:
      self.before_do_task()
      i, url = self.get_task()
      while url:
        self.before_download_file()
        print "%s [%d] [%d/%d]: %s\n" % (self.sen, i, self.cur_task_num, self.total_task_num, url)
        start_time = time.time()
        session = self.get_a_session()
        if self.headers:
          req2 = session.get(url=url, headers=self.headers, timeout=self.conf['download_timeout'])
        else:
          req2 = session.get(url=url, timeout=self.conf['download_timeout'])
        print "%s [%d]:\n\treq: [%s]\n\tencoding: %s\n\theader: %s\n" % (self.sen, i, req2, req2.encoding, req2.headers)
        if req2.status_code == 200:
          if 'key' in self.info and self.info['key']:
            cryptor = AES.new(self.info['key'], AES.MODE_CBC, self.info['key'])
            f_content = cryptor.decrypt(req2.content)
          else:
            f_content = req2.content
          self.release_a_session(session)
          f_size = len(f_content)
          # print req.content
          f_path = os.path.join(self.store_dir, "%s_%d.ts" % (self.sen, i))
          fd = open(f_path, "wb")
          fd.write(f_content)
          fd.close()
          fd = None
          end_time = time.time()
          print "%s [%d] [%d/%d]:\n\tfile: %s\n\tstart: %s\n\tend: %s\n\tused: %.3f\n\tsize: %.3f kb\n\trate: %.3f kb/s\n" % (
            self.sen,
            i,
            self.cur_task_num,
            self.total_task_num,
            f_path,
            time.ctime(start_time),
            time.ctime(end_time),
            end_time - start_time,
            f_size/1000.0,
            f_size/(end_time - start_time)/1000.0)
        else:
          self.release_a_session(session)
        i, url = self.get_task()
    except:
      print "Exception in getAFile: %s [%d]: %s\n" % (self.sen, i, url)
      traceback.print_exc()
      if fd:
        fd.close()
      if session:
        self.release_a_session(session)

  @classmethod
  def get_base_sen_id(cls):
    if cls.base_sen_id != 0:
      cls.base_sen_id += 1
      print "base_sen_id: %d" % cls.base_sen_id
      return cls.base_sen_id
    for f in cls.done_file_list:
      f = "%s_." % f
      i = min(f.find("_"), f.find("."))
      id = 0
      try:
        id = int(f[:i])
      except:
        id = 0
      if id > cls.base_sen_id:
        cls.base_sen_id = id
    cls.base_sen_id += 1
    print "base_sen_id: %d" % cls.base_sen_id
    return cls.base_sen_id

  @classmethod
  def parse_sen_from_line(cls, line):
    line = line.strip()
    if line and not line.startswith('#'):
      print chardet.detect(line)
      line2 = line.decode('utf-8')
      fields = re.split("\s+", line2)
      info = {}
      for field_name in cls.conf['sen_field_name']:
        info[field_name] = fields.pop(0) if fields else ''
      if 'sen' in cls.conf['sen_field_name']:
        cls.sen_list.append((info['sen'], info))
      else:
        cls.sen_list.append((cls.get_base_sen_id(), info))

  @classmethod
  def gen_sens(cls):
    cls.sen_lock.acquire()
    if not cls.sen_list:
      if os.path.exists(cls.conf['sen_info_path']):
        fd = open(cls.conf['sen_info_path'], "rb")
        for line in fd:
          cls.parse_sen_from_line(line)
        fd.close()
    cls.sen_lock.release()
    print "sens: %s\n" % cls.sen_list

  @classmethod
  def is_sen_exist(cls):
    cls.gen_sens()
    return len(cls.sen_list)

  @classmethod
  def get_a_sen(cls):
    ret = (None, None)
    cls.sen_lock.acquire()
    if cls.sen_list and cls.sen_no < len(cls.sen_list):
      cls.sen_no += 1
      ret = cls.sen_list[cls.sen_no-1]
    cls.sen_lock.release()
    print "get_a_sen: %s\n" % list(ret)
    return ret

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

  def get_ref_from_url(self, url):
    if self.headers:
      req = requests.get(url, headers=self.headers)
    else:
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

  def gen_m3u8(self):
    pass

  def get_urls_from_m3u8(self):
    f_name = os.path.join(self.store_dir, "%s.m3u8" % self.sen)
    if not os.path.isfile(f_name):
      self.gen_m3u8()
    fd = open(f_name, 'r')
    res = []
    for i in fd:
      i = i.strip()
      if not i.startswith('#'):
        res.append(i)
    fd.close()
    return res

  @classmethod
  def concat_url(cls, url, path):
    if not path.startswith('/'):
      return "%s/%s" % (url[:url.rfind('/')], path)
    else:
      return "%s%s" % (url[:url[9:].find('/') + 9], path)

  def get_not_download(self):
    res = self.get_urls_from_m3u8()
    flags = [False]*len(res)
    f_list = os.listdir(self.store_dir)
    for f in f_list:
      if self.sen_number_equal(f) and f.find('_') != -1 and f.find('.') != -1:
        t_str = f[f.find('_')+1:f.rfind('.')]
        if t_str.isdigit():
          t_int = int(t_str, 10)
          if t_int < len(flags):
            flags[t_int] = True
    self.task_list = []
    for i in range(len(flags)):
      if not flags[i]:
        if self.conf['append_url_before'] and 'url' in self.info and self.info['url']:
          self.task_list.append((i, GetSensBase.concat_url(self.info['url'], res[i])))
        else:
          self.task_list.append((i, res[i]))
    self.total_task_num = len(self.task_list)
    self.cur_task_num = len(self.task_list)
    print "get_not_download: [%s]" % self.task_list

  def start_download(self):
    for i in range(self.conf['threading_num']):
      th = threading.Thread(target=self.do_task)
      self.thread_list.append(th)
      th.start()
    for th in self.thread_list:
      th.join()

  def run(self):
    req = None
    self.check_dir()
    self.get_exist_file()
    GetSensBase.gen_sens()
    while not self.stopped():
      try:
        self.sen, self.info = GetSensBase.get_a_sen()
        if self.sen:
          merge_again = False
          copy_again = False
          f_list = []
          self.headers = {}
          self.headers.update(self.conf['headers'])
          self.init_session()
          dst_file = os.path.join(self.target_dir, "%s.mp4" % self.info['name'])
          if not self.done_file_list.count("%s.mp4" % self.sen):
            self.get_not_download()
            retry = self.conf['check_downloaded_retry']
            if not self.task_list:
              print "All ts file downloaded! So not download again!" % self.sen
            else:
              while self.task_list and retry > 0:
                print "len: %d" % len(self.task_list)
                print "tasks:"
                print self.task_list
                self.before_start_download()
                self.start_download()
                self.get_not_download()
                retry -= 1
              merge_again = True
          else:
            print "file %s.mp4 exist! So not download again!" % self.sen
          if not f_list:
            f_n = 0
            for file in os.listdir(self.store_dir):
              if file.endswith('.ts') and self.sen_number_equal(file):
                f_n += 1
                f_list.append(os.path.join(self.store_dir, file))
            #f_list = map(lambda x: os.path.join(self.store_dir, "%s_%d.f4v" % (sen, x)), range(f_n))
          f_list.sort(key=lambda x: int(x[x.rfind('_')+1:x.rfind('.')], 10))
          if merge_again or not self.done_file_list.count("%s.mp4" % self.sen):
            GetSensBase.merge_lock.acquire()
            MergeF4v.MergeF4v.merge(f_list, self.target_dir, False, False)
            GetSensBase.merge_lock.release()
          else:
            print "file %s.mp4 exist! So not merge again!" % self.sen
          f_list.extend(map(lambda x: os.path.join([self.store_dir, x]),
                            filter(lambda x: x.startswith('merge_%d_') and x.endswith('.ts'), os.listdir(self.store_dir))))
          src_file = os.path.join(self.target_dir, "%s.mp4" % self.sen)
          if ("%s.mp4" % self.sen) not in os.listdir(self.target_dir) and ("%s.mp4" % self.sen) in os.listdir(self.store_dir):
            shutil.move(os.path.join(self.store_dir, "%s.mp4" % self.sen), src_file)
          if os.path.isfile(src_file) and os.path.getsize(src_file):
            print "src: [%s]\n" % src_file
            print "dst: [%s]\n" % dst_file
            GetSensBase.rename_lock.acquire()
            os.rename(os.path.join(self.target_dir, "%s.mp4" % self.sen),
                      os.path.join(self.target_dir, "%s.mp4" % self.info['name']))
            GetSensBase.rename_lock.release()
            open(os.path.join(self.target_dir, "%s.mp4" % self.sen), 'wb').close()
            if self.conf['remove_ts']:
              for t_f in f_list:
                os.unlink(t_f)
          else:
            print "%s already renamed!\n" % src_file
          self.close_session()
        else:
          print '%s is leisure!' % self.getName()
          self.close_session()
          self.stop()
          time.sleep(1)
      except:
        self.stop()
        print "Exception in getSens.run\n"
        if req:
          req.close()
        self.close_session()
        traceback.print_exc()
        break
    self.close_session()
    print "getSens.run thread %s end!" % self.getName()


if __name__ == "__main__":
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  os.chdir("..")
  th = GetSensBase(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 1,
                         'session_number': 4,
                         'threading_num': 8,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'm3u8', 'name', 'url', 'key'],
                         'sen_info_path': 'sens_info_cctv.txt',
                         'remove_ts': True,
                         })
  th.start()
  th.join()
