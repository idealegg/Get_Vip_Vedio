# -*- coding:utf-8 -*-
import pprint
import re
import requests
import time
from hashlib import md5
from Util.myLogging import *
from Common.GetSensBase import GetSensBase


#ffmpeg -i http://www.xxx.com/xxx.m3u8 name.mp4
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
    logger.info("Encrypt method: %s, Key uri: %s\n" % (res.group(1), res.group(2)))
    url = "%s%s" % (uri_dir, res.group(2))
    logger.info("URL: %s\n" % url)
    req = requests.get(url)
    logger.info("req: %s" % req.content)
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
  logger.info("To generate a youku file:\n")
  if not read_json:
    c_time = str(int(time.time() * 1000))
    #c_time = "1618467677079"
    if 'token' not in gsb.conf:
      get_cookie(gsb, c_time)
    params, headers = generate_url(gsb, gsb.conf['src_url'][i], c_time)
    req = gsb.get_req(YK_URL, params=params, headers=headers)
    logger.info("req: %s" % req)
    logger.info("req.content: %s" % req.content)
    if req.status_code != 200:
      logger.info("request failed: %s")
      return  False
    j = json.loads(req.content)
    if not j['ret'][0].startswith('SUCCESS') or "error" in j['data']['data']:
      logger.info("api call failed!")
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
    if gsb.conf['direct_download_m3u8']:
      cmd = 'avconv -i "%s" -c copy %s' % (url, os.path.join(gsb.target_dir, "%s.mp4" % name))
      ret = os.system(cmd)
      return ret == 0
    req = gsb.get_req(url)
    logger.info("url: %s" % url)
    logger.info("req: %s" % req)
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
          logger.info("req2: %s" % req2)
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
  logger.info("\n".join(outs).encode('utf8')+"\n")
  logger.info("outs: %s " % outs)
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
  setup_logging()
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  conf={'base_dir': r'E:\hzw',
        'direct_download_m3u8': True,
                         'check_downloaded_retry': 5,
                         'session_number': 4,
                         'threading_num': 6,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'key'],
                         'sen_info_path': os.path.join(conf_dir,'sens_info_youku.txt'),
                         'youku_info_path': os.path.join(conf_dir,'youku_sens_info.txt'),
                         'src_url': [
                            # "http://v.youku.com/v_show/id_XMjMzNDYyNjA0.html",  # 【09dota提高班】顶着延迟加卡的蝴蝶小强 52:25
                           # "http://v.youku.com/v_show/id_XMjM2NDIyMTA4.html",  # yy2009开业活动录音内有09的演讲 01:34:22
                           #  "http://v.youku.com/v_show/id_XMjM2NjY1NDY4.html",  # 【09dota提高班】速成输出王黑鸟 01:00:44
                           # "http://v.youku.com/v_show/id_XMjM3MzkyNDY4.html",  # 【2009讲dota】P神影魔B神水人年终决战 01:03:13
                           # "http://v.youku.com/v_show/id_XMjM4MTYzMjY4.html",  # 【dota心态篇】面对外挂和冤枉，要淡定 46:51
                           # "http://v.youku.com/v_show/id_XMjQwNzY5MDQw.html",  # 【09dota提高班】蚂蚁-新版本Carry英雄的首选？ 55:24
                           # "http://v.youku.com/v_show/id_XMjQyODM3ODI0.html",  # 【09dota提高班】WE新人的犀利狗和09的稳重狗 01:32:38
                           # "http://v.youku.com/v_show/id_XMjQzMDY4ODE2.html",  # 【09dota解说】DK三人组的路人之旅 58:03
                           # "http://v.youku.com/v_show/id_XMjQ0MzQ1ODIw.html",  # 【09dota解说】WE内部训练赛 01:15:30
                           # "http://v.youku.com/v_show/id_XMjQ1MTk0MTI4.html",  # 【09dota解说】2011的第一个冠军花落谁家？ 02:00:13
                           # "http://v.youku.com/v_show/id_XMjQ2OTgzMDc2.html",  # 【09dota提高班】多变的收割机"痛苦女王" 01:24:26
                           # "http://v.youku.com/v_show/id_XMjQ3MTAwMzIw.html",  # 【09dota提高班】54分钟42杀的痛苦女王 57:59
                           # "http://v.youku.com/v_show/id_XMjUwMTI2NzM2.html",  # 【09dota解说】CHUAN神霸气SF领衔WE对LGD秘密训练赛 01:26:21
                           # "http://v.youku.com/v_show/id_XMjUyNDE2MzIw.html",  # 【09dota提高班】死灵龙一样打C，内有09献歌 01:21:30
                           # "http://v.youku.com/v_show/id_XMjU1MDA4NzQ0.html",  # 【09dota解说】大马决赛CCM.CN上演太极 47:41
                           # "http://v.youku.com/v_show/id_XMjU2MTQ5ODE2.html",  # 【09dota超清提高班】帅气敌法篇，内有sky表演魔术 01:00:36
                           # "http://v.youku.com/v_show/id_XMjU3NTg0MDYw.html",  # 【09dota超清提高班】蝙蝠骑士的妖娆火焰 52:37
                           # "http://v.youku.com/v_show/id_XMjU3ODcxMzEy.html",  # 【09dota记录片】ACG2008的回忆 05:57
                           # "http://v.youku.com/v_show/id_XMjU4OTc2ODUy.html",  # 【09dota提高班】VIPER的单杀是一种信仰 47:05
                           # "http://v.youku.com/v_show/id_XMjU5NDk4Njky.html",  # 【09dota解说】转会风波主角线下大赛碰头EHvsDK 49:51
                           # "http://v.youku.com/v_show/id_XMjU5NzkzNTU2.html",  # 【09dota超清提高班】暴力火卡 01:06:57
                           # "http://v.youku.com/v_show/id_XMjYwNzA4ODQ4.html",  # 【09dota超清提高班】恶魔巫师 02:13:06
                           # "http://v.youku.com/v_show/id_XMjYyMjY4MTIw.html",  # 【09dota提高班】山岭巨人第一视角 36:04
                           # "http://v.youku.com/v_show/id_XMjYyOTY1MjEy.html",  # 【09dota提高班】巫医第一视角 01:28:17
                           # # "http://v.youku.com/v_show/id_XMjYzNzUxMTQ0.html",  # 【09dota超清提高班】压制流敌法 43:57
                           # "http://v.youku.com/v_show/id_XMjY0NjY4OTc2.html",  # 【09dota提高班】月之女祭司 01:02:48
                           # "http://v.youku.com/v_show/id_XMjY1MjUwNzky.html",  # 【09dota超清提高班】月之骑士 01:43:58
                           # # "http://v.youku.com/v_show/id_XMjY2NDM1Njk2.html",  # 【09dota超清提高班】纯爷们第一视角 01:15:08
                           # # "http://v.youku.com/v_show/id_XMjY2ODIyMjAw.html",  # 【09dota超清提高班】曾经第一后期黑弓 01:16:32
                           # "http://v.youku.com/v_show/id_XMjY3OTk5MDEy.html",  # 【09dota提高班】疯脸小黑和30分钟三圣剑PA 01:19:34
                           # # "http://v.youku.com/v_show/id_XMjY4NjkxNjAw.html",  # 【09dota提高班】 疯狂的死骑和多舛的赏金 01:20:29
                           # # "http://v.youku.com/v_show/id_XMjY5ODQyMjU2.html",  # 【09dota提高班】嘲讽猎人和精打细算猫 01:33:22
                           # # "http://v.youku.com/v_show/id_XMjcwMjgyMDI0.html",  # 【09dota纪录片】2009_THE_MOVIE 12:09
                           # "http://v.youku.com/v_show/id_XMjcyNTc0MTU2.html",  # 【09dota提高班】无与伦比的华丽风行 01:29:33
                           # "http://v.youku.com/v_show/id_XMjc1MDU2NDYw.html",  # 【09dota开黑篇】2次暴走的4圣剑敌法 01:02:57
                           # # "http://v.youku.com/v_show/id_XMjc1MTI1NjAw.html",  # 【09dota开黑篇】电猫毒蛇和山岭 02:17:22
                           # # "http://v.youku.com/v_show/id_XMjc1NTQzODgw.html",  # 【09dota解说】STARWAR上EHOME的龙7表演 01:08:27
                           # # "http://v.youku.com/v_show/id_XMjc4MzYzMDA0.html",  # 【09dota提高班】风行者完结篇 01:37:47
                           # # "http://v.youku.com/v_show/id_XMjgwNzk3ODI4.html",  # 【09dota提高班】复仇之魂 01:54:13
                           # # "http://v.youku.com/v_show/id_XMjgzMDc3NzQ0.html",  # 【09dota解说】G-1年度经典WE对DK 01:16:18
                           # # "http://v.youku.com/v_show/id_XMjgzMDc3Nzc2.html",  # 【09dota解说】G-1年度经典WE对DK 2 01:08:49
                           # # "http://v.youku.com/v_show/id_XMjgzMDc3ODU2.html",  # 【09dota解说】G-1年度经典WE对DK 3 01:27:47
                           # # "http://v.youku.com/v_show/id_XMjgzNjM1Nzgw.html",  # 【09dota解说】LGD对WE 2 51:26
                           # # "http://v.youku.com/v_show/id_XMjgzNjM0MDgw.html",  # 【09dota解说】LGD对WE 1 01:01:24
                           # # "http://v.youku.com/v_show/id_XMjgzNjM2Mjg4.html",  # 【09dota解说】LGD对WE 3 01:03:56
                           # "http://v.youku.com/v_show/id_XMjgzNjM1Nzg0.html",  # 【09dota第一视角】宙斯兽王屠夫 02:08:55
                           # "http://v.youku.com/v_show/id_XMjgzNjM1Mzky.html",  # 【09dota第一视角】亚龙蚂蚁火女 02:30:34
                           # # "http://v.youku.com/v_show/id_XMjg1ODQyMzc2.html",  # 【09dota提高班】巨魔战将(troll) 01:33:03
                           # # "http://v.youku.com/v_show/id_XMjg2MTYwNzY0.html",  # 【09dota提高班】沙王（SK） 01:38:48
                           # # "http://v.youku.com/v_show/id_XMjg5NDIxOTIw.html",  # 【09dota提高班】狼人Lycan 01:25:20
                           # "http://v.youku.com/v_show/id_XMjg5NDI4MDgw.html",  # 【09dota解说】PDL半决赛LGDvsTYLOO 02:38:57
                           # "http://v.youku.com/v_show/id_XMjkzNTkxNzg0.html",  # 【09dota提高班】混沌骑士（CK） 01:37:40
                           # "http://v.youku.com/v_show/id_XMjk0ODkxNDky.html",  # 【09dota解说】曾经的LGD对上越南全明星 01:07:02
                           # "http://v.youku.com/v_show/id_XMjk4NzA0NDcy.html",  # 【09dota提高班】先知(Furion)上集 57:51
                           # "http://v.youku.com/v_show/id_XMjk4NzA3NTQ4.html",  # 【09dota提高班】先知(Furion)下集 01:28:49
                           # "http://v.youku.com/v_show/id_XMjk5MjA5OTk2.html",  # 【09dota提高班】末日使者（DOOM） 01:03:43
                           # "http://v.youku.com/v_show/id_XMzAxMzc5OTEy.html",  # 【09dota提高班】冥界亚龙（VIPER） 01:52:11
                           # "http://v.youku.com/v_show/id_XMzA0NDczMDg4.html",  # 【09dota提高班】隐形刺客（SA） 55:08
                           # "http://v.youku.com/v_show/id_XMzA1NjIwMDY0.html",  # 【09dota提高班】艾瑞达（SD） 55:21
                           # "http://v.youku.com/v_show/id_XMzA4NDQ5Mjg4.html",  # 【09dota提高班】风暴之灵（ST） 01:04:56
                           # "http://v.youku.com/v_show/id_XMzA4ODYxNzg4.html",  # 【09dota水友秀】酱油不是不能亮，只是不好赢 01:17:11
                           # "http://v.youku.com/v_show/id_XMzA5MDYzMDAw.html",  # 【09dota提高班】电猫紫苑篇（真人出镜） 01:27:40
                           # "http://v.youku.com/v_show/id_XMzExMDYxNDY0.html",  # 【09dota提高班】暗夜魔王（NS） 01:25:27
                           # "http://v.youku.com/v_show/id_XMzEzMjUyOTY0.html",  # 【09dota提高班】黑鸟（OD） 01:34:10
                           # "http://v.youku.com/v_show/id_XMzE1NTUxMTI4.html",  # 【09dota视频解说】WEvsTongFu 01:27:50
                           # "http://v.youku.com/v_show/id_XMzE1NTQ5ODE2.html",  # 【09dota视频解说】IG.ZvsPanda 01:41:54
                           # "http://v.youku.com/v_show/id_XMzE1Nzg1NzMy.html",  # 【09dota提高班】幽鬼（spectre） 01:35:51
                           # "http://v.youku.com/v_show/id_XMzE3NDQ5MzE2.html",  # 【09dota视频解说】IG.YvsWE 57:07
                           # "http://v.youku.com/v_show/id_XMzE5NzgzMTEy.html",  # 【09dota提高班】剑圣（JUGG） 01:19:51
                           # "http://v.youku.com/v_show/id_XMzIwMjM1MjQ4.html",  # 【09dota视频解说】DK vs Nv.cn_完整版！G1联赛总决赛 03:47:30
                           # "http://v.youku.com/v_show/id_XMzIyNjc2Nzky.html",  # 【09dota提高班】牛头人酋长（TC） 01:24:15
                           # "http://v.youku.com/v_show/id_XMzI1ODM3Nzg4.html",  # 【09dota提高班】渔人守卫（SG） 01:46:47
                           # "http://v.youku.com/v_show/id_XMzI3NDE2MzQ0.html",  # 【09寻梦水友赛】第一周拍拍小强 01:47:18
                           # "http://v.youku.com/v_show/id_XMzI5NDE5NDY0.html",  # 【09dota提高班】地穴编织者（NW） 01:19:12
                           # "http://v.youku.com/v_show/id_XMzI5ODAxOTcy.html",  # 【09寻梦水友赛】第二周月女虚空 01:25:15
                           # "http://v.youku.com/v_show/id_XMzMyMDYyNzg0.html",  # 【09dota提高班】暗影萨满 ( SS ) 01:49:16
                           # "http://v.youku.com/v_show/id_XMzMzOTYyMzM2.html",  # 【09dota提高班】全能骑士 (OK) 01:22:39
                           # "http://v.youku.com/v_show/id_XMzM0NzcxMTE2.html",  # 【09dota提高班】混沌骑士 (CK) 01:40:54
                           # "http://v.youku.com/v_show/id_XMzM0OTM1NzQw.html",  # 【09dota视频解说】送水队和妖刀的妖怪水人 01:27:31
                           # "http://v.youku.com/v_show/id_XMzM1NDYxODQ0.html",  # 【09dota解说】(无遮挡版)送水队和妖刀水人 01:27:31
                           # "http://v.youku.com/v_show/id_XMzM2NzQ3NDUy.html",  # 【09dota提高班】灰烬之灵 (EM) 01:23:05
                           # "http://v.youku.com/v_show/id_XMzM4NjczNTU2.html",  # 【09dota提高班】地精撕裂者 (GS) 01:53:52
                           # "http://v.youku.com/v_show/id_XMzQyNDkyMTg0.html",  # 【09dota提高班】育母蜘蛛 (BR) 01:32:23
                           # "http://v.youku.com/v_show/id_XMzQyOTgyNjg0.html",  # 【09dota视频解说】DK vs Panda 01:16:25
                           # "http://v.youku.com/v_show/id_XMzQzNTkyMjY0.html",  # 【09dota提高班】军团指挥官 (LC)  01:55:37
                           # "http://v.youku.com/v_show/id_XMzQ1MzE3MjAw.html",  # 【09dota提高班】爱人直升机(GY) 34:41
                           # "http://v.youku.com/v_show/id_XMzQ1Mzc1MjUy.html",  # 【09dota开黑第一视角】虚灵BR和萨尔 58:32
                           # "http://v.youku.com/v_show/id_XMzQ4NDgyODMy.html",  # 【09dota提高班】虚空假面（FV） 01:04:58
                           # "http://v.youku.com/v_show/id_XMzUwNjQyNTky.html",  # 【09dota提高班】潮汐猎人（TH） 01:31:31
                           # "http://v.youku.com/v_show/id_XMzUwODYyNTI0.html",  # 【09dota第一视角】亚龙蚂蚁 01:15:48
                           # "http://v.youku.com/v_show/id_XMzUxNjQzMDc2.html",  # 【09dota提高班】血魔（BS） 48:51
                           # "http://v.youku.com/v_show/id_XMzU1NDY2MDM2.html",  # 【09dota提高班】月之女祭司（Pom） 01:24:08
                           # "http://v.youku.com/v_show/id_XMzU2Mjk5MTUy.html",  # 【09dota提高班】痛苦之源（Bane） 01:32:26
                           # "http://v.youku.com/v_show/id_XMzU4NDQwNTky.html",  # [众神之夜]暗夜魔王(NS) 58:35
                           # "http://v.youku.com/v_show/id_XMzU5NTY0NjUy.html",  # 【09dota第一视角】小鹿和修补 46:09
                           # "http://v.youku.com/v_show/id_XMzYwMTYyNjMy.html",  # [众神之夜]暗影萨满（SS） 01:18:44
                           # "http://v.youku.com/v_show/id_XMzYwOTQxNjM2.html",  # G-1 iG vs WE 2 01:08:59
                           # "http://v.youku.com/v_show/id_XMzYxMDA1MTk2.html",  # 【09omg第一视角】全明星(hao,mu,820,830,dd,faith,dc,xl) 01:30:35
                           # "http://v.youku.com/v_show/id_XMzYwOTQxODM2.html",  # G-1 iG vs WE 3 01:28:13
                           # "http://v.youku.com/v_show/id_XMzYyMTk3MjUy.html",  # [众神之夜]地穴编织者(NW)_xiao8 01:44:20
                           # "http://v.youku.com/v_show/id_XMzYzMDM3MzQw.html",  # G-1激情团战一波三折 DK vs LGD 2 01:08:20
                           # "http://v.youku.com/v_show/id_XMzYzMDM3ODY0.html",  # G-1八导再秀QOP之役 LGD vs WE 1 01:06:11
                           # "http://v.youku.com/v_show/id_XMzYzMDM4MTI0.html",  # 《怒放中前行》G-1冠军联赛VCR 02:03
                           # "http://v.youku.com/v_show/id_XMzYzMDM1ODAw.html",  # G-1霸气PUSH先下一城 DK vs LGD 1 43:28
                           # "http://v.youku.com/v_show/id_XMzYzMDM2NTI4.html",  # G-1德鲁伊体系的破绽 DK vs LGD 3 43:22
                           # "http://v.youku.com/v_show/id_XMzYzMDM4NDYw.html",  # G-1超神冰魂闪亮4号位 LGD vs WE 2 01:05:28
                           # "http://v.youku.com/v_show/id_XMzY0NzIyMDMy.html",  # [众神之夜]兽王(BM)_xiao8 53:20
                           # "http://v.youku.com/v_show/id_XMzY2ODc4OTI4.html",  # 【09dota提高班】召唤师（Kael）  50:59
                           # "http://v.youku.com/v_show/id_XMzY5MzY5OTQ4.html",  # 【09dota第一视角】圣堂老鹿 01:43:45
                           # "http://v.youku.com/v_show/id_XMzcwNTg5MzQ4.html",  # [众神之夜]鱼人守卫（Slardar）Burning 43:39
                           # "http://v.youku.com/v_show/id_XMzczMzMyMzUy.html",  # 【09dota提高班】天怒法师(SM) 01:52:54
                           # "http://v.youku.com/v_show/id_XMzc0OTM3Nzg0.html",  # DK vs WE 01:15:38
                           # "http://v.youku.com/v_show/id_XMzc3MjAxOTY0.html",  # 【09dota第一视角】熊猫酒仙和风暴之灵 01:32:27
                           # "http://v.youku.com/v_show/id_XMzgwODM3MzI4.html",  # 【09dota提高班】水晶室女（CM） 01:38:04
                           # "http://v.youku.com/v_show/id_XMzgxOTY1MTQ4.html",  # 【09dota第一视角】月之骑士和暗影牧师 01:26:20
                           # "http://v.youku.com/v_show/id_XMzg0NjA5NDA4.html",  # 【09dota第一视角】巫妖和鱼人夜行者 52:22
                           # "http://v.youku.com/v_show/id_XMzg5MDI5OTIw.html",  # 【09dota提高班】地穴编制者（NW） 01:51:46
                           # "http://v.youku.com/v_show/id_XMzkxNjQzMDMy.html",  # 【09dota第一视角】极寒幽魂和剑圣 54:55
                           # "http://v.youku.com/v_show/id_XNDAwMDI5NTIw.html",  # 【09dota解说】电锤的逆转 01:17:34
                           # "http://v.youku.com/v_show/id_XNDAyNjAyMzA4.html",  # 【09dota第一视角】黑暗贤者(DS)和血魔(BS) 01:10:41
                           # "http://v.youku.com/v_show/id_XNDA0NDQ3MDEy.html",  # 【09dota解说】CW讲解黑鸟篇 53:37
                           # "http://v.youku.com/v_show/id_XNDA5NTc4ODEy.html",  # 【09dota提高班】仙女龙(PUCK) 01:37:31
                           # "http://v.youku.com/v_show/id_XNDE0MDM4MzEy.html",  # 【09dota第一视角】痛苦女王 01:09:33
                           # "http://v.youku.com/v_show/id_XNDE3NTEyMzEy.html",  # 【09dota第一视角】潮汐龙骑合集 01:12:03
                           # "http://v.youku.com/v_show/id_XNDIzMDgzMTI4.html",  # 【09dota提高班】死亡先知（DP） 54:30
                           # "http://v.youku.com/v_show/id_XNDI0MDE4MjA4.html",  # 【09dota第一视角】火女小鱼人 01:30:10
                           # "http://v.youku.com/v_show/id_XNDI0Nzc0NjE2.html",  # 【09dota第一视角】天怒沙王合集 01:11:39
                           # "http://v.youku.com/v_show/id_XNDI1NzQ1OTc2.html",  # 【09dota2解说】LGD对ZENITH 01:47:51
                           # "http://v.youku.com/v_show/id_XNDI5MTM3NzI0.html",  # 【09dota提高班】影魔（NEVERMORE） 01:08:07
                           # "http://v.youku.com/v_show/id_XNDMwNjI5ODcy.html",  # 【09dota2解说】DK对ORANGE mushi超神秀 01:19:36
                           # "http://v.youku.com/v_show/id_XNDM0MjY3NDc2.html",  # 【09dota提高班】圣堂刺客(TA) 01:30:27
                           # "http://v.youku.com/v_show/id_XNDM1NDk1Nzk2.html",  # 【09dota第一视角】流浪剑客（SVEN） 01:02:58
                           # "http://v.youku.com/v_show/id_XNDM1OTAyNjE2.html",  # 【09dota第一视角】多折的痛苦女王 01:19:24
                           # "http://v.youku.com/v_show/id_XNDM3NzIzMDY4.html",  # 【09dota2解说】MM半决赛LGD对IG 01:54:23
                           # "http://v.youku.com/v_show/id_XNDQwMjk1OTA4.html",  # 【09dota提高班】1v5的诀窍（女王影魔） 01:20:56
                           # "http://v.youku.com/v_show/id_XNDQyMjYzNTUy.html",  # DOTA2 BTS 01:48:06
                           # "http://v.youku.com/v_show/id_XNDQzNjUzNDU2.html",  # 【09dota2解说】LGD对ZENITH，西雅图小组赛 29:39
                           # "http://v.youku.com/v_show/id_XNDQzNjU0NDA4.html",  # 【09dota2解说】IG对NAVI，西雅图小组赛 01:15:04
                           # "http://v.youku.com/v_show/id_XNDQzODk1NDcy.html",  # 【09dota2解说】IG对EHOME，西雅图小组赛 29:54
                           # "http://v.youku.com/v_show/id_XNDQ0MTE2OTYw.html",  # 【09dota2解说】西雅图小组赛第二天 02:21:45
                           # "http://v.youku.com/v_show/id_XNDQ0NDAzNzQ4.html", # 【09dota2解说】小组赛第三天Tongfu和EHOME的最后命运 01:53:03
                           # "http://v.youku.com/v_show/id_XNDQ4MDk2ODA4.html",  # 【09dota第一视角】恶巫，魂守，修补 01:32:04
                           # "http://v.youku.com/v_show/id_XNDQ5MDEyMzA0.html",  # 【09dota提高班】月之骑士2（luna ) 01:39:36
                           # "http://v.youku.com/v_show/id_XNDUxNTc5Nzky.html",  # 【09dota第一视角】宙斯，小鹿，毒狗 01:21:17
                           # "http://v.youku.com/v_show/id_XNDUzOTg0NjE2.html",  # 【09dota提高班】黑暗贤者(DS) 01:42:51
                           # "http://v.youku.com/v_show/id_XNDU2NTU4OTMy.html",  # 【09dota提高班】猴子 01:53:18
                           # "http://v.youku.com/v_show/id_XNDU3NTA3MDQ4.html",  # 【09dota提高班】弧光守望者 02:13:26
                           # "http://v.youku.com/v_show/id_XNDU4OTY2MTg0.html",  # 【09dota第一视角】赏金和蚂蚁 01:11:01
                           # "http://v.youku.com/v_show/id_XNDYzMDI3MTI4.html",  # 【09dota第一视角】DPS型LINA 01:04:12
                           # "http://v.youku.com/v_show/id_XNDYzOTM3MTgw.html",  # 【09dota第一视角】小强，剧毒 01:22:02
                           # "http://v.youku.com/v_show/id_XNDY0MTYxMTQ0.html",
                           # # 【09dota解说】天才少年SOLO赛430VS夜夜笙歌，AIRvs杀意来袭 01:28:25
                           # "http://v.youku.com/v_show/id_XNDY0NjUyODcy.html",
                           # # 【09dota解说】天才少年SOLO赛HAOvsSTICK,小乖vs你咬我呀 01:47:15
                           # "http://v.youku.com/v_show/id_XNDY2MDc2MDcy.html",
                           # # 【09dota解说】天才少年SOLO赛sumnusm和sylar登场，妖刀对决CTY 02:04:36
                           # "http://v.youku.com/v_show/id_XNDY2ODE0Mjcy.html",  # 【09dota第一视角】死亡骑士美杜莎 01:19:15
                           # "http://v.youku.com/v_show/id_XNDcwMDU3NjQ4.html",  # 【09dota提高班】冥界亚龙2(viper) 01:33:21
                           # "http://v.youku.com/v_show/id_XNDcwNTcwNzYw.html",  # 【09dota解说】天才少年杯solo赛Air对Mu 47:41
                           # "http://v.youku.com/v_show/id_XNDcwODkyMDE2.html",  # 【09dota解说】solo大赛Sumnus丶M对430 01:11:13
                           # "http://v.youku.com/v_show/id_XNDczNjY1MzE2.html",  # 【09dota第一视角】痛苦女王，风暴之灵 01:36:30
                           # "http://v.youku.com/v_show/id_XNDczNjkxNTgw.html",  # 【09dot解说】solo赛cty对sylar 01:00:20
                           # "http://v.youku.com/v_show/id_XNDczNzY4MDMy.html",  # 【09dota第一视角】拉比克，龙骑士 01:33:58
                           # "http://v.youku.com/v_show/id_XNDc1NjE2OTM2.html",  # 【09dota提高班】中单猛犸（上） 01:04:48
                           # "http://v.youku.com/v_show/id_XNDc1NjE1NjE2.html",  # 【09dota提高班】中单猛犸（下） 01:28:01
                           # "http://v.youku.com/v_show/id_XNDc4OTk2ODky.html",  # 【09dota第一视角】黑鸟吐槽班 01:06:14
                           # "http://v.youku.com/v_show/id_XNDc5MDgxODc2.html",  # 【09dota解说】天才少年杯CTY对SUMNUSM 24:54
                           # "http://v.youku.com/v_show/id_XNDc5MTk2NDAw.html",  # 【09dota解说】天才少年杯妖刀对MU 01:06:04
                           # "http://v.youku.com/v_show/id_XNDgxMjc0NDYw.html",  # 【09dota提高班】魅惑魔女（小鹿EH） 53:29
                           # "http://v.youku.com/v_show/id_XNDgxMzQ0MzY4.html",  # 【09dota提高班】沉默术士（sil） 01:12:16
                           # "http://v.youku.com/v_show/id_XNDg0NjYxOTU2.html",  # 【09dota第一视角】月骑黑弓 01:20:11
                           # "http://v.youku.com/v_show/id_XNDg1ODg2Mzc2.html",  # 【09dota解说】天才少年杯SOLO赛决赛 59:41
                           # "http://v.youku.com/v_show/id_XNDg3MTE0MjA0.html",  # 【09dota提高班】沉默亚龙骨弓法球流 01:43:42
                           # "http://v.youku.com/v_show/id_XNDkwMzc0NDky.html",  # 【09dota提高班】新版黑弓高分局 01:39:53
                           # "http://v.youku.com/v_show/id_XNDkyOTI5NTk2.html",  # 【09dota第一视角】无力回天VP和误打误撞JUGG 01:45:42
                           # "http://v.youku.com/v_show/id_XNDk0Njc5NDU2.html",  # 【09dota提高班】翻盘，翻盘 01:44:13
                           # "http://v.youku.com/v_show/id_XNDk4NzcxNTYw.html",  # 【09dota提高班】绿鞋全能冲脸流 01:08:50
                           # "http://v.youku.com/v_show/id_XNDk5NDMwNDc2.html",  # 【09dota提高班】逆袭型辅助 01:33:27
                           # "http://v.youku.com/v_show/id_XNDk5ODY2ODQ4.html",  # 【09dota第一视角】辅助流LINA 01:41:25
                           # "http://v.youku.com/v_show/id_XNTAyOTk4NDA4.html",  # 【09dota提高班】山岭巨人第二视角 01:55:58
                           # "http://v.youku.com/v_show/id_XNTAzODk0Mzg0.html",  # 【09dota解说】水友的圣剑翻盘超级兵 01:23:06
                           # "http://v.youku.com/v_show/id_XNTA2NzUwNjA4.html",  # 【09dota提高班】虐心的痛苦之源 02:17:55
                           # "http://v.youku.com/v_show/id_XNTA3OTc1ODEy.html",  # 【09dota提高班】月骑太爽了 01:27:17
                           # "http://v.youku.com/v_show/id_XNTA4OTEzNTky.html",  # 【09dota从零单排1】劣势路无解肥混沌 38:40
                           # "http://v.youku.com/v_show/id_XNTA5MjUxNDUy.html",  # 【09dota从零单排2-4】亚龙LION赏金 01:13:56
                           # "http://v.youku.com/v_show/id_XNTA5NTc3MDky.html",  # 【09dota从零单排5-6】疯狂骨法和PUCK 01:11:38
                           # "http://v.youku.com/v_show/id_XNTA5OTkwMTQ0.html",  # 【09dota从零单排7-8】修补和翻身老鹿 01:04:24
                           # "http://v.youku.com/v_show/id_XNTExMTUxMzY4.html",  # 【09dota从零单排9-10】小鱼痛苦之源 01:10:30
                           # "http://v.youku.com/v_show/id_XNTExNDAzMjI0.html",  # 【09dota从零单排11-12】圣堂恶魔巫师 01:17:14
                           # "http://v.youku.com/v_show/id_XNTExNzM1NjMy.html",  # 【09dota从零单排13-14】回来复仇的恶魔巫师的队友 53:57
                           # "http://v.youku.com/v_show/id_XNTEyMTc5MTIw.html",  # 【09dota从零单排15】兽王 56:06
                           # "http://v.youku.com/v_show/id_XNTEyNjAyNTYw.html",  # 【09dota从零单排16】修补匠(TINKER) 59:44
                           # "http://v.youku.com/v_show/id_XNTEyNjQ0MDQ4.html",  # 【09dota从零单排17-19】老鹿(TS) 01:17:24
                           # "http://v.youku.com/v_show/id_XNTEyNzMxNDU2.html",  # 【09dota从零单排20】影魔(SF) 55:07
                           # "http://v.youku.com/v_show/id_XNTEyODkzNzU2.html",  # 【09dota从零单排21】仙女龙(PUCK) 52:04
                           # "http://v.youku.com/v_show/id_XNTE1MjY2NDI4.html",  # 【09dota从零单排22】暗影牧师（SP） 46:23
                           # "http://v.youku.com/v_show/id_XNTE2MjA0Nzcy.html",  # 【09dota从零单排23】男人的故事 54:13
                           # "http://v.youku.com/v_show/id_XNTE3NzczMDE2.html",  # 【09dota从零单排24-26】bsthsil还有献歌 02:06:11
                           # "http://v.youku.com/v_show/id_XNTIwNjc4MzQ4.html",  # 【09dota从零单排27-28】剧毒赏金 01:51:19
                           # "http://v.youku.com/v_show/id_XNTIxMzAzMzg0.html",  # 【09dota寻梦水友赛】伐木机女王 01:38:23
                           # "http://v.youku.com/v_show/id_XNTIzNDMyMDk2.html",  # 【09dota从零单排】29-31骨法小鱼流浪 01:24:21
                           # "http://v.youku.com/v_show/id_XNTI0NzE2MDA0.html",  # 【09DOTA从零单排】32-33老鹿沉默 01:03:46
                           # "http://v.youku.com/v_show/id_XNTI3MTg1MzQw.html",  # 【09DOTA从零单排】34电魂 46:38
                           # "http://v.youku.com/v_show/id_XNTI5MzM3NDY0.html",  # 【09DOTA从零单排】35-36沉默的独白 01:43:56
                           # "http://v.youku.com/v_show/id_XNTMwOTU3NDc2.html",  # 【09DOTA零单第二季】1-2船长和劣势路1V9的 01:38:24
                           # "http://v.youku.com/v_show/id_XNTMzMTkyNDk2.html",  # 【09DOTA零单第二季】3-5tiny/bane/nec 01:19:12
                           # "http://v.youku.com/v_show/id_XNTM0ODUwMzU2.html",  # 【09DOTA零单第二季】6-7卡尔蚂蚁 01:14:02
                           "http://v.youku.com/v_show/id_XNTM4Mzg1Njcy.html",  # 【09dota零单第二季】拉比克，龙鹰，蝙蝠 01:54:45
                           "http://v.youku.com/v_show/id_XNTQxNDA5ODU2.html",  # 【09dota零单第二季】11-13暗夜魔王 02:10:32
                           "http://v.youku.com/v_show/id_XNTQyNzgzNzY0.html",  # 【09dota零单第二季】14-15大酒神之根？ 01:15:14
                           "http://v.youku.com/v_show/id_XNTQ1NTM0MzQ0.html",  # 【09DOTA零单第二季】16-18SNK,BH,LUNA 02:12:10
                           "http://v.youku.com/v_show/id_XNTQ4Mzk3NDI0.html",  # 【09dota零单第二季】19-20伐木机，神灵！（其实不是） 01:15:08
                           "http://v.youku.com/v_show/id_XNTQ4ODgwODUy.html",  # 【09dota零单第二季】21,22混沌蝙蝠 59:00
                           "http://v.youku.com/v_show/id_XNTQ5MzkwODMy.html",  # 【09dota零单第二季】23大后期的故事 01:01:31
                           "http://v.youku.com/v_show/id_XNTUxMzIzMzc2.html",  # 【09DOTA零单第二季】24-26小黑影魔骨弓 01:46:09
                           "http://v.youku.com/v_show/id_XNTU0MzM1NDY0.html",  # 【09DOTA零单第二季】27影魔 01:21:59
                           "http://v.youku.com/v_show/id_XNTU1MjY0NTU2.html",  # 【09DOTA零单第二季】28人马 01:07:54
                           "http://v.youku.com/v_show/id_XNTU4MDQ5ODY0.html",  # 【09DOTA零单第二季】29-30神灵电猫 01:32:46
                           "http://v.youku.com/v_show/id_XNTU4OTgxNjIw.html",  # 【09DOTA零单第二季】31-32赏金冰魂 41:26
                           "http://v.youku.com/v_show/id_XNTYwODUyNTA4.html",  # 【09DOTA零单第二季】33-34宙斯电狗 01:47:16
                           "http://v.youku.com/v_show/id_XNTYzMTM5NDA4.html",  # 【09DOTA零单第二季】35坚强的圣堂刺客 01:22:38
                           "http://v.youku.com/v_show/id_XNTY0MzYwODYw.html",  # 【09DOTA零单第二季】36顺风斧王 46:04
                           "http://v.youku.com/v_show/id_XNTY2NTg4NDky.html",
                           # 【09DOTA零单第二季】37-38先知女王（内附新版本讲解） 02:16:26
                           "http://v.youku.com/v_show/id_XNTY4NDIzOTYw.html",  # 【09DOTA零单第二季】39-40飞机巨魔 01:46:19
                           "http://v.youku.com/v_show/id_XNTcwNjE5OTQ0.html",  # 【09DOTA零单第二季】41-42山岭黑鸟 01:17:15
                           "http://v.youku.com/v_show/id_XNTczMTg0NDc2.html",  # 【09DOTA零单第二季】43-44血魔痛苦之源 01:18:49
                           "http://v.youku.com/v_show/id_XNTc0MDQ3NTcy.html",  # 【09DOTA零单第二季】45水人！ 01:21:27
                           "http://v.youku.com/v_show/id_XNTc2NTk4NjM2.html",  # 【09DOTA零单第二季】46-47神灵熊德 01:37:18
                           "http://v.youku.com/v_show/id_XNTc4OTcyMDgw.html",  # 【09DOTA零单第二季】48-49毒狗修补 01:22:41
                           "http://v.youku.com/v_show/id_XNTgxMDA1NzE2.html",  # 【09DOTA零单第二季】50-51小黑小强 01:44:14
                           "http://v.youku.com/v_show/id_XNTgzODk3NDEy.html",  # 【09DOTA零单第二季】52-53小骷髅末日 01:24:41
                           "http://v.youku.com/v_show/id_XNTg2NTk4MDI4.html",  # 【09DOTA零单第二季】结局和神谕者部分讲解 01:33:43
                           "http://v.youku.com/v_show/id_XNTg4NzY5NDEy.html",  # 【09DOTA零单第二季】44杀物理流神谕 01:30:31
                           "http://v.youku.com/v_show/id_XNTkyMTk5Mjcy.html",
                           # 西雅图TI3分析、小组赛LODA演绎最强CARRY(A对TONGFU) 02:12:37
                           "http://v.youku.com/v_show/id_XNTkyNDE2OTMy.html",  # 西雅图TI3分析、小组赛DENDI演绎最强屠夫(LGD对NAVI) 35:29
                           "http://v.youku.com/v_show/id_XNTkyNTczMTEy.html",  # 【09dota提高班】GANK之王土熊猫 02:15:22
                           "http://v.youku.com/v_show/id_XNTk2NDU3NTA0.html",  # 【09dota小坚强】可能不是最好的C 01:34:30
                           "http://v.youku.com/v_show/id_XNTk4NTk5OTQ4.html",  # 【09dota小坚强】后期血魔 58:23
                           "http://v.youku.com/v_show/id_XNjAwOTYzMDAw.html",  # 2013浙大演讲 02:15:48
                           "http://v.youku.com/v_show/id_XNjAxODk5NjU2.html",  # 【09dota2试玩】65杀暴走女王 01:52:19
                           "http://v.youku.com/v_show/id_XNjAzNDY1NzA4.html",  # 【09dota小坚强】影魔4连发（片头抽奖录好忘放了） 02:27:02
                           "http://v.youku.com/v_show/id_XNjA2ODE1MDMy.html",  # 【09DOTA零单第三季】1-3先知末日蓝猫 01:37:14
                           "http://v.youku.com/v_show/id_XNjA4NTg3Njc2.html",  # 【09DOTA零单第三季】4-7斧王幽鬼夜魔女王 01:29:35
                           "http://v.youku.com/v_show/id_XNjEwMjExODg0.html",  # 【09DOTA第一视角】虚空炼金 01:20:45
                           "http://v.youku.com/v_show/id_XNjExMTYzMjQ4.html",  # 【09DOTA高分局】拉比克小鱼人 01:39:57
                           "http://v.youku.com/v_show/id_XNjE1MTU0NTAw.html",  # 【09DOTA零单第三季】8-9蝙蝠龙鹰 01:10:39
                           "http://v.youku.com/v_show/id_XNjE2MTM2Mzcy.html",  # 【09DOTA零单第三季】10-11蓝猫 猴子 01:07:39
                           "http://v.youku.com/v_show/id_XNjE3NDUzOTQw.html",  # 【09DOTA零单第三季】12-13 屠夫 影魔 01:02:17
                           "http://v.youku.com/v_show/id_XNjIwMjg2NTk2.html",  # 【09DOTA零单第三季】14-16 小鱼拍拍沉默 01:38:56
                           "http://v.youku.com/v_show/id_XNjIxNjYzNTI0.html",  # 【09DOTA零单第三季】17-18黑贤海民 53:08
                           "http://v.youku.com/v_show/id_XNjIyOTAxMTc2.html",  # 【09DOTA零单第三季】19-20飞机圣堂 01:10:35
                           "http://v.youku.com/v_show/id_XNjI2MTc4MTM2.html",
                           # 【09DOTA零单第三季】21-22高分局QOPand蚂蚁小强 01:18:57
                           "http://v.youku.com/v_show/id_XNjI4NDY4ODYw.html",  # 【09DOTA零单高分局】暴力的大鱼人 59:55

                           "http://v.youku.com/v_show/id_XNjI5ODU3Njg0.html",  # 【09dota零单第三季】23-25中单神牛影魔和bane 01:46:36
                           "http://v.youku.com/v_show/id_XNjMyMTExMTA4.html",  # 【09dota零单第三季】26-27大地五杀激情亚巴顿 01:32:44
                           "http://v.youku.com/v_show/id_XNjMzMDI5NTA4.html",  # 【09DOTA零单高分局】神灵和逆风局暴走影魔 01:23:39
                           "http://v.youku.com/v_show/id_XNjM1OTk5OTEy.html",  # 【09dota零单第三季】28-29小娜迦骨法 01:11:50
                           "http://v.youku.com/v_show/id_XNjM4NDUwMDIw.html",  # 【09DOTA零单高分局】扑朔迷离的船长和董小姐 59:40
                           "http://v.youku.com/v_show/id_XNjM5MTYwMzc2.html",  # 【09DOTA零单高分局】新船长和前剧情补完 47:15
                           "http://v.youku.com/v_show/id_XNjQxNjMwMjQ0.html",  # 【09dota零单第三季】30-31土猫中单火女 01:18:12
                           "http://v.youku.com/v_show/id_XNjQzNDI3ODc2.html",  # 【09DOTA零单高分局】飞机中的战斗机 01:06:51
                           "http://v.youku.com/v_show/id_XNjQ2NzQ0NDYw.html",  # 【09DOTA提高班】炼金术士 01:31:35
                           "http://v.youku.com/v_show/id_XNjUwMDE2Njcy.html",  # 【09DOTA高分局】机智的小狗 57:03
                           "http://v.youku.com/v_show/id_XNjUxNzYyOTYw.html",  # 【09DOTA高分局】影魔蓝猫 01:21:41
                           "http://v.youku.com/v_show/id_XNjUzODQzMzcy.html",  # 【09DOTA高分局】蝙蝠拍拍熊！ 01:56:36
                           "http://v.youku.com/v_show/id_XNjU1NDY3MTQ0.html",  # 【09DOTA高分局】圣剑火猫 01:14:43
                           "http://v.youku.com/v_show/id_XNjU4NzE5MTcy.html",  # 【09DOTA高分局】超级发条  01:55:19
                           "http://v.youku.com/v_show/id_XNjYwNzk1MzY4.html",  # 【09dota零单第三季】32-33炼金小鱼 01:05:19
                           "http://v.youku.com/v_show/id_XNjYxMzYyNDY0.html",  # 【09dota零单第三季】34-35风行小狗 58:42
                           "http://v.youku.com/v_show/id_XNjYzNTY3NDcy.html",  # 【09dota高分单排】不能忍的大鱼人和魔鬼伐木机 01:29:34
                           "http://v.youku.com/v_show/id_XNjY1NjY5ODYw.html",  # 【09dota零单第三季】36精彩末日 01:04:32
                           "http://v.youku.com/v_show/id_XNjY3NDk3MjY4.html",  # 【09dota高分局】逆风幽鬼 58:10
                           "http://v.youku.com/v_show/id_XNjY4OTM0NzI4.html",  # 【09Dota高分局】圣堂隐刺 01:10:02
                           "http://v.youku.com/v_show/id_XNjcwOTI3MTY0.html",  # 【09Dota零单第三季】37-39神谕幽鬼炼金 01:24:14
                           "http://v.youku.com/v_show/id_XNjcyNDc4MjI0.html",  # 【09dota高分局】精彩斧王 01:45:31
                           "http://v.youku.com/v_show/id_XNjc0NDc4OTUy.html",  # 【09DOTA零单第三季】40-41女王影魔 55:13
                           "http://v.youku.com/v_show/id_XNjc4NjM4NDEy.html",  # 【09DOTA高分局】对黑夜魔龙鹰 01:45:15
                           "http://v.youku.com/v_show/id_XNjgxNjYwNjQ0.html",  # 【09DOTA零单第三季】42-44飞机龙鹰土猫 01:19:20
                           "http://v.youku.com/v_show/id_XNjgzNjMxMzQ4.html",  # 【09DOTA高分局】山岭人马 01:42:49
                           "http://v.youku.com/v_show/id_XNjg1OTM1MzQ4.html",  # 【09DOTA零单第三季】45-46影魔神谕 01:22:59
                           "http://v.youku.com/v_show/id_XNjg4MzI5OTI4.html",  # 【09DOTA高分局】矮人！火枪手 01:37:38
                           "http://v.youku.com/v_show/id_XNjg5MDE0MTg4.html",  # 【09DOTA高分局】钢背猪！ 01:00:03
                           "http://v.youku.com/v_show/id_XNjkxODM5MTg0.html",  # 【09DOTA高分局】屠夫 54:03
                           "http://v.youku.com/v_show/id_XNjk1MzE5MzA0.html",  # 【09DOTA零单第三季】47-48神灵风行 01:17:10
                           "http://v.youku.com/v_show/id_XNjk1MzQ0MjEy.html",  # 【09DOTA2第一视角】骷髅卡 01:13:40
                           "http://v.youku.com/v_show/id_XNjk2ODg3ODM2.html",  # 【09DOTA高分局】极限火卡 01:10:32
                           "http://v.youku.com/v_show/id_XNjk3OTkwMTUy.html",  # 【09DOTA2第一视角】小骷髅 01:36:57
                           "http://v.youku.com/v_show/id_XNjk4NzE0MDg0.html",  # 【09DOTA零单第三季】49蝙蝠 01:08:11
                           "http://v.youku.com/v_show/id_XNzAwOTgxMzAw.html",  # 【09DOTA高分局】吊打被吊打船长 01:17:16
                           "http://v.youku.com/v_show/id_XNzAxNDcxNTQ0.html",  # 【09DOTA2第一视角】凤凰（要保护好蛋蛋哦） 01:09:28
                           "http://v.youku.com/v_show/id_XNzAzNzM0NjUy.html",  # 【09DOTA高分局】中单宙斯亚龙 01:39:21
                           "http://v.youku.com/v_show/id_XNzA0NzI0MjMy.html",  # 【09DOTA2第一视角】恐怖利刃（TB荣耀） 01:06:12
                           "http://v.youku.com/v_show/id_XNzA2MTE0NzEy.html",  # 【09DOTA零单第三季】50-51影魔黑贤 01:17:08
                           "http://v.youku.com/v_show/id_XNzA5NDc4OTk2.html",  # 【09DOTA2第一视角】7杀TA！！？ 02:06:08
                           "http://v.youku.com/v_show/id_XNzEwMzc5OTg4.html",  # 【09DOTA高分局】勇敢的斧王 57:15
                           "http://v.youku.com/v_show/id_XNzExMjU0MTYw.html",  # 【09DOTA高分局】中单沉默 01:33:06
                           "http://v.youku.com/v_show/id_XNzEzNDg5NDk2.html",  # 【09DOTA2第一视角】不能忍的大骷髅 01:33:55
                           "http://v.youku.com/v_show/id_XNzE0OTI3MTY0.html",  # 【09DOTA零单第三季】52-53蝙蝠圣堂2 01:32:42
                           "http://v.youku.com/v_show/id_XNzE2MzU0NTIw.html",  # 【09DOTA高分局】辅助海民和刃甲puck 02:09:26
                           "http://v.youku.com/v_show/id_XNzE4MTQwOTg4.html",
                           # 【09DOTA2比赛解说】NEWBEE DK LGD决战华西村 02:18:10
                           "http://v.youku.com/v_show/id_XNzE5MjIxODU2.html",  # 【09DOTA高分局】灵巧的月之女祭司 01:03:45
                           "http://v.youku.com/v_show/id_XNzIwNjAyMjg0.html",  # 【09DOTA2第一视角】发条地精 01:15:56
                           "http://v.youku.com/v_show/id_XNzIyNDE4NDg0.html",  # 【09DOTA零单第三季】54-55小强猛犸 01:38:06

                           "http://v.youku.com/v_show/id_XNzIzNTY2MTE2.html",  # 【09DOTA提高班】久违的提高班TB! 01:47:23
                           "http://v.youku.com/v_show/id_XNzI1NTYzNDE2.html",  # 【09DOTA高分局】进击的撼地神牛 01:05:00
                           "http://v.youku.com/v_show/id_XNzI3OTA1NTg0.html",  # 【09DOTA2第一视角】逆袭的阿牛 01:02:44
                           "http://v.youku.com/v_show/id_XNzI5OTAxMDMy.html",  # 【09DOTA高分局】流浪和高攻军团 01:38:24
                           "http://v.youku.com/v_show/id_XNzMyODE1NjI0.html",  # 【09DOTA高分局】真男人奥特qq原地复活 01:06:17
                           "http://v.youku.com/v_show/id_XNzM0MzE2NTU2.html",  # 【09DOTA2第一视角】梅肯幽鬼！！ 01:08:05
                           "http://v.youku.com/v_show/id_XNzM1NDMzMjc2.html",  # 【09DOTA零单第三季】56-58神灵小鱼超威蓝猫 01:39:18
                           "http://v.youku.com/v_show/id_XNzM3ODE0ODg0.html",  # 【09DOTA高分局】正面猴和跳刀神灵 01:28:25
                           "http://v.youku.com/v_show/id_XNzM5ODY1NzAw.html",  # 【09DOTA比赛解说】TI4积分赛VG对IG 48:45
                           "http://v.youku.com/v_show/id_XNzQwMzAxMjYw.html",  # 【09DOTA比赛解说】TI4预选赛DK对EG 01:04:08
                           "http://v.youku.com/v_show/id_XNzQwODU3ODI4.html",  # 【09dota比赛解说】TI4淘汰赛第一天DK对C9 01:38:22
                           "http://v.youku.com/v_show/id_XNzQxOTUzNzI0.html",  # 【09DOTA零单第三季】59-60影魔火女 01:58:39
                           "http://v.youku.com/v_show/id_XNzQ2MjEwMzgw.html",  # 【09DOTA提高班】天怒法师！ 01:59:54
                           "http://v.youku.com/v_show/id_XNzQ4NTcyODQw.html",  # 【09DOTA2第一视角】负重神灵魔鬼的步伐 01:15:07
                           "http://v.youku.com/v_show/id_XNzQ5NDI2Mjg0.html",  # 【09DOTA零单第三季】61酣畅淋漓淋漓的蝙蝠 01:10:09
                           "http://v.youku.com/v_show/id_XNzUzMzgxNjUy.html",  # 【09dota高分局】全民胜率冠军亚巴顿 56:24
                           "http://v.youku.com/v_show/id_XNzU0MjIzMzky.html",  # 【09dota2第一视角】小狗要逆袭 43:04
                           "http://v.youku.com/v_show/id_XNzU2NDAwNjI4.html",  # 【09dota高分局】无敌BB猪 01:28:39
                           "http://v.youku.com/v_show/id_XNzU4NzE1NDA0.html",  # 【冰桶挑战】支持渐冻人 01:05
                           "http://v.youku.com/v_show/id_XNzU5ODc2Mzc2.html",  # 【09高分局】尸王人马 01:26:21
                           "http://v.youku.com/v_show/id_XNzYxMjM2ODA4.html",  # 【09DOTA2第一视角】时尚蚂蚁输出流 01:35:52
                           "http://v.youku.com/v_show/id_XNzYyODUyNjYw.html",
                           # 【09dota趣味solo赛】8进4一组握爪对龙MM KUNKKA NA 27:30
                           "http://v.youku.com/v_show/id_XNzY0MDIxOTEy.html",  # 【09dota零单第3季】62攻速棒山岭巨人 52:17
                           "http://v.youku.com/v_show/id_XNzczMjAxNTQ4.html",  # 【09dota趣味solo赛】8进4 冯VS别装 海民光法 23:07
                           "http://v.youku.com/v_show/id_XNzczNTU4Mjcy.html",  # 【09DOTA高分局】就是要出5级大根 01:28:52
                           "http://v.youku.com/v_show/id_XNzc1OTM4MDU2.html",  # 【09DOTA2第一视角】虚空山岭 01:19:47
                           "http://v.youku.com/v_show/id_XNzgwMzY3OTI4.html",  # 【09DOTA高分局】小狗隐刺 01:45:30
                           "http://v.youku.com/v_show/id_XNzg2NDcxMjEy.html",  # 【09DOTA高分局】电魂 01:03:45
                           "http://v.youku.com/v_show/id_XNzg2NTQyMDQw.html",  # 【09炉石提高班】万恶的动物园 52:01
                           "http://v.youku.com/v_show/id_XNzg5OTUyNTUy.html",  # 【09DOTA2第一视角】luna谜团 01:33:44
                           "http://v.youku.com/v_show/id_XNzkyNDYyMjk2.html",  # 【09DOTA零单大结局】63-64猴子神牛 01:22:53
                           "http://v.youku.com/v_show/id_XNzk2NTMzMzgw.html",  # 【09DOTA高分局】赏金伐木机毒狗 01:47:59
                           "http://v.youku.com/v_show/id_XODAwMDQwOTA4.html",  # 【09DOTA2对黑】VIPER全明星 01:41:38
                           "http://v.youku.com/v_show/id_XODAwNDUxODcy.html",  # 【09DOTA高分局】复仇之魂 56:32
                           "http://v.youku.com/v_show/id_XODA2NDQ1Njk2.html",  # 【09DOTA高分局】炼金术士 56:43
                           "http://v.youku.com/v_show/id_XODExMDg2NjIw.html",  # 【09DOTA高分局】精彩血魔！ 01:50:22
                           "http://v.youku.com/v_show/id_XODE2NzAzODIw.html",  # 【09DOTA2第一视角】剑圣人马 01:22:47
                           "http://v.youku.com/v_show/id_XODE3NTQ4MzI4.html",  # 【09DOTA高分局】神灵宙斯 01:30:01
                           "http://v.youku.com/v_show/id_XODIzODcyNDIw.html",  # 【09DOTA高分局】双十一特别篇圣堂冰魂 02:20:48
                           "http://v.youku.com/v_show/id_XODI0MTY3MDA0.html",  # 【09DOTA2天梯单排】双十一巫妖王虚空 02:13:57
                           "http://v.youku.com/v_show/id_XODI2ODgxMjYw.html",  # 【09DOTA高分局】龙骑幽鬼！ 01:58:20
                           "http://v.youku.com/v_show/id_XODMxNDIwNDg4.html",  # 【09DOTA高分局】黑贤凤凰 01:21:56
                           "http://v.youku.com/v_show/id_XODM2MTE1OTA4.html",  # 【09DOTA高分局】半人猛犸 55:43
                           "http://v.youku.com/v_show/id_XODM4NjM4ODU2.html",  # 【09DOTA高分局】3进3出大根火猫 44:42
                           "http://v.youku.com/v_show/id_XODQxNjM0MDc2.html",  # 【09DOTA高分局】前期保人中期杀人后期carry 01:24:28
                           "http://v.youku.com/v_show/id_XODQ1NDA0MzUy.html",  # 【09DOTA2全明星】巫妖亚龙with大萌p 01:11:06
                           "http://v.youku.com/v_show/id_XODQ3MDUzNTY4.html",
                           # 【09DOTA高分局】霸气蓝猫！(双12正片忘记了罪过种罪过) 01:03:38
                           "http://v.youku.com/v_show/id_XODUxOTM5Mjg4.html",  # 【09DOTA高分局】中单蚂蚁 01:06:08
                           "http://v.youku.com/v_show/id_XODUyNzI5MDEy.html",  # 【09DOTA2全明星】刀刀烈火 55:34
                           "http://v.youku.com/v_show/id_XODU1NzU3MjUy.html",  # 【09DOTA大根的故事】有希望有翻盘 01:07:20

                           "http://v.youku.com/v_show/id_XODYyMjM4MzYw.html",  # 【09DOTA大根的故事】贺岁篇老虎 01:11:28
                           "http://v.youku.com/v_show/id_XODY5NTQyMDEy.html",  # 【09DOTA高分局】A杖屠夫 53:53
                           "http://v.youku.com/v_show/id_XODcxMzUzOTUy.html",  # 【09DOTA大根的故事】虚灵NEC 42:15
                           "http://v.youku.com/v_show/id_XODc0ODk2NzM2.html",  # 【09DOTA大根的故事】中单蝙蝠 01:03:09
                           "http://v.youku.com/v_show/id_XODgwODQ0MTgw.html",  # 【09DOTA2第一视角】圣堂影魔 01:30:43
                           "http://v.youku.com/v_show/id_XODg0MzIyMjU2.html",  # 【09DOTA大根的故事】仙女龙 57:57
                           "http://v.youku.com/v_show/id_XODg5MzY0MjMy.html",  # 【09DOTA高分局】吹风影魔=_= 52:44
                           "http://v.youku.com/v_show/id_XOTAwMzE5OTUy.html",  # 【09DOTA高分局】圣剑火枪 01:59:24
                           "http://v.youku.com/v_show/id_XOTAzNTQ0ODY4.html",  # 【09DOTA高分局】暴走幻刺 56:42
                           "http://v.youku.com/v_show/id_XOTA4ODI1NjYw.html",  # 【09DOTA开黑】风行和破纪录SF3 01:31:28
                           "http://v.youku.com/v_show/id_XOTExNjg4NjIw.html",  # 【09DOTA高分局】80杀LINA（上） 34:03
                           "http://v.youku.com/v_show/id_XOTE1Nzc3OTcy.html",  # 【09DOTA高分局】80杀LINA（下） 01:18:14
                           "http://v.youku.com/v_show/id_XOTE3OTU2MTg0.html",  # 【09DOTA2高分局】巨魔战将 58:28
                           "http://v.youku.com/v_show/id_XOTIyNTk5MzI0.html",  # 【09DOTA高分局】奥蕾莉亚 56:58
                           "http://v.youku.com/v_show/id_XOTI4OTU5MTY4.html",  # 【09DOTA高分局】哑巴女王秘法蓝猫 01:10:13
                           "http://v.youku.com/v_show/id_XOTMyODA1ODcy.html",  # 【09DOTA高分局】逆风小小 57:38
                           "http://v.youku.com/v_show/id_XOTM3MjIzMzc2.html",  # 【09DOTA高分局】劲乐团卡尔 01:02:51
                           "http://v.youku.com/v_show/id_XOTQzNDQ0NTcy.html",  # 【09DOTA2单排】但是巨魔不可能死 01:15:35
                           "http://v.youku.com/v_show/id_XOTQ3MTAyMzEy.html",  # 【09DOTA高分局】富一代幻刺老鹿 01:03:56
                           "http://v.youku.com/v_show/id_XOTUyOTY4NDI0.html",  # 【09DOTA高分局】~风行隐刺 01:14:56
                           "http://v.youku.com/v_show/id_XOTU0OTU3MjYw.html",  # 【09DOTA大根的故事】最后的倔强 01:24:18
                           "http://v.youku.com/v_show/id_XOTYyNDM5MDIw.html",  # 【09DOTA高分局】快使用双截棍 01:04:38
                           "http://v.youku.com/v_show/id_XMTI1MzMwNjYwOA==.html",  # 【09DOTA高分局】被克女王（开图者说） 52:40
                           "http://v.youku.com/v_show/id_XMTI1NTE3Nzc0NA==.html",  # 【09DOTA高分局】影魔影魔 01:20:16
                           "http://v.youku.com/v_show/id_XMTI2MDQ1NTkwOA==.html",  # 【09DOTA高分局】圣堂do1do2 01:02:43
                           "http://v.youku.com/v_show/id_XMTI2Nzc0NTcwOA==.html",  # 【09DOTA高分局】军团老虎 01:18:20
                           "http://v.youku.com/v_show/id_XMTI3MjI5NzEyNA==.html",  # 【09DOTA高分局】刷新赏金 53:20
                           "http://v.youku.com/v_show/id_XMTI3Njg5NTU4NA==.html",  # 【09DOTA高分局】拆黑小鱼 50:45
                           "http://v.youku.com/v_show/id_XMTI4MzE5NDY5Mg==.html",  # 【09DOTA高分局】飞机全能 01:29:15
                           "http://v.youku.com/v_show/id_XMTI4NzIxNDQyOA==.html",  # 【09DOTA高分局】仙女龙沙王 01:08:59
                           "http://v.youku.com/v_show/id_XMTI5MjIyMTM2OA==.html",  # 【09DOTA高分局】斧王 58:18
                           "http://v.youku.com/v_show/id_XMTI5NTMyOTg2NA==.html",  # 【09DOTA高分局】凶 44:01
                           "http://v.youku.com/v_show/id_XMTI5ODU2NTQ1Mg==.html",  # 【09DOTA高分局】逆风蓝猫 50:58
                           "http://v.youku.com/v_show/id_XMTMwNTk3MjUwMA==.html",  # 【09DOTA2单排】上分鹿 39:44
                           "http://v.youku.com/v_show/id_XMTMwODk1OTQ5Ng==.html",  # 【09DOTA高分局】电魂死灵法 01:19:58
                           "http://v.youku.com/v_show/id_XMTMxNTYyMjAwOA==.html",  # 【09DOTA高分局】暗灭蓝猫 43:51
                           "http://v.youku.com/v_show/id_XMTMyMjQ4NzU0MA==.html",  # 【09DOTA高分局】中单女王电魂 01:02:08
                           "http://v.youku.com/v_show/id_XMTMzMDI5MDQyNA==.html",  # 【09DOTA高分局】刷新猛犸4V5 01:10:41
                           "http://v.youku.com/v_show/id_XMTMzNTQ1MDY2OA==.html",  # 【09DOTA高分局】推推影魔 01:03:00
                           "http://v.youku.com/v_show/id_XMTM0MjIwMjc3Ng==.html",  # 【09DOTA高分局】酱油LINA 40:39
                           "http://v.youku.com/v_show/id_XMTM0ODg1OTA4NA==.html",  # 【09DOTA高分局】宙斯骨法 01:00:58
                           "http://v.youku.com/v_show/id_XMTM1MTAyNTg2NA==.html",  # 【09DOTA高分局】劣单暗灭牛 31:35
                           "http://v.youku.com/v_show/id_XMTM1NDU3MTk2NA==.html",  # 【09DOTA高分局】逆风传说哥 01:05:51
                           "http://v.youku.com/v_show/id_XMTM2MTE0Mzc2OA==.html",  # 【09DOTA高分局】小鱼飞机 01:28:02
                           "http://v.youku.com/v_show/id_XMTM2NzA5MjY0OA==.html",  # 【09DOTA高分局】4V5一刀流海民 48:20
                           "http://v.youku.com/v_show/id_XMTM3MzAyODkxNg==.html",  # 【09DOTA高分局】4V5!红蓝伐木机 01:02:23
                           "http://v.youku.com/v_show/id_XMTM3NTMxMzAyNA==.html",  # 【09DOTA高分局】来自劣势路的输出 52:42
                           "http://v.youku.com/v_show/id_XMTM3OTczMTIwOA==.html",  # 【09DOTA高分局】双十一史诗级猛犸 01:37:54
                           "http://v.youku.com/v_show/id_XMTM4MjQzNjQ5Ng==.html",  # 【09DOTA高分局】机智的中单发条 01:34:23
                           "http://v.youku.com/v_show/id_XMTM4ODg2OTI4OA==.html",  # 【09DOTA高分局】刷新法核荣耀 01:01:17

                           "http://v.youku.com/v_show/id_XMTM5NjQ4Njk2NA==.html",  # 【09DOTA高分局】绝境PA 58:33
                           "http://v.youku.com/v_show/id_XMTQwMzEzMzA1Ng==.html",  # 【09DOTA高分局】中单carry蓝猫 56:00
                           "http://v.youku.com/v_show/id_XMTQwMzM1NTY0OA==.html",  # 【09DOTA2解说】CDEC高分局神灵体系 58:06
                           "http://v.youku.com/v_show/id_XMTQxMDQyOTM4MA==.html",  # 【09DOTA高分局】逆风斧王 01:16:34
                           "http://v.youku.com/v_show/id_XMTQxODE4OTIwMA==.html",  # 【09DOTA高分局】32-4-19 57:24
                           "http://v.youku.com/v_show/id_XMTQyNTcwODU5Mg==.html",  # 【09DOTA高分局】猴子 52:14
                           "http://v.youku.com/v_show/id_XMTQzMDcyMDQ2MA==.html",  # 【09DOTA2解说】ECL4强FTD.B-CDEC 02:02:47
                           "http://v.youku.com/v_show/id_XMTQzMTczMzQ2OA==.html",
                           # 【09DOTA2解说】ECL4强FTD.B-CDEC(不卡) 02:18:49
                           "http://v.youku.com/v_show/id_XMTQzMjQyMzc2MA==.html",  # 【09DOTA高分局】中单天怒3打5 43:36
                           "http://v.youku.com/v_show/id_XMTQzNzY2MDMwOA==.html",  # 【09DOTA高分局】3V5大电锤斧王！ 01:00:24
                           "http://v.youku.com/v_show/id_XMTQ0MTI5NzAwOA==.html",  # 【09DOTA高分局】受折磨灵魂 45:58
                           "http://v.youku.com/v_show/id_XMTQ0ODIxNjAxMg==.html",  # 【09DOTA高分局】停不下来 46:59
                           "http://v.youku.com/v_show/id_XMTQ1NzEwNjcxNg==.html",  # 【09DOTA高分局】中单ROSHAN 53:10
                           "http://v.youku.com/v_show/id_XMTQ2MzM1MjAxMg==.html",  # 【09DOTA高分局】中单龙骑 50:56
                           "http://v.youku.com/v_show/id_XMTQ2NjgzNzg2NA==.html",  # 【09DOTA高分局】2016要中单要2V5! 01:12:29
                           "http://v.youku.com/v_show/id_XMTQ3NDE5NTUwNA==.html",  # 【09DOTA高分局】中单混沌 32:38
                           "http://v.youku.com/v_show/id_XMTQ3OTMyNzE1Mg==.html",  # 【09DOTA高分局】+190辅助沉默 50:27
                           "http://v.youku.com/v_show/id_XMTQ5MzI0NjY2NA==.html",  # 【09DOTA高分局】冰电强 01:06:57
                           "http://v.youku.com/v_show/id_XMTQ5ODc5NTAwOA==.html",  # 【09DOTA第分局】小鱼混混下周继续两更 33:08
                           "http://v.youku.com/v_show/id_XMTUwMjUyNDA4NA==.html",  # 【09DOTA】28分钟6神鹿 43:36
                           "http://v.youku.com/v_show/id_XMTUwNjU2MjEzNg==.html",  # 【09DOTA高分局】中单巫医和勋章炼金 01:27:19
                           "http://v.youku.com/v_show/id_XMTUwOTQ1NTQ2MA==.html",  # 【09DOTA高分局】中单幻刺影魔 01:17:30
                           "http://v.youku.com/v_show/id_XMTUyMjIwMjE5Ng==.html",  # 【09DOTA高分对黑】10个火枪9个菜 56:24
                           "http://v.youku.com/v_show/id_XMTUyODU4NTI1Mg==.html",  # 【09DOTA双排】中单VIPER! 51:47
                           "http://v.youku.com/v_show/id_XMTUzMDE3MTMwMA==.html",  # 【09DOTA高分局】中单神谕 01:00:33
                           "http://v.youku.com/v_show/id_XMTU0MDI1MDc1Ng==.html",  # 【09DOTA小坚强】劣势路买眼也要carry 01:09:27
                           "http://v.youku.com/v_show/id_XMTU0NDkwMzc4OA==.html",  # 【09DOTA直播局】我上我不想3:0 01:00:37
                           "http://v.youku.com/v_show/id_XMTU1NTYxODQ5Ng==.html",  # 【09DOTA高分局】劣势路的强心戟 57:56
                           "http://v.youku.com/v_show/id_XMTU2NTQ1MjM4NA==.html",  # 【09DOTA小坚强】海民你好 01:03:41
                           "http://v.youku.com/v_show/id_XMTU3ODg0NjY0NA==.html",  # 【09DOTA高分局】刷新大炮 59:42
                           "http://v.youku.com/v_show/id_XMTU3OTY1NDU0OA==.html",  # 【09DOTA全明星】血精一姐 01:01:41
                           "http://v.youku.com/v_show/id_XMTU5NTA0NTk5Ng==.html",  # 【09DOTA高分局】没有心一样肉 01:31:32
                           "http://v.youku.com/v_show/id_XMTYxMDAzMDI1Ng==.html",  # 【09DOTA小坚强】？ 01:06:25
                           "http://v.youku.com/v_show/id_XMTYyNDcxMDM4OA==.html",  # 【09DOTA高分局】神灵武士 52:43
                           "http://v.youku.com/v_show/id_XMTYzMDAzNTc5Ng==.html",  # 【09DOTA高分局】跳刀蚂蚁 44:24
                           "http://v.youku.com/v_show/id_XMTYzNzg2NDUyMA==.html",  # 【09DOTA高分局】剑圣 53:58
                           "http://v.youku.com/v_show/id_XMTYzODc1OTEzMg==.html",  # 【09DOTA高分局】人头超过分钟的PA 45:58
                           "http://v.youku.com/v_show/id_XMTY0ODU1OTkxMg==.html",  # 【09DOTA大根的故事】劣势路小鱼 42:07
                           "http://v.youku.com/v_show/id_XMTY1NjU1MTk1Mg==.html",  # 【09DOTA高分局】劣单VS 35:12
                           "http://v.youku.com/v_show/id_XMTY2NzgzNTIxMg==.html",  # 【09DOTA高分局】AM+PA怎么赢 01:05:03
                           "http://v.youku.com/v_show/id_XMTY4MDcyODMwNA==.html",  # 【09DOTA高分局】臂章大鱼 48:24
                           "http://v.youku.com/v_show/id_XMTY4Njc3ODA0MA==.html",  # 【09DOTA直播局】影魔幽鬼 01:36:40
                           "http://v.youku.com/v_show/id_XMTcwMzk2NTIwMA==.html",  # 【09DOTA高分局】地上最强猪 59:29
                           "http://v.youku.com/v_show/id_XMTcyMTA4Mzc0NA==.html",  # 【09DOTA高分局】魔法流飞机 38:34
                           "http://v.youku.com/v_show/id_XMTcyNDE3NTc5Mg==.html",  # 【09DOTA高分局】蝎子莱莱 58:29
                           "http://v.youku.com/v_show/id_XMTczOTU1MzczMg==.html",  # 【09直播高分局】剑圣天怒 01:32:05
                           "http://v.youku.com/v_show/id_XMTc0ODU2OTc4MA==.html",  # 【09DOTA高分局】不肯老去的蓝猫 49:08
                           "http://v.youku.com/v_show/id_XMTc1NTU4MzA2NA==.html",  # 【09DOTA高分局】中年恶魔巫师 01:05:58
                           "http://v.youku.com/v_show/id_XMTc3MDgyMDc4MA==.html",  # 【09DOTA高分局】阿汤佛歌 03:22:44
                           "http://v.youku.com/v_show/id_XMTgwNTE3MjM1Mg==.html",  # 【09DOTA高分局】游走拍拍，你拍了吗 40:22

                           "http://v.youku.com/v_show/id_XMTgxMTY0OTY1Ng==.html",  # 【09DOTA高分局】幻刺小鱼剑圣怎么赢 01:28:29
                           "http://v.youku.com/v_show/id_XMTgxMzAzNDk1Ng==.html",  # 【09DOTA双十一特别篇】4V5中单沙发 01:38:07
                           "http://v.youku.com/v_show/id_XMTgyODU1ODQ2OA==.html",  # 【09DOTA高分局】修补匠 01:06:28
                           "http://v.youku.com/v_show/id_XMTgzNDk4Mjg2MA==.html",  # 【09DOTA高分局】天降正义 57:26
                           "http://v.youku.com/v_show/id_XMTg0NjIxNTMyNA==.html",  # 【09dota高分局】根本停不下来 56:36
                           "http://v.youku.com/v_show/id_XMTg1NTIyODk0MA==.html",  # 【09DOTA双十二特别篇】不死大鱼 01:19:50
                           "http://v.youku.com/v_show/id_XMTg1ODI0MDQ0OA==.html",  # 【09DOTA双十二特别篇】逆风逆风 01:18:13
                           "http://v.youku.com/v_show/id_XMTg2Nzg2OTM4MA==.html",  # 【09dota高分局】仙女龙 52:27
                           "http://v.youku.com/v_show/id_XMTg4MDEyMDE3Ng==.html",  # 【09DOTA高分局】中单牛头 57:58
                           "http://v.youku.com/v_show/id_XMTg5MTM5MjAzNg==.html",  # 【09DOTA高分局】中单海民 01:03:36
                           "http://v.youku.com/v_show/id_XMTkyOTUzMjgyOA==.html",  # 【09DOTA高分局】150人头局女王 01:08:47
                           "http://v.youku.com/v_show/id_XMjMzMTkxOTMxNg==.html",  # 【09DOTA高分局】逆风SF 56:51
                           "http://v.youku.com/v_show/id_XMjQxOTgxMjA1Ng==.html",  # 【09DOTA高分局】中单龙骑期末快乐 01:07:42
                           "http://v.youku.com/v_show/id_XMjQ4NjAyMjI1Ng==.html",  # 【09Dota高分局】劣单伐木机 34:33
                           "http://v.youku.com/v_show/id_XMjQ4ODE0NDU2OA==.html",  # 【09DOTA高分局】猥琐大鱼 01:09:23
                           "http://v.youku.com/v_show/id_XMjUwNTQ0MzYxNg==.html",  # 【09DOTA高分局】中单火猫 48:40
                           "http://v.youku.com/v_show/id_XMjUxNjYyNTE1Mg==.html",  # 【09DOTA高分局】瞬间崛起的UG（下期素材绝对认真） 49:21
                           "http://v.youku.com/v_show/id_XMjUyMzQ0ODY2MA==.html",  # 【09DOTA高分局】逆风火女 59:30
                           "http://v.youku.com/v_show/id_XMjUyOTcyNzIyOA==.html",  # 【09DOTA高分局】难玩的影魔 55:46
                           "http://v.youku.com/v_show/id_XMjU4ODQ4ODEzMg==.html",  # 【09DOTA高分局】小鱼 43:51
                           "http://v.youku.com/v_show/id_XMjYyODAxMTc0OA==.html",  # 【09DOTA6.84】玲珑心火女 37:53
                           "http://v.youku.com/v_show/id_XMjYzMjk4NTMwNA==.html",  # 【09DOTA6.84】高达狗 46:37
                           "http://v.youku.com/v_show/id_XMjY0NTkzMDgyNA==.html",  # 【09DOTA零单第四季】1 蓝猫 48:49
                           "http://v.youku.com/v_show/id_XMjY1Mjc1NzI3Mg==.html",  # 【09DOTA6.84】偶遇天梯第一炼金 01:01:22
                           "http://v.youku.com/v_show/id_XMjY2NTU3OTA1Ng==.html",  # 【09DOTA零单第四季】2-3纳加老鹿 58:23
                           "http://v.youku.com/v_show/id_XMjY4MzMwNDU2MA==.html",  # 【09dota零单第四季】4破记录小小和天怒彩蛋 55:23
                           "http://v.youku.com/v_show/id_XMjcwMDM4NjQ2NA==.html",  # 【09DOTA6.84】土猫以及新版本讲解 38:25
                           "http://v.youku.com/v_show/id_XMjcxMjM5NTUxNg==.html",  # 【09DOTA零单第四季】5-6影魔和暴走女王 01:11:30
                           "http://v.youku.com/v_show/id_XMjcyNTAxNjgyOA==.html",  # 【09DOTA6.84】伐木四件套黑鸟 35:48
                           "http://v.youku.com/v_show/id_XMjc0NzQ4OTM4NA==.html",  # 【09DOTA高分局】一刀权限牛 44:01
                           "http://v.youku.com/v_show/id_XMjc1Nzg1OTk0MA==.html",  # 【09DOTA高分局】3V5带球荣耀 59:26
                           "http://v.youku.com/v_show/id_XMjc3MzcyNzA2OA==.html",  # 【09dota零单第四季・】7天怒 50:19
                           "http://v.youku.com/v_show/id_XMjgwNjQ3MTk4NA==.html",  # 【09DOTA高分局】中单小小 33:42
                           "http://v.youku.com/v_show/id_XMjgwNjgyNzcxNg==.html",  # 【09DOTA高分局】辉耀狂战硬头猫 28:46
                           "http://v.youku.com/v_show/id_XMjgzODk4NTEwOA==.html",  # 【09DOTA6.84高分局】新一代野区吸血鬼 37:23
                           "http://v.youku.com/v_show/id_XMjg4MTU5MjMwMA==.html",  # 【09DOTA6.84高分局】（上集）特权敌法 45:44
                           "http://v.youku.com/v_show/id_XMjg4MjczMzQ0OA==.html",  # 【09DOTA高分局】（下集）中单敌法 46:29
                           "http://v.youku.com/v_show/id_XMjk0MTA1NzE1Mg==.html",  # 【09DOTA6.84提高班】42杀游走拍拍 01:02:43
                           "http://v.youku.com/v_show/id_XMjk4NDM0Mjg2NA==.html",  # 【09DOTA高分局】两个鸡翅的圣堂刺客 50:15
                           "http://v.youku.com/v_show/id_XMjk5NjY1NDU0OA==.html",  # 【09DOTA6.84高分局】中单AA 45:50
                           "http://v.youku.com/v_show/id_XMzA2NDAxNjcyMA==.html",  # 【09DOTA6.85高分局】新版本游走DOOM 51:29
                           "http://v.youku.com/v_show/id_XMzEzNDM0NTI1Mg==.html",  # 【09DOTA6.84高分局】200+沉默 54:32
                           "http://v.youku.com/v_show/id_XMzE0MTE5NjM1Mg==.html",  # 【09DOTA高分局】劣单蓝猫不可能死 01:22:16
                           "http://v.youku.com/v_show/id_XMzIwMTQ4MzIyMA==.html",  # 【09DOTA高分局】31杀sven 01:16:01
                           "http://v.youku.com/v_show/id_XMzMwMjA4ODY5Mg==.html",  # 【09DOTA6.85高分局】逆风QOP 51:47
                           "http://v.youku.com/v_show/id_XMzMzMTI4NDc4OA==.html",
                           # 【09】换了新发型有属性加成，吃鸡还不是手到擒来？和囚大一起四排吃鸡！ 34:06
                           "http://v.youku.com/v_show/id_XMzQzNjQ1ODc5Ng==.html",  # 【主播酒神】2018.02.24下午直播录像 04:39:45
                           "http://v.youku.com/v_show/id_XMzQzNzQ2NDA5Ng==.html",
                           # 绝地求生：酒神遇神秘bug获得透视神力，小绝身先士卒惨遭围攻！ 01:09
                           "http://v.youku.com/v_show/id_XMzQzNjQ4MDA5Ng==.html",  # 【主播09】2018.02.26下午直播录像 20:01
                           "http://v.youku.com/v_show/id_XMzQzNjQ3MDM3Mg==.html",  # 【主播09】2018.02.26下午直播录像 23:19

                           "http://v.youku.com/v_show/id_XMzQzNjQ2MTI0NA==.html",  # 【主播09】2018.02.25上午直播录像 38:04
                           "http://v.youku.com/v_show/id_XMzQzNjQ3MTE1Ng==.html",  # 【主播09】2018.02.26下午直播录像 28:59
                           "http://v.youku.com/v_show/id_XMzQzNjcyNjQ2NA==.html",  # 【主播09】无限闪现流。7杀吃鸡局 18:14
                           "http://v.youku.com/v_show/id_XMzQzNjcyMTk2NA==.html",  # 【主播09】残血反杀，带小姐姐10杀吃鸡 31:18
                           "http://v.youku.com/v_show/id_XMzQzNjQ4MDU0NA==.html",  # 【主播09】2018.02.26下午直播录像 01:05:09
                           "http://v.youku.com/v_show/id_XMzQ0MDM0MTI3Mg==.html",  # 【主播09】 狙神09上线，17杀完美吃鸡！ 25:34
                           "http://v.youku.com/v_show/id_XMzQ0MDA4NTY4OA==.html",  # 【主播09】2018.3.2下午直播录像 01:25:54
                           "http://v.youku.com/v_show/id_XMzQ0NjQ1OTE0NA==.html",  # 绝地求生：伍声火枪手附体！m24狙击枪在手17杀实力吃鸡 01:48
                           "http://v.youku.com/v_show/id_XMzQ0MDMzMTE1Mg==.html",  # 【主播09】2018.03.01下午直播录像 08:18
                           "http://v.youku.com/v_show/id_XMzQ0MDE1ODY4NA==.html",  # 【主播09】队友全体阵亡，09战神1V24，12杀吃鸡 23:09
                           "http://v.youku.com/v_show/id_XMzQ0MDY4MzI1Mg==.html",  # 【主播09】2018.03.01下午直播录像 44:30
                           "http://v.youku.com/v_show/id_XMzQ0MDA4OTI2NA==.html",  # 【主播09】2018.3.4下午直播录像 01:45:05
                           "http://v.youku.com/v_show/id_XMzQ0MDA5NDQ4MA==.html",  # 【主播09】2018.3.2下午直播录像 04:35:53
                           "http://v.youku.com/v_show/id_XMzQ0MDMzODU4OA==.html",  # 【主播09】2018.02.27下午直播录像 03:09:15
                           "http://v.youku.com/v_show/id_XMzQ0Nzk1ODE2NA==.html",  # 【主播09】2018.03.01下午直播录像 03:21:21
                           "http://v.youku.com/v_show/id_XMzQ1MDA4MjIyOA==.html",  # 绝地求生：吃鸡车技那家强？伍声09飞车救人反送双杀！ 01:28
                           "http://v.youku.com/v_show/id_XMzQ0ODY5NTM5Mg==.html",  # 【主播09】2018.03.01上午直播录像 03:21:13
                           "http://v.youku.com/v_show/id_XMzQ0ODYzNDM5Ng==.html",  # 【主播09】2018.02.28下午直播录像 03:29:08
                           "http://v.youku.com/v_show/id_XMzQ0ODYzNDUxMg==.html",  # 【主播09】2018.02.28下午直播录像) 03:29:02
                           "http://v.youku.com/v_show/id_XMzQ0ODYzMzg5Ng==.html",  # 【主播09】2018.02.27下午直播录像 03:09:16
                           "http://v.youku.com/v_show/id_XMzQ2NDk1Mzc2NA==.html",
                           # 绝地求生：新BUG前列腺开车？原来这样骑摩托可以让人变GAY！ 02:00
                           "http://v.youku.com/v_show/id_XMzQ3NTQyMTkzNg==.html",  # 【主播09】2018.03.05下午直播录像 03:34:29
                           "http://v.youku.com/v_show/id_XMzQ3NTQyMTQ5Ng==.html",  # 【主播09】2018.03.06下午直播录像 02:56:46
                           "http://v.youku.com/v_show/id_XMzQ3NTQyMjY2OA==.html",  # 【主播09】2018.03.05下午直播录像 03:34:26
                           "http://v.youku.com/v_show/id_XMzQ3NTM4MDUxMg==.html",  # 【主播09】2018.03.03下午直播录像 02:44:19
                           "http://v.youku.com/v_show/id_XMzQ3NTM4MDY0NA==.html",  # 【主播09】2018.03.03下午直播录像 02:44:20
                           "http://v.youku.com/v_show/id_XMzQ3NTM4MDkzNg==.html",  # 【主播09】2018.03.06下午直播录像 02:56:44
                           "http://v.youku.com/v_show/id_XMzQ4MDgwNTQ5Mg==.html",  # 绝地求生：电影感Max！原来这个游戏攻个楼可以这么帅！ 03:01
                           "http://v.youku.com/v_show/id_XMzQ4ODgzNzUxNg==.html",  # 【主播09】2018.03.07下午直播录像 03:08:48
                           "http://v.youku.com/v_show/id_XMzQ4ODgzODQ4MA==.html",  # 【主播09】2018.03.08下午直播录像 04:09:31
                           "http://v.youku.com/v_show/id_XMzQ4OTExNDg0OA==.html",  # 【主播09】2018.03.09下午直播录像 02:14:31
                           "http://v.youku.com/v_show/id_XMzQ4ODgzODM5Ng==.html",  # 【主播09】2018.03.08下午直播录像 04:09:28
                           "http://v.youku.com/v_show/id_XMzQ4OTA1NDUxNg==.html",  # 【主播09】2018.03.07下午直播录像 03:08:50
                           "http://v.youku.com/v_show/id_XMzUyMTU2NjE0OA==.html",  # 【主播09】2018.03.10下午直播录像 03:11:04
                           "http://v.youku.com/v_show/id_XMzUyMTU2MTI4NA==.html",  # 【主播09】2018.03.11下午直播录像 03:25:39
                           "http://v.youku.com/v_show/id_XMzUyMTU2MzA4MA==.html",  # 【主播09】2018.03.10下午直播录像 03:11:01
                           "http://v.youku.com/v_show/id_XMzUyMTc1MDE0NA==.html",  # 【主播09】2018.03.11下午直播录像 03:25:38
                           "http://v.youku.com/v_show/id_XMzUyMzIzMzIxMg==.html",  # 【主播09】2018.03.18下午直播录像 03:31:23
                           "http://v.youku.com/v_show/id_XMzUyMzE5MzU5Mg==.html",  # 【主播09】2018.03.18下午直播录像 03:31:20
                           "http://v.youku.com/v_show/id_XMzUyMzM3NTkwNA==.html",  # 【主播09】2018.03.15下午直播录像 04:09:41
                           "http://v.youku.com/v_show/id_XMzU4MDI2OTMxMg==.html",  # 【09解说DOTA】熊猫杯决赛闹他对GOD 03:41:21
                           "http://v.youku.com/v_show/id_XMzc3MDA2MTQ1Mg==.html",  # 【09DOTA】大酒神怎么可能是菜比 03:26
                           "http://v.youku.com/v_show/id_XMzc4NjY2MDg2NA==.html",
                           # 【09DOTA解说】2009 ZSMJ 单车 解说TI第三日小组赛 LGD-IG 43:48
                           "http://v.youku.com/v_show/id_XMzc4NjY1NzI4MA==.html",
                           # 【09DOTA解说】2009 ZSMJ 单车 解说TI第三日小组赛 液体-EG 01:31:39
                           "http://v.youku.com/v_show/id_XMzg0MTgwNDg0NA==.html",  # 【伍声2009】新的起点, 新的征程 03:14
                           "http://v.youku.com/v_show/id_XMzk3MzE3NTEyNA==.html",
                           # 【09DOTA2】超凡蓝猫求学八年成杂技, 酒神舔狗居然是隐藏黑粉 02:47
                           "http://v.youku.com/v_show/id_XMzk5NjQwMzEyNA==.html",
                           # 09DOTA2: 第一把兔子看我渡劫上超凡! 我要做的事没人拦得住我! 03:10
                           "http://v.youku.com/v_show/id_XNjcwODU2MjAw.html",  # 【09Dota零单第三季】37-39神谕幽鬼炼金 01:24:14
                           "http://v.youku.com/v_show/id_XNTM3ODY3NDU2.html",  # 【09dota零单第二季】拉比克，龙鹰，蝙蝠 01:54:45
                           "http://v.youku.com/v_show/id_XODUxMzEwOTA0.html",  # 【09DOTA高分局】中单蚂蚁 01:06:08

                         ],
                         'servers': '',
        'remove_ts': True,
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  is_get_url = 0
  if is_get_url:
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
  if not is_get_url:
    th_list = [th]
    th.start()
    th = GetSensBase(conf)
    th_list.append(th)
    th.start()
    for th in th_list:
      th.join()
