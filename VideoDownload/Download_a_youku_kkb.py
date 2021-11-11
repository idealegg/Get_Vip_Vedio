# -*- coding:utf-8 -*-
import os, requests
import RedirectOut.RedirectOut
import time
import json
import re
from GetSensBase.GetSensBase import GetSensBase
from hashlib import md5
import pprint
import random


path_coding = 'ISO-8859-1'
file_coding = 'Windows-1252'
KEY_PATTERN = re.compile('#EXT-X-KEY\s*:\s*METHOD\s*=\s*([^,]+?),\s*URI\s*=\s*"([^"]+?)"')

DATA = '''{
	"steal_params": "{\"ccode\":\"0502\",\"client_ip\":\"192.168.1.1\",\"utid\":\"NBevFStAZEQCAW40jnu9IcNS\",\"client_ts\":%s,\"version\":\"1.8.1\",\"ckey\":\"119#MlKT3NBFM8PGzMMzlyfMRuVLT7EBEbACc6MtYBAsqUnTFatOwvVDvYyAjcplNL8GLeASRBsU3AALuwHNk9SKOrA8RJBONt8L9ei25SSUdGIy/Upp4SMn6rA2RW1zNNFGfeAzR/QYdUeIx4LL7G12qCnxSCqOfoDjsvmw6EOMAOl7Y/h6SYVHIxImmtyIKrTJDojBBgjZTamxD7tViyQxxP+C3W/fByo7iM3PGDP3dzMNrb0Y96bE7k8oJV6e6IaFwcLCuRUspdmc4zcGhpzU4m/8TqqD0cuYnEwbg+pQHpkBd9ALU3j6uFCi9h6jIaRrpTSV7kwAur6WcTODqT1B4d6/MJ9eFwkMZrVn5MabjVXDbKcnmaGmL9aj/4k1yfWkCY0YNhREFvU7N/slngR/mgjDBGPBvvm5CR4PHRrTE4c7DCfnW/xEW31J19xRLyc2P48mIQM2LQxfw2cBJhCDrxZXJBEWyA3XplF7/8a9D5z0BU0THL6GE4ec/ru6n9yNWaSMq5mY/uJNNf9wh3GymAu4hJTGV35dOFSIhSrYsMa3r/Icy4BmbcxCzxIw9f4xqeQxFBo8d8501Zl2vKkrOO2WMrom3RkH1OBfOLUwjPSJqOZ1Y7HFSE0RkD+FHtNhZdE1bTjG3FW56JBXao90g1tWjedX+Q14g9QTbhVSrzkXBbMUIC==\"}",
	"biz_params": "{\"vid\":\"%s\",\"play_ability\":5376,\"master_m3u8\":1,\"media_type\":\"standard,subtitle\",\"app_ver\":\"1.8.1\"}",
	"ad_params": "{\"vs\":\"1.0\",\"pver\":\"1.8.1\",\"sver\":\"2.0\",\"site\":1,\"aw\":\"w\",\"fu\":0,\"d\":\"0\",\"bt\":\"pc\",\"os\":\"win\",\"osv\":\"7\",\"dq\":\"auto\",\"atm\":\"\",\"partnerid\":\"null\",\"wintype\":\"interior\",\"isvert\":0,\"vip\":0,\"emb\":\"AjEwNzk3MDM3NzMCdi55b3VrdS5jb20CL3Zfc2hvdy9pZF9YTkRNeE9EZ3hOVEE1TWc9PS5odG1s\",\"p\":1,\"rst\":\"mp4\",\"needbf\":2}"
}'''
DATA=r'{"steal_params":"{\"ccode\":\"0502\",\"client_ip\":\"192.168.1.1\",\"utid\":\"lsrgF2BcrDYCAT0zX8K67uS1\",\"client_ts\":%s,\"version\":\"2.1.63\",\"ckey\":\"DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND\"}","biz_params":"{\"vid\":\"%s\",\"play_ability\":16782592,\"preferClarity\":2,\"extag\":\"EXT-X-PRIVINF\",\"master_m3u8\":1,\"media_type\":\"standard,subtitle\",\"app_ver\":\"2.1.63\",\"h265\":1}","ad_params":"{\"vs\":\"1.0\",\"pver\":\"2.1.63\",\"sver\":\"2.0\",\"site\":1,\"aw\":\"w\",\"fu\":0,\"d\":\"0\",\"bt\":\"pc\",\"os\":\"win\",\"osv\":\"10\",\"dq\":\"auto\",\"atm\":\"\",\"partnerid\":\"null\",\"wintype\":\"interior\",\"isvert\":0,\"vip\":0,\"emb\":\"AjU4MzY1NjUxAnYueW91a3UuY29tAi92X3Nob3cvaWRfWE1qTXpORFl5TmpBMC5odG1s\",\"p\":1,\"rst\":\"mp4\",\"needbf\":2,\"avs\":\"1.0\"}"}'
YK_APPKEY = "24679788"
YK_URL = "https://acs.youku.com/h5/mtop.youku.play.ups.appinfo.get/1.1/"
YK_API = "mtop.youku.play.ups.appinfo.get"


