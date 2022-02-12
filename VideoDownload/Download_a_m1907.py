# -*- coding:utf-8 -*-
import re
import requests
from Common.GetSensBase import GetSensBase
from Util.myLogging import *
import pprint
import subprocess
import urllib.parse


KEY_PATTERN = re.compile(b'#EXT-X-KEY\s*:\s*METHOD\s*=\s*([^,]+?),\s*URI\s*=\s*"([^"]+?)"')


def generate_m1907_file(gsb, i=0, force=False):
  if not force and os.path.isfile(gsb.conf['m1907_info_path']):
    f_m1907 = open(gsb.conf['m1907_info_path'])
    content = f_m1907.read()
    f_m1907.close()
    if content.strip():
      logger.info("%s is already existing!\n" % gsb.conf['m1907_info_path'])
      return False
  logger.info("To generate a m1907 file:\n")
  cmd = '%s %s %s' % (r'tools\phantomjs.exe',
                      r'js\m1907.js',
                      gsb.conf['src_url'][i])
  logger.info("cmd: %s" % cmd)
  f_popen = os.popen(cmd)
  sign_url = f_popen.read()
  logger.info("Return value: %s" % sign_url)
  f_popen.close()
  sign_url = re.sub('/cover/[^/]+/', '/page/', sign_url)
  url = "%s%s" % (gsb.conf['servers'], sign_url.strip())
  logger.info("Url: %s" % url)
  #req = requests.get(url)
  req = gsb.get_req(url)
  logger.info("req: %s" % req)
  logger.info("req.content: %s" % req.content)
  f_m1907 = open(gsb.conf['m1907_info_path'], 'wb')
  f_m1907.write(req.content)
  f_m1907.close()
  req.close()
  return True


def check_key(con, uri_dir):
  res = re.search(KEY_PATTERN, con)
  if res:
    logger.info("Encrypt method: %s, Key uri: %s\n" % (res.group(1), res.group(2)))
    url = "%s%s" % (uri_dir, res.group(2))
    logger.info("URL: %s\n" % url)
    req = requests.get(url)
    logger.info("req: %s" % req.content)
    ret = req.content
    req.close()
    return ret
  return ''


def generate_a_new_sen(gsb, force=False):
  if force or not os.path.isfile(gsb.conf['sen_info_path']) or not gsb.is_sen_exist():
    f_m1907 = open(gsb.conf['m1907_info_path'], 'rb')
    j = json.load(f_m1907)
    f_m1907.close()
    pprint.pprint(j)
    outs = []
    error = False
    if 'data' in j:
      f_cctv5 = open(gsb.conf['sen_info_path'], 'r+b')
      outs.extend(f_cctv5.read().decode('utf8').split('\n'))
      for season in j['data']:
        for e in season['source']['eps']:
          logger.info("e['url']: %s" % e['url'])
          if e['url'].endswith('playlist.m3u8'):
            logger.info("Skip it!")
            continue
          #req = requests.get(e['url'])
          req = gsb.get_req(e['url'])
          logger.info("req: %s" % req.content)
          if req.content.count(b'.ts') or len(req.content.split(b'\n')) > 10:
            if gsb.conf['direct_download_m3u8']:
              cmd = '"G:\Program Files (x86)\FormatFactory\\ffmpeg.exe" -i %s -c copy %s' % (e['url'].replace('https', 'http'), os.path.join(gsb.target_dir, "%s.mp4" % (season['name'] + e['name'])))
              logger.info(cmd)
              os.system(cmd)
              return
            i = gsb.get_base_sen_id()
            m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
            f_m3u8 = open(m3u8, 'wb')
            f_m3u8.write(req.content)
            f_m3u8.close()
            uri_dir = e['url'][:e['url'].rfind('/') + 1]
            outs.append("%d %s %s %s %s" % (i, m3u8, season['name'] + e['name'], uri_dir, check_key(req.content, uri_dir)))
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
                  i = gsb.get_base_sen_id()
                  m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
                  f_m3u8 = open(m3u8, 'wb')
                  f_m3u8.write(req2.content)
                  f_m3u8.close()
                  uri_dir = url[:url.rfind('/')+1]
                  outs.append("%d %s %s %s %s" % (i, m3u8, season['name']+e['name'], uri_dir, check_key(req2.content, uri_dir)))
                  req2.close()
                else:
                  error = True
                break
          logger.info("\n".join(outs).encode('utf8')+b"\n")
          req.close()
          if error:
            break
        # only first data
        break
      logger.info("outs: %s " % outs)
      #f_cctv5 = open(gsb.conf['sen_info_path'], 'w')
      f_cctv5.write("\n".join(outs).encode('utf8'))
      f_cctv5.close()
    else:
      logger.info("no data in content!")
    #open(gsb.conf['m1907_info_path'], 'w').close()


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
  conf={'base_dir': r'G:\hzw',
        'direct_download_m3u8': False,
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'm3u8', 'name', 'url'],
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_m1907.txt'),
                         'm1907_info_path': os.path.join(conf_dir, 'm1907_sens_info.txt'),
                         'src_url': [
                         #完美关系 'https://www.iqiyi.com/v_19rxfnb3w4.html?vfrm=pcw_dianshiju&vfrmblk=F&vfrmrst=711219_dianshiju_tbrb_float_video_play3'
                         #  'https://v.youku.com/v_show/id_XNDAyMTYwMjc4MA==.html?tpa=dW5pb25faWQ9MTAzNzUzXzEwMDAwMV8wMV8wMQ&refer=sousuotoufang_market.qrwang_00002944_000000_QJFFvi_19031900'
                         urllib.parse.quote('误杀2'),
                         #  urllib.parse.quote('长津湖'),
                         ],
                         'servers': 'https://z1.m1907.cn',
        'remove_ts': False,
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  my_flag1 = 0
  #my_flag2 = 1
  my_flag2 = my_flag1
  my_flag3 = not (my_flag1 or my_flag2)
  if 0:
    for j in range(len(conf['src_url'])):
      generate_m1907_file(th, j, True)
      #generate_a_new_sen(th, my_flag2)
      generate_a_new_sen(th, True)
  if 1:
    th_list = [th]
    th.start()
    th = GetSensBase(conf)
    th_list.append(th)
    th.start()
    for th in th_list:
      th.join()
