# -*- coding:utf-8 -*-
import json, requests
import chardet
import gzip
import re

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
url='http://data.video.iqiyi.com/videos/v0/20190103/54/60/c1b38609dc6f23c59084598b97e2e4c0.f4v?qd_tvid=385421200&qd_vipres=0&qd_index=1&qd_aid=202861101&qd_stert=0&qd_scc=a5b7c0555b318bd861c59b2af752b138&qd_sc=4a756f30f0a2b0a6708fd4a5a5dbc41a&qd_p=72e6454c&qd_k=0927e11a1475c4e3e32cb104893a978b&qd_src=01010031010000000000&qd_vipdyn=0&qd_uid=&qd_tm=1546686617972&qd_vip=0&cross-domain=1&qyid=035b208727f148f48ea981df267497c8&qypid=1408763600_02020031010000000000&qypid=1408763600_02020031010000000000&rn=1546686617911&pv=0.2&cross-domain=1&pri_idc=zibo5_cnc'
req = requests.get(url=url)
print req.encoding
print req.headers
print req.reason
#print req.content

fd=open("file.f4v", "wb")
fd.write(req.content)
fd.close()




#输出内容:{"jsonrpc":"2.0","result":"2c42e987811c90e0491f45904a67065d","id":1}