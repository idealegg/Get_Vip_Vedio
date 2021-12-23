from bs4 import BeautifulSoup as bs
import requests
import json
import os
import sys


def get_list(kw, pno):
    url = u'http://www.momozyz9.com/share/search?name=%s&page=%s' % (kw, pno)
    r = requests.get(url)
    if r.status_code == 200:
        j = json.loads(r.content)
        f = open(os.path.join(outdir, '%s_%s.json' %(kw, pno)), 'wb')
        f.write(r.content)
        f.close()
        for item in j['data']['items']:
            if item['node'] in [u'制服', u'美腿', u'丝袜']:
                r2 = requests.get(u'http://www.momozyz9.com%s' % item['urlpath'])
                if r2.status_code == 200:
                    s = bs(r2.content, 'html.parser')
                    links = s.find_all('input', attrs={'name': 'copy_sel', 'type':'checkbox'})
                    for link in links:
                        print(link['value'])
                        outs.append(link['value'])


if __name__ == "__main__":
    outdir=r''
    outs =[]
    for i in range(1, 10):
        get_list(u'4时间', i)
    f2 = open(os.path.join(outdir, 'outs.txt'), 'wb')
    f2.write("\n".join(outs).encode('utf8'))
    f2.close()