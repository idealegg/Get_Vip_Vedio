# -*- coding:utf-8 -*-
import os
import requests
import Common.GetSensBase
from Util.myLogging import *


class HGetSens(Common.GetSensBase.GetSensBase):
  """Thread class with a stop() method. The thread itself has to check
  regularly for the stopped() condition."""

  def __init__(self, conf=Common.GetSensBase.default_conf):
    super(HGetSens, self).__init__(conf)
    self.headers_updated = False

  def before_start_download(self):
    if not self.headers_updated:
      url = self.task_list[0][1]
      t1 = url[url.find('://') + 3:]
      self.headers['Host'] = t1[:t1.find('/')]
      self.headers_updated = True

  def gen_m3u8(self):
    hash = self.info['url'][self.info['url'].rfind('/') + 1:]
    u2 = "https://qq.iqiyi5.b555b.com:7777/video/%s" % hash
    logger.info("task url: %s\n" % u2)
    req = requests.get(u2, headers=self.conf['headers'])
    logger.info("req: %s\n" % req)
    if req.status_code != 200:
      raise Exception("findout_all_ref: get m3u8 failed!")
    refs = req.content.split('\n')
    req.close()
    refs = filter(lambda x: not x.startswith('#'), refs)
    refs = refs[1:]
    if len(refs) > 999:
      refs = map(lambda x: "".join([x[1:x.rfind('/')], '/1', x[x.rfind('/')+1:]]) if x.startswith('1http') else x , refs)
    f_name = os.path.join(self.store_dir, "%s.m3u8" % self.sen)
    f1 = open(f_name, "wb")
    f1.write('\n'.join(refs))
    f1.close()
    self.headers_updated = False


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
                           'Host': 'qq.iqiyi5.b555b.com:7777',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'zh-CN,zh;q=0.9',
                           'Origin': 'http://youku.letv.player.c24680.com:6688',
                           'x-requested-with': 'XMLHttpRequest',
                         }

                         }
  th_list = []
  for i in range(2):
    th = HGetSens(conf)
    th_list.append(th)
    th.start()
  for th in th_list:
    th.join()
