# -*- coding:utf-8 -*-
import requests
import re


def GetKey(url, addr, host, ref):
  ret = ""
  textmod={ "url": addr,
  }
  header_dict = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                 "Accept-Encoding": "gzip,deflate",
                 "Accept-Language": "zh-CN,zh;q=0.9",
  "Connection": "keep-alive",
  "Host": host,
  "Referer": "%s%s" % (ref, addr),
  "User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
  "Upgrade-Insecure-Requests": "1"
  }
  req = requests.get(url=url, params=textmod,  headers=header_dict)
  print req.encoding
  print req.headers
  print req.reason
  print req.content
  res = re.search("eval\(\"(.*?)\"\);", req.content)
  if not res:
    print "GetKey error: %s\n" % addr
  else:
    ret = "".join(map(lambda x: chr(int(x, 16)), res.group(1).split('\\x')[1:]))[17:-3]
    print 'GetKey: key[%s]' % ret
  req.close()
  return  ret


if __name__ == "__main__":
  #print GetKey(url='http://all.baiyug.cn:2021/vip_all/index.php',
  #             addr='https://www.iqiyi.com/v_19rrok775g.html?vfm=2008_aldbd',
  #             host='all.baiyug.cn:2021',
  #             ref='http://app.baiyug.cn:2019/vip/iqiyi.php?url=')
  print GetKey(url='http://www.1717yun.com/1717yun/',
               addr='https://www.iqiyi.com/v_19rrf3hzfs.html?vfm=2008_aldbd',
               host='www.1717yun.com',
               ref='http://www.1717yun.com/jx/ty.php?url=&url=')#