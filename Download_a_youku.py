# -*- coding:utf-8 -*-
import os, requests
import RedirectOut.RedirectOut
import time
import json
import re
from GetSensBase.GetSensBase import GetSensBase
from hashlib import md5
import pprint


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
    if not j['ret'][0].startswith('SUCCESS'):
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
  name = re.sub('[\s()]', '', j['data']['data']['video']['title'])
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
                           # # "http://v.youku.com/v_show/id_XMjYyOTY1MjEy.html",  # 【09dota提高班】巫医第一视角 01:28:17
                           # "http://v.youku.com/v_show/id_XMjYzNzUxMTQ0.html",  # 【09dota超清提高班】压制流敌法 43:57
                           # "http://v.youku.com/v_show/id_XMjY0NjY4OTc2.html",  # 【09dota提高班】月之女祭司 01:02:48
                           # "http://v.youku.com/v_show/id_XMjY1MjUwNzky.html",  # 【09dota超清提高班】月之骑士 01:43:58
                           # "http://v.youku.com/v_show/id_XMjY2NDM1Njk2.html",  # 【09dota超清提高班】纯爷们第一视角 01:15:08
                           # "http://v.youku.com/v_show/id_XMjY2ODIyMjAw.html",  # 【09dota超清提高班】曾经第一后期黑弓 01:16:32
                           # # "http://v.youku.com/v_show/id_XMjY3OTk5MDEy.html",  # 【09dota提高班】疯脸小黑和30分钟三圣剑PA 01:19:34
                           # "http://v.youku.com/v_show/id_XMjY4NjkxNjAw.html",  # 【09dota提高班】 疯狂的死骑和多舛的赏金 01:20:29
                           # "http://v.youku.com/v_show/id_XMjY5ODQyMjU2.html",  # 【09dota提高班】嘲讽猎人和精打细算猫 01:33:22
                           # "http://v.youku.com/v_show/id_XMjcwMjgyMDI0.html",  # 【09dota纪录片】2009_THE_MOVIE 12:09
                           # "http://v.youku.com/v_show/id_XMjcyNTc0MTU2.html",  # 【09dota提高班】无与伦比的华丽风行 01:29:33
                           # "http://v.youku.com/v_show/id_XMjc1MDU2NDYw.html",  # 【09dota开黑篇】2次暴走的4圣剑敌法 01:02:57
                           "http://v.youku.com/v_show/id_XMjc1MTI1NjAw.html",  # 【09dota开黑篇】电猫毒蛇和山岭 02:17:22
                           "http://v.youku.com/v_show/id_XMjc1NTQzODgw.html",  # 【09dota解说】STARWAR上EHOME的龙7表演 01:08:27
                           "http://v.youku.com/v_show/id_XMjc4MzYzMDA0.html",  # 【09dota提高班】风行者完结篇 01:37:47
                           "http://v.youku.com/v_show/id_XMjgwNzk3ODI4.html",  # 【09dota提高班】复仇之魂 01:54:13
                           # "http://v.youku.com/v_show/id_XMjgzMDc3NzQ0.html",  # 【09dota解说】G-1年度经典WE对DK 01:16:18
                           # "http://v.youku.com/v_show/id_XMjgzMDc3Nzc2.html",  # 【09dota解说】G-1年度经典WE对DK 2 01:08:49
                           # "http://v.youku.com/v_show/id_XMjgzMDc3ODU2.html",  # 【09dota解说】G-1年度经典WE对DK 3 01:27:47
                           # "http://v.youku.com/v_show/id_XMjgzNjM1Nzgw.html",  # 【09dota解说】LGD对WE 2 51:26
                           # "http://v.youku.com/v_show/id_XMjgzNjM0MDgw.html",  # 【09dota解说】LGD对WE 1 01:01:24
                           # "http://v.youku.com/v_show/id_XMjgzNjM2Mjg4.html",  # 【09dota解说】LGD对WE 3 01:03:56
                           # "http://v.youku.com/v_show/id_XMjgzNjM1Nzg0.html",  # 【09dota第一视角】宙斯兽王屠夫 02:08:55
                           # "http://v.youku.com/v_show/id_XMjgzNjM1Mzky.html",  # 【09dota第一视角】亚龙蚂蚁火女 02:30:34
                           "http://v.youku.com/v_show/id_XMjg1ODQyMzc2.html",  # 【09dota提高班】巨魔战将(troll) 01:33:03
                           "http://v.youku.com/v_show/id_XMjg2MTYwNzY0.html",  # 【09dota提高班】沙王（SK） 01:38:48
                           "http://v.youku.com/v_show/id_XMjg5NDIxOTIw.html",  # 【09dota提高班】狼人Lycan 01:25:20
                         ],
                         'servers': '',
        'remove_ts': False,
                         }
  th = GetSensBase(conf)
  th.check_dir()
  th.get_exist_file()
  if 0:
    if 1:
      for j in range(len(conf['src_url'])):
        generate_youku_file(th, j, True)
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
