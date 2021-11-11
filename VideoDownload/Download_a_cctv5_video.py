# -*- coding:utf-8 -*-
import json
import os
import requests
import time
from Util.myLogging import *
from Common.GetSensBase import GetSensBase


def generate_a_new_sen(gsb, cctv5_file="cctv5_sens_info.txt"):
  #url = 'http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=bce8688d121c44a8846e4b5b19166383&tz=-8&from=000news&idl=32&idlr=32&modifyed=false&url=%s&tsp=1558853289&vn=1540&vc=63101A88ED29C1C4C89A90276812BD5B&uid=277E443320A0441F1C7514AAF4600CA6'
  if not os.path.isfile(gsb.conf['sen_info_path']) or not gsb.is_sen_exist():
    f_cctv5 = open(cctv5_file)
    target_list = [i for i in f_cctv5]
    f_cctv5.close()
    f_cctv5 = open(gsb.conf['sen_info_path'], 'w')
    for i in target_list:
      if i.startswith("#") or i.startswith("--"):
        continue
      logger.info(i)
      target_url = i.strip()
      req = requests.get(url=target_url)
      j = json.loads(req.content)
      req.close()
      logger.info(j)
      logger.info(j['hls_url'])
      logger.info(j['title'])
      t_host=j['hls_url'][:j['hls_url'].find('/', 7)]
      m3u8_list = requests.get(url=j['hls_url'])
      max_resolution = 0
      logger.info(m3u8_list.content)
      for line in m3u8_list.content.split("\n"):
        if line and not line.startswith("#"):
          logger.info(line)
          resolution = int(line[line.rfind('/')+1:-5])
          if resolution > max_resolution:
            m3u8_url = line
      m3u8_list.close()
      s_info = {'id': gsb.get_base_sen_id()}
      s_info['m3u8'] = os.path.join(gsb.store_dir, "%d.m3u8" % s_info['id'])
      f_m3u8 = open(s_info['m3u8'], 'w')
      r_m3u8 = requests.get(url="%s%s" % (t_host, m3u8_url))
      f_m3u8.write(r_m3u8.content)
      f_m3u8.close()
      r_m3u8.close()
      s_info['title'] = j['title'].replace(' ', '_').replace('/', '_')
      s_info['url'] = "%s%s" % (t_host, m3u8_url[:m3u8_url.rfind("/")+1])
      f_cctv5.write(" ".join(["%d" % s_info['id'], s_info['m3u8'], s_info['title'], s_info['url'], "\n"]).encode('utf8'))
    f_cctv5.close()


if __name__ == "__main__":
  setup_logging()
  #Util.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  th = GetSensBase(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 8,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'm3u8', 'name', 'url'],
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_cctv.txt'),
                         })
  th.check_dir()
  th.get_exist_file()
  generate_a_new_sen(th)
  th.start()
  th.join()
