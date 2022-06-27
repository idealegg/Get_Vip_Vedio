# -*- coding:utf-8 -*-
import re
import requests
from Common.GetSensBase import GetSensBase
from Util.myLogging import *
import pprint
import subprocess
import urllib.parse
import Util.Utility as util


KEY_PATTERN = re.compile(b'#EXT-X-KEY\s*:\s*METHOD\s*=\s*([^,]+?),\s*URI\s*=\s*"([^"]+?)"')


def generate_m1907_file(gsb, is_force=False):
  f_conf = gsb.conf['m1907_info_path']
  m1907_info = {}
  if not is_force and os.path.isfile(f_conf):
    m1907_info = util.get_json(f_conf)
  logger.info("To generate a m1907 file:\n")
  for src_url in gsb.conf['src_url']:
    if src_url not in m1907_info or m1907_info[src_url]['force_reset']:
      cmd = '%s %s %s' % (r'tools\phantomjs.exe',
                          r'js\m1907.js',
                          src_url)
      logger.info("cmd: %s" % cmd)
      f_popen = os.popen(cmd)
      sign_url = f_popen.read()
      logger.info("Return value: %s" % sign_url)
      f_popen.close()
      sign_url = re.sub('/cover/[^/]+/', '/page/', sign_url)
      url = "%s%s" % (gsb.conf['servers'], sign_url.strip())
      logger.info("Url: %s" % url)
      req = gsb.get_req(url)
      logger.info("req: %s" % req)
      logger.info("req.content: %s" % req.content)
      m1907_info[src_url] = {'m1907_src_url': src_url,
                             'm1907_sign_url': sign_url,
                             'm1907_url': url,
                             'm1907_status': 'parsed',
                             'force_reset': True,
                             }
      m1907_info[src_url].update(json.loads(req.content.decode('utf8')))
      util.save_json(m1907_info, f_conf)
      req.close()
    generate_a_new_sen(gsb, m1907_info[src_url], m1907_info[src_url]['force_reset'])
  return True


def check_key(con, uri_dir):
  res = re.search(KEY_PATTERN, con)
  if res:
    logger.info("Encrypt method: %s, Key uri: %s\n" % (res.group(1), res.group(2)))
    url = "%s%s" % (uri_dir, res.group(2).decode('utf8'))
    logger.info("URL: %s\n" % url)
    req = requests.get(url)
    logger.info("req: %s" % req.content)
    ret = req.content.decode('utf8')
    req.close()
    return ret
  return ''


def save_sen(gsb, m1907_one_info, sens_info, req, e, season):
  if gsb.conf['is_one_sen_a_url']:
    il = list(filter(lambda x: x['m1907_src_url'] == m1907_one_info['m1907_src_url'], sens_info['sen_list']))
  else:
    il = ''
  cur_sen = {}
  if il:
    cur_sen = il[0]
    i = cur_sen['sen']
  else:
    i = gsb.get_base_sen_id()
    sens_info['sen_list'].append(cur_sen)
  logger.info("save %s.m3u8" % i)
  m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
  f_m3u8 = open(m3u8, 'wb')
  f_m3u8.write(req.content)
  f_m3u8.close()
  uri_dir = e['url'][:e['url'].find('/', e['url'].find('//')+2) + 1]
  cur_sen.update({
    'sen': i,
    'm3u8': m3u8,
    'name': season['name'] + e['name'],
    'url': uri_dir,
    'key': check_key(req.content, uri_dir),
    'm1907_src_url': m1907_one_info['m1907_src_url']
  })


