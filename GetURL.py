# -*- coding:utf-8 -*-
import json,urllib2, requests
import chardet
import gzip


textmod={"id": "http%3A%2F%2Fwww.iqiyi.com%2Fv_19rrok5ncc.html%3Fvfm%3D2008_aldbd",
"type": "auto",
"siteuser": "",
"md5": "ab596537258ab5d68e8a9a6bbb87loij",
"hd": "",
"lg": ""}
textmod = json.dumps(textmod)
print(textmod)
#输出内容:{"params": {"password": "zabbix", "user": "admin"}, "jsonrpc": "2.0", "method": "user.login", "auth": null, "id": 1}
header_dict = {"Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip,deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
"Connection": "keep-alive",
"Content-Length": 133,
"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
"Host": "all.baiyug.cn:2021",
"Origin": "http://all.baiyug.cn:2021",
"Referer": "http://all.baiyug.cn:2021/vip_all/index.php?url=http://www.iqiyi.com/v_19rrok5ncc.html?vfm=2008_aldbd",
"User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
"X-Requested-With": "XMLHttpRequest"
}
url='http://all.baiyug.cn:2021/vip_all/url.php'
req = urllib2.Request(url=url,data=textmod,headers=header_dict)
res = urllib2.urlopen(req)
print dir(res)
#res = res.read()
#code = chardet.detect(res)
#print code
#print code['encoding']
#print(res.decode(code['encoding']))
con = res.read()
print res.getcode()
print res.code
print res.headers
print res.msg
print res.url

fd=open("abc.zip", "wb")
fd.write(con)
fd.close()
fd=gzip.open("abc.zip", "rb")
for line in fd:
  print line
fd.close()
#输出内容:{"jsonrpc":"2.0","result":"2c42e987811c90e0491f45904a67065d","id":1}