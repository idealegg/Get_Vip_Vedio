# coding=utf-8
import requests
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class SinaBlog(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(SinaBlog, self).__init__(conf)

    def replace_body(self, soup):
        h2 = soup.find(class_='articalTitle')
        text = soup.find(attrs={'id': "sina_keyword_ad_area2"})
        abody = soup.find(attrs={'id': "articlebody"})
        if abody:
            abody_ch = [x for x in abody.children]
        if h2 is None:
            h2 = abody_ch[0]
        if text is None:
            text = abody_ch[1]
        found = text is not None
        soup.body.clear()
        soup.body.append(h2)
        soup.body.append(text)
        return soup, found

    def find_menu_container(self, s):
        return s.find(class_="articleList")

    def get_page_title(self, item):
        return "%s(%s)" % (item.text, item.findParent('div').find(class_='atc_tm SG_txtc').text)

    def update_urls(self, urls, j):
        u_k = list(urls.keys())
        j_k = list(j.keys())
        u_k = self.sorted(u_k)
        j_k = self.sorted(j_k)
        outs = {}
        for k in u_k:
            k_s = k.rfind('_') + 1
            k_e = k.rfind('.')
            o_seq = int(k[k_s:k_e], 10)
            n_seq = o_seq + len(j_k)
            new_k = "".join([k[:k_s], "%s" % n_seq, k[k_e:]])
            outs[new_k] = urls[k]
            outs[new_k]['index'] = n_seq
            outs[new_k]['file'] = new_k
        for i, k in enumerate(j_k[::-1]):
            k_s = k.rfind('_') + 1
            k_e = k.rfind('.')
            n_seq = i
            new_k = "".join([k[:k_s], "%s" % n_seq, k[k_e:]])
            outs[new_k] = j[k]
            outs[new_k]['index'] = n_seq
            outs[new_k]['file'] = new_k
        return outs

    def get_url_list(self, f):
        urls = {}
        iurl = self.info['url']
        pages = int(self.info['pages'])
        for page in range(pages):
            self.info['url'] = iurl.replace('_1.html', '_%s.html' % (page + 1) )
            super().get_url_list(f)
            with open(f, 'r') as jr:
                j = json.load(jr)
                urls = self.update_urls(urls, j)
        with open(f, 'w') as jf:
            json.dump(urls, jf)

if __name__ == "__main__":
  setup_logging()
  sys.setrecursionlimit(3000)
  th = SinaBlog(conf={'base_dir': r'E:\hzw',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'pages'],
                         'src_type': 'file',
                      'remove_pdf': False,
                      'remove_html': False,
                         'headers':{
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    "Accept-Encoding": 'gzip, deflate',
    "Accept-Language": 'zh-CN,zh;q=0.9',
    "Cache-Control": 'max-age=0',
    "Connection": 'keep-alive',
       "Host": 'blog.sina.com.cn',
    'DNT': '1',
    "Pragma": 'no-cache',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    "User-Agent": 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'},
                      'cookies': {
                            'CNZZDATA1280486254': '223523596-1635383857-|1635750212',
                            'CNZZDATA1280486250': '681936964-1635383472-|1635750983',
                            'CNZZDATA1280486255': '40455575-1635383291-|1635750496',
                            'CNZZDATA1280486251': '1534032754-1635383499-|1635750941',
                            'blogAppAd_blog7article': '1',
                            'CNZZDATA1280552662': '1167568446-1637545331-|1637545331',
                            'CNZZDATA1280552818': '878131494-1637538392-|1637538392',
                            'CNZZDATA1280552725': '2020007201-1637543651-|1637543651',
                            'name': 'sinaAds',
                            'post': 'massage',
                            'page': '23333',
                            'dlg680': '11',
                            'blogAppAd_blog7articlelistM': '1',
                            'blogAppAd_blog7articleM': '1',
                            'NowDate': 'Wed Dec 01 2021 16:50:11 GMT+0800 (中国标准时间)',
                          "rotatecount": "5",
                          "SCF": "AvgfNVcBXUfJUWwjAfOWzA1iyMN5H5zckkW7HluOYDsbf1ipEVAz8IGbu_uINxFuXFumgy0Fa4tMEAsEe-IfImE.",
                          "SessionID": "2137us6ujnpq84ua5goqd700f0",
                          "SINABLOGNUINFO": "2179882845.81ee5f5d.",
                          "SINAGLOBAL": "125.71.226.26_1624504398.105329",
                          "SUB": "_2A25MooHqDeRhGeRP7FsZ-CzEzzmIHXVv2fQirDV_PUNbm9AfLRTkkW9NUBMdaWuxMbrTkWCxQJoQivjeUYAOZnDa",
                          "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WFW_wTf_gKjikY4Ligh9dk45NHD95QEeKM41hnE1hBfWs4Dqcj.i--4i-zRi-zfi--4i-zRiKLsi--ciKnXiKysi--Ri-8siKnc",
                          "U_TRS1": "0000001a.ab134fb4.60d3f84c.0e18dc6b",
                          "U_TRS2": "0000001a.bec215803.619c8672.4fdf97de",
                          "ULV": "1638330821032:6:1:1:125.71.226.26_1637647983.887650:1637548845935",
                          "UM_distinctid": "17af6baa3d43d5-08e9f4a50199a38-4c3f2d73-1fa400-17af6baa3d51a6",
                          "UOR": "www.baidu.com,blog.sina.com.cn,",
                                 "IDC_LOGIN": "BJ:1638330826",
                                              "mblog_userinfo": "uid=2179882845&nick=淡然",
                          "BLOG_TITLE": "淡然的博客",
                          "__gads": "ID=31b9bd1679463cb2-225291bf99ca0079:T=1627637066:RT=1627637066:S=ALNI_MbmYG9EwoQxrNcB-omgQqh9z-kl9A",
                          "_s_loginStatus": "2179882845",
                          "_s_loginuid": "2179882845",
                          "Apache": "125.71.226.26_1637647983.887650",
                      },
                      })
  th.start()
  th.join()

