# -*- coding:utf-8 -*-
import os, requests
import RedirectOut.RedirectOut
import time
import json
from GetSensBase.GetSensBase import GetSensBase


path_coding = 'ISO-8859-1'
file_coding = 'Windows-1252'


def generate_m1907_file(gsb, force=False):
  if not force and os.path.isfile(gsb.conf['m1907_info_path']):
    f_m1907 = open(gsb.conf['m1907_info_path'])
    content = f_m1907.read()
    f_m1907.close()
    if content.strip():
      print "%s is already existing!\n" % gsb.conf['m1907_info_path']
      return False
  print "To generate a m1907 file:\n"
  cmd = '%s %s %s' % (r'tools\phantomjs.exe',
                      r'tools\get_url.js',
                      gsb.conf['src_url'])
  print "cmd: %s" % cmd
  f_popen = os.popen(cmd)
  sign_url = f_popen.read()
  print "Return value: %s" % sign_url
  f_popen.close()
  url = "%s%s" % (gsb.conf['servers'], sign_url.strip())
  print "Url: %s" % url
  req = requests.get(url)
  print "req: %s" % req
  print "req.content: %s" % req.content
  f_m1907 = open(gsb.conf['m1907_info_path'], 'wb')
  f_m1907.write(req.content)
  f_m1907.close()
  req.close()
  return True


def generate_a_new_sen(gsb, force=False):
  if force or not os.path.isfile(gsb.conf['sen_info_path']) or not gsb.is_sen_exist():
    f_m1907 = open(gsb.conf['m1907_info_path'])
    j = json.load(f_m1907)
    f_m1907.close()
    b = j['data'][0]['source']['eps']
    outs = []
    i = gsb.get_base_sen_id()
    for e in b:
      print "e['url']: %s" % e['url']
      req = requests.get(e['url'])
      print "req: %s" % req.content
      for line in req.content.split('\n'):
        if not line.startswith("#"):
          url = GetSensBase.concat_url(e['url'], line)
          print "url: %s" % url
          req2 = requests.get(url)
          print "req2: %s" % req2
          m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
          f_m3u8 = open(m3u8, 'wb')
          f_m3u8.write(req2.content)
          f_m3u8.close()
          outs.append("%d %s %s %s" % (i, m3u8, e['name'], url[:url.rfind('/')+1]))
          req.close()
          req2.close()
          break
      i += 1
    print "outs: %s " % outs
    f_cctv5 = open(gsb.conf['sen_info_path'], 'w')
    f_cctv5.write("\n".join(outs).encode('utf8'))
    f_cctv5.close()


if __name__ == "__main__":
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'm3u8', 'name', 'url'],
                         'sen_info_path': 'sens_info_m1907.txt',
                         'm1907_info_path': 'm1907_sens_info.txt',
                         'src_url': 'https://www.iqiyi.com/v_19rqs2dqf0.html?vfm=2008_aldbd',
                         'servers': 'https://z1.m1907.cn',
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  generate_a_new_sen(th, generate_m1907_file(th, False))
  th_list = [th]
  th.start()
  th = GetSensBase(conf)
  th_list.append(th)
  th.start()
  for th in th_list:
    th.join()
