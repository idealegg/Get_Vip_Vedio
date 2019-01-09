# -*- coding:utf-8 -*-
import json, requests
import chardet
import gzip
import re
import GetVid.GetVid
import GetSign.GetSign
import GetKey.GetKey

textmod={ "xml": "http://www.iqiyi.com/v_19rrok5n98.html?vfm=2008_aldbd",
"md5": "ab59a7e5488ab5d664e3e74ddce8loij",
"type": "auto",
"hd": "cq",
"wap": "0",
"siteuser": None,
"lg": None,
"sohuuid": None}
header_dict = {"Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip,deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
"Connection": "keep-alive",
"Host": "all.baiyug.cn:2021",
"Referer": "http://all.baiyug.cn:2021/vip_all/index.php?url=http://www.iqiyi.com/v_19rrok5ncc.html?vfm=2008_aldbd",
"User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
"X-Requested-With": "ShockwaveFlash/32.0.0.101"
}
url='http://all.baiyug.cn:2021/vip_all/url.php'

info = GetVid.GetVid.GetSens()
keys = info.keys()
keys.sort(cmp=lambda x,y: cmp(int(x[:-1], 10), int(y[:-1], 10)))
for sen in keys:
  textmod['xml'] = info[sen]
  textmod['md5'] = GetSign.GetSign.GetSign(GetKey.GetKey.GetKey(info[sen]))
  header_dict['Referer'] = "http://all.baiyug.cn:2021/vip_all/index.php?url=%s" % info[sen]
  req = requests.get(url=url, params=textmod,  headers=header_dict)
  print req.encoding
  print req.headers
  print req.reason
  print req.content
  res = re.findall("<!\[CDATA\[(http.*?f4v.*?)\]\]></file>", req.content)
  print "len: %d" % len(res)
  print "res:"
  print res
  for i in range(len(res)):
    print res[i]
    req2 = requests.get(url=res[i])
    print req2.encoding
    print req2.headers
    print req2.reason
    # print req.content

    fd = open("%s_%d.f4v" % (sen, i), "wb")
    fd.write(req2.content)
    fd.close()
    req2.close()
  req.close()
