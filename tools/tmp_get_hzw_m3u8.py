import re
import requests



out=[]
start=50
with open("sens_info3.txt") as fd:
  for sen in fd:
    sen=sen[:-1]
    fs=sen.split()
    s1='https://660e.com/?url=&url=%s' % fs[1]
    print(s1)
    req=requests.get(s1)
    p=re.compile('src="/m3u8-dp.php\?url=(.*?)">')
    res=re.search(p, req.content)
    print("res: %s"% res)
    s2=res.group(1)
    s3=s2[:s2.rfind('/')]
    print(s2)
    req=requests.get(s2)
    for line in req.content.split('\n'):
      if not line.startswith('#') and line:
        url=line
    s4="%s/%s" % (s3, url)
    print(s4)
    req=requests.get(s4)
    #https://qq.com-ok-qq.com/20190922/23649_c6521083/index.m3u8
    #https://qq.com-ok-qq.com/20190922/23649_c6521083/1000k/hls/index.m3u8
    m3u8="%d.m3u8" % start
    f2=open(m3u8, 'wb')
    f2.write(req.content)
    f2.close()
    s5=s4[:s4.rfind('/')+1]
    out.append("%d %s %s %s" %(start, m3u8, fs[0], s5))
    #print(out)
    start+=1


with open("sens_info.txt", "wb") as f3:
  f3.write("\n".join(out))