def generate_a_new_sen(gsb, m1907_one_info, is_force=False):
  f_conf = gsb.conf['sen_info_path']
  sens_info = {'sen_list':[]}
  if not is_force and os.path.isfile(f_conf):
    sens_info = util.get_json(f_conf)
  logger.info("To generate a sens_info file:\n")
  pprint.pprint(m1907_one_info)
  if is_force or not os.path.isfile(gsb.conf['sen_info_path']
  ) or all(map(lambda x: x['m1907_src_url'] != m1907_one_info['m1907_src_url'], sens_info['sen_list'])):
    error = False
    if 'data' in m1907_one_info:
      for season in m1907_one_info['data']:
        for e in season['source']['eps'][gsb.conf['start_sen']-1:]:
          logger.info("e['url']: %s" % e['url'])
          if e['url'].endswith('playlist.m3u8'):
            logger.info("Skip it!")
            continue
          req = gsb.get_req(e['url'], headers=gsb.conf['headers'])
          logger.info("req: %s, %s" % (req, req.content))
          if req.status_code == 200:
            if req.content.count(b'.ts') or len(req.content.split(b'\n')) > 10:
              if gsb.conf['direct_download_m3u8']:
                cmd = '"G:\Program Files (x86)\FormatFactory\\ffmpeg.exe" -i %s -c copy %s' % (e['url'].replace('https', 'http'), os.path.join(gsb.target_dir, "%s.mp4" % (season['name'] + e['name'])))
                logger.info(cmd)
                os.system(cmd)
                return
              save_sen(gsb, m1907_one_info, sens_info, req, e, season)
              util.save_json(sens_info, f_conf)
            else:
              for line in req.content.split(b'\n'):
                if not line.startswith(b"#"):
                  url = GetSensBase.concat_url(e['url'], line.decode('utf8'))
                  logger.info("url: %s" % url)
                  #req2 = requests.get(url)
                  req2 = gsb.get_req(url)
                  logger.info("req2: %s" % req2)
                  if req2:
                    if gsb.conf['direct_download_m3u8']:
                      cmd = '"G:\Program Files (x86)\FormatFactory\\ffmpeg.exe" -i %s -c copy %s' % (
                      e['url'].replace('https', 'http'), os.path.join(gsb.target_dir, "%s.mp4" % (season['name'] + e['name'])))
                      logger.info(cmd)
                      os.system(cmd)
                      return
                    save_sen(gsb, m1907_one_info, sens_info, req2, e, season)
                    util.save_json(sens_info, f_conf)
                  else:
                    error = True
                  break
          req.close()
          if error:
            break
        # only first data
        break
      logger.info("outs: %s " % sens_info)
    else:
      logger.info("no data in content!")


def a():
  fd=open('1.json')
  j=json.load(fd)
  fd.close()
  k=0
  for i in range(len(j['video'])):
    if 'm3u8' in j['video'][i]:
      k=i
  fd=open("0.m3u8" , 'wb')
  fd.write(j['video'][k]['m3u8'])
  fd.close()


if __name__ == "__main__":
  setup_logging()
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  conf={'base_dir': r'C:\hzw',
        'direct_download_m3u8': False,
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'm3u8', 'name', 'url'],
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_m1907.json'),
                         'm1907_info_path': os.path.join(conf_dir, 'm1907_sens_info.json'),
                         'start_sen': 1014,
                         'is_one_sen_a_url': False,
                         'src_url': [
                         #完美关系 'https://www.iqiyi.com/v_19rxfnb3w4.html?vfrm=pcw_dianshiju&vfrmblk=F&vfrmrst=711219_dianshiju_tbrb_float_video_play3'
                         #  'https://v.youku.com/v_show/id_XNDAyMTYwMjc4MA==.html?tpa=dW5pb25faWQ9MTAzNzUzXzEwMDAwMV8wMV8wMQ&refer=sousuotoufang_market.qrwang_00002944_000000_QJFFvi_19031900'
                         #urllib.parse.quote('误杀2'),
                          # urllib.parse.quote('长津湖'),
                          # urllib.parse.quote('我和我的父辈'),
                           urllib.parse.quote('海贼王'),
                         ],
                         'servers': 'https://z1.m1907.cn',
        'remove_ts': False,
        'headers': {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  if 0:
    generate_m1907_file(th, True)
  if 1:
    th_list = [th]
    th.start()
    th = GetSensBase(conf)
    th_list.append(th)
    th.start()
    for th in th_list:
      th.join()