def check_key(con, uri_dir):
  res = re.search(KEY_PATTERN, con)
  if res:
    print "Encrypt method: %s, Key uri: %s\n" % (res.group(1), res.group(2))
    url = "%s%s" % (uri_dir, res.group(2))
    print "URL: %s\n" % url
    req = requests.get(url)
    print "req: %s" % req.content
    ret = req.content
    req.close()
    return ret
  return ''


def get_cookie(gsb, c_time):
  params = {
    "appKey": YK_APPKEY,
    "api": YK_API,
    't': c_time,
  }
  headers = {
    'Referer':'https://v.youku.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  }
  req = gsb.get_req(YK_URL, params=params, headers=headers)
  print("get_cookie => req: [%s] \n cookie: [%s]" % (req.content, req.headers['Set-Cookie']))
  gsb.conf['cookie'] = req.headers['Set-Cookie']
  cookies = req.headers['Set-Cookie'].split(';')
  for k in cookies:
    k=k.strip()
    if k.startswith('_m_h5_tk'):
      m_h5_tk = k
    elif k.count('_m_h5_tk_enc'):
      m_h5_tk_enc = '_m_h5_tk_enc=%s' % k[k.find('=')+1:]
  gsb.conf['token'] = m_h5_tk[9:41]
  gsb.conf['cookie2'] = "; ".join([m_h5_tk, m_h5_tk_enc])
  print("token: %s" % gsb.conf['token'])

def generate_url(gsb, url, c_time):
  res = re.search('id_(.*?).html', url)
  if not res:
    print("no id found in url: %s" % url)
    return None
  vid = res.group(1)
  token = gsb.conf['token']
  #token = '7ef41aea2898f8c848f396b494c01b55'
  #cookie = gsb.conf['cookie']
  cookie = '__ysuid=1589183474621ZvU; cna=lsrgF2BcrDYCAT0zX8K67uS1; juid=01f377kmur2p0p; __ayft=1618371833369; __aysid=1618371833370szU; __ayscnt=1; __arycid=dg-1-00; __arcms=dg-1-00; modalFrequency={"UUID":"2"}; seid=01f39lsjelj3u; P_ck_ctl=6C5ED43870D7F4DFD963A6050C5135D0; referhost=http://i.youku.com; seidtimeout=1618455686812; __ayvstp=143; __aysvstp=143; isg=BLq6wao7jkJMWAKvkNgfCnttC-Dcaz5FT_NjFcSyoM0Yt1rxrPsaVVbGB0NrJ7bd; l=eBTbL4KHjw351Qz_BO5Zourza77tEIdb4sPzaNbMiInca6MFgFM8_NCQrdfwzdtjgt1EeetPg9-qKRLHR3AJwxDDBre9DJwInxf..; tfstk=cpDCBFmKmwbQy7RPLDtNUP0WJzwGa6L_jBaKAjNoXnVh-ElLWs4P3rOe0bbGBSE1.; rpvid=16184538910872GDiad-1618467659647; __arpvid=1618467674393ExpjxC-1618467674494; __aypstp=44; __ayspstp=44;'
  cookie = ';'.join([cookie, gsb.conf['cookie2']])
  #dat = DATA % (c_time[:-3], vid)
  dat = DATA % (c_time, vid)
  params = {
    "jsv" : "2.5.8",
    "appKey": YK_APPKEY,
    "t" : c_time,
    "sign" : md5("&".join([token, c_time, YK_APPKEY, dat])).hexdigest(),
    "api" : YK_API,
    "v" : "1.1",
    #"timeout": "20000",
    #"YKPid": '20160317PLF000211',
    #'YKLoginRequest': "true",
    #'AntiFlood': "true",
    #'AntiCreep': 'true',
    #'type': 'jsonp',
    #'dataType': 'jsonp',
    #'callback': 'mtopjsonp1',
    "data" : dat,
  }
  headers = {
    'Cookie': cookie,
    'Referer':'http://v.youku.com/v_show/id_%s.html'% vid,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  }
  print("params: %s" % pprint.pformat(params))
  print("headers: %s" % pprint.pformat(headers))
  return params, headers


def generate_youku_file(gsb, i=0, force=False, read_json=False):
  print "To generate a youku file:\n"
  if not read_json:
    c_time = str(int(time.time() * 1000))
    #c_time = "1618467677079"
    if 'token' not in gsb.conf:
      get_cookie(gsb, c_time)
    params, headers = generate_url(gsb, gsb.conf['src_url'][i], c_time)
    req = gsb.get_req(YK_URL, params=params, headers=headers)
    print "req: %s" % req
    print "req.content: %s" % req.content
    if req.status_code != 200:
      print "request failed: %s"
      return  False
    j = json.loads(req.content)
    if not j['ret'][0].startswith('SUCCESS') or "error" in j['data']['data']:
      print "api call failed!"
      return False
    i = gsb.get_base_sen_id()
    jsonf = os.path.join(gsb.store_dir, "%d.json" % i)
    f_youku = open(jsonf, 'wb')
    f_youku.write(req.content)
    f_youku.close()
  else:
    with open(os.path.join(gsb.store_dir, '%s.json' % i), 'rb') as f_json:
      j = json.load(f_json)
  index = 0
  outs = []
  name = re.sub('[\s()/]', '_', j['data']['data']['video']['title'])
  c_stream = list(map(lambda x: x['stream_type'], j['data']['data']['stream']))
  #stream_type = ['mp4hd2v2', 'mp4hd2', 'mp4hd', 'mp4sd', '3gphd', 'flvhd']
  try:
    stream_type = j['data']['data']['video']['stream_ext']['default']
    stream_type = sorted(stream_type,
                         key=lambda x: stream_type[x]['resolu'] * 100 + stream_type[x]['fps'] + stream_type[x]['size']/(2**34),
                         reverse=True)
    for stream in c_stream:
      if stream == stream_type[0]:
        break
      index += 1
  except KeyError, e:
    index = -1
    print("KeyError: %s" % e.message)
    pass
  if index in range(len(j['data']['data']['stream'])):
    url = j['data']['data']['stream'][index]['m3u8_url']
    print("Chosen stream: [%s], size[%.02fM], dur[%s], bitrate[%.02fkb/s]" % (
      j['data']['data']['stream'][index]['stream_type'],
      j['data']['data']['stream'][index]['size']/1024/1024,
      j['data']['data']['stream'][index]['milliseconds_video'],
      j['data']['data']['stream'][index]['size'] / j['data']['data']['stream'][index]['milliseconds_video'] * 1000 * 8 / 1024,
    ))
    req = gsb.get_req(url)
    print "url: %s" % url
    print "req: %s" % req
    if req.content.count('.ts'):
      m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
      f_m3u8 = open(m3u8, 'wb')
      f_m3u8.write(req.content)
      f_m3u8.close()
      outs.append("%d %s" % (i, name))
    else:
      for line in req.content.split('\n'):
        if not line.startswith("#"):
          req2 = gsb.get_req(url)
          print "req2: %s" % req2
          if req2:
            m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
            f_m3u8 = open(m3u8, 'wb')
            f_m3u8.write(req2.content)
            f_m3u8.close()
            outs.append("%d %s" % (i, name, ))
            req2.close()
          else:
            error = True
          break
  else:
    segs = list(map(lambda x: x['cdn_url'], j['data']['data']['stream'][0]['segs']))
    m3u8 = os.path.join(gsb.store_dir, "%d.m3u8" % i)
    f_m3u8 = open(m3u8, 'wb')
    f_m3u8.write('\n'.join(segs))
    f_m3u8.close()
    outs.append("%d %s" % (i, name,))
  print "\n".join(outs).encode('utf8')+"\n"
  print "outs: %s " % outs
  f_cctv5 = open(gsb.conf['sen_info_path'], 'a')
  f_cctv5.write("\n".join(outs).encode('utf8')+"\n")
  f_cctv5.close()
  return True


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
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  conf={'base_dir': r'E:\hzw',
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'key'],
                         'sen_info_path': 'sens_info_youku.txt',
                         'youku_info_path': 'youku_sens_info.txt',
                         'src_url': [
                           '//v.youku.com/v_show/id_XNDU3OTgwNTI0NA==.html',  # 葵葵爸爸 小达人京途毛毛虫点读笔铺码制作点读包 音频如何批量修改名字
                           '//v.youku.com/v_show/id_XNDU3OTcwNTE0MA==.html',  # 葵葵爸爸 小达人京途毛毛虫点读笔铺码 最简单的铺码教程
                           '//v.youku.com/v_show/id_XNDU3OTcwNDI5Ng==.html',
                           # 葵葵爸爸 小达人京途毛毛虫点读笔铺码合成点读包音频切割教程 'http://v.youku.com/v_show/id_XNDcwODg3ODE0MA==.html',  # 第25讲小达人毛毛虫京途点读笔点读笔图片铺码音频关系葵葵爸讲铺码

                         ],
                         'servers': '',
        'remove_ts': True,
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  is_get_url = 0
  if 1:
    if 1:
      for j in range(len(conf['src_url'])):
        #time.sleep(random.random()*10+2)
        if not generate_youku_file(th, j, True):
          exit(1)
          pass
    else:
      f_list = os.listdir(th.store_dir)
      json_list = list(filter(lambda x: x.endswith('.json'), f_list))
      for jsonf in json_list:
        generate_youku_file(th, int(jsonf.replace(".json", '')), True, True)
  if 1:
    th_list = [th]
    th.start()
    th = GetSensBase(conf)
    th_list.append(th)
    th.start()
    for th in th_list:
      th.join()
