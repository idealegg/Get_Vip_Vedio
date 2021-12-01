# coding=utf-8
import requests
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class BoHaiXiaoLi(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(BoHaiXiaoLi, self).__init__(conf)

    def format_header(self, soup):
        return soup

    def find_all_hrefs2(self, container):
        links = container.find_all('a', class_='list_item js_post')
        if not links:
            links = list(map(lambda x: x.find_all('a')[-1],
                            filter(lambda x: x.contents
                                  and x.find_all('a')
                                  and (x.find_all('a')[-1].find_all('strong') or x.find_all('a')[-1].find_parents('strong')),
                                   container.find_all('p'))))
        logger.info(links)
        return links

    def find_all_hrefs(self, container):
        links = list(filter(lambda x:x.has_attr('data-link') and x.has_attr('data-title'),
                            container.find_all('li')))
        logger.info(links)
        return links

    def get_url_list(self, f):
        urls = {}
        iurl = 'https://mp.weixin.qq.com/mp/appmsgalbum'
        begin_msgid = self.info['begin_msgid']
        i = 0
        while begin_msgid:
            self.conf['params']['begin_msgid'] = begin_msgid
            req = requests.get(iurl, headers=self.conf['headers2'], params=self.conf['params'])
            if req.status_code == 200:
                ij = json.loads(req.content)
                import pprint
                pprint.pprint(ij)
                for item in ij['getalbum_resp']['article_list']:
                    level = 0
                    fname = "%s_%s.pdf" % (self.sen, i)
                    urls[fname] = item
                    url = item['url']
                    if url and not url.startswith('http') and self.conf['append_url_before'] and 'url' in self.info and self.info['url']:
                        url = Html2PdfBase.concat_url(self.info['url'], url)
                    urls[fname].update({
                          'url': url,
                          'level': 1,
                          'label': item['title'],
                          'index': i,
                          'file': fname,
                          })
                    begin_msgid = item['msgid']
                    logger.info("%*d %s" % (level, level, item))
                    i += 1
                if ij['getalbum_resp']['continue_flag'] == '0':
                    begin_msgid = None
            else:
                begin_msgid = None
        with open(f, 'w') as jf:
            json.dump(urls, jf)


if __name__ == "__main__":
  setup_logging()
  th = BoHaiXiaoLi(conf={'base_dir': r'E:\hzw',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'album_id', 'begin_msgid'],
                         'src_type': 'file',
                         'headers':{
                             "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
                         },
                         'params':{"action": 'getalbum',
                                    "__biz": 'MzUyMzUyNzM4Ng==',
                                    "album_id": '2091728990028824579',
                                    "count": '10',
                                    "begin_msgid": '2247503545',
                                    "begin_itemidx": '1',
                                    "uin": '',
                                    "key": '',
                                    "pass_ticket": '',
                                    "wxtoken": '',
                                    "devicetype": '',
                                    "clientversion": '',
                                    "__biz": 'MzUyMzUyNzM4Ng==',
                                    "appmsg_token": '',
                                    "x5": '0',
                                    "f": 'json',},
                         'headers2':{
    "accept": '*/*',
    "accept-encoding": 'gzip, deflate, br',
    "accept-language": 'zh-CN,zh;q=0.9',
    "cache-control": 'no-cache',
    "pragma": 'no-cache',
    "referer": 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzUyMzUyNzM4Ng==&action=getalbum&album_id=2091728990028824579',
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": '?0',
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": 'empty',
    "sec-fetch-mode": 'cors',
    "sec-fetch-site": 'same-origin',
    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    "x-requested-with": 'XMLHttpRequest',}
                         })
  th.start()
  th.join()

