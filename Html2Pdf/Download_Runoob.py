# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase
from bs4 import BeautifulSoup
import requests


class Runoob(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(Runoob, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find_all('div', class_="article-body")[0]
        found = container is not None
        logger.info(container)
        body = soup.find('body')
        if found:
            body.contents = container
        return soup, found

    def find_menu_container(self, s):
        return s.find('div', class_='design', attrs={'id': 'leftcolumn'})

    def find_all_hrefs(self, container):
        aa = container.find_all('a')
        aa2 = []
        for item in aa:
            aa2.append(item)
            if item.get('title').strip() in ["C 语言经典100例", "C 语言实例"]:
                url = item.get('href')
                if url and not url.startswith('http') and self.conf['append_url_before'] and 'url' in self.info and \
                        self.info['url']:
                    url = Html2PdfBase.concat_url(self.info['url'], url)
                r = requests.get(url, headers=self.conf['headers'])
                soup = BeautifulSoup(r.content, 'html.parser', from_encoding=self.conf['html_encoding'])
                container = soup.find_all('div', class_="article-body")[0]
                aa2.extend(container.find_all('a'))
                for a2 in container.find_all('a'):
                    item.append(a2)
        return aa2



if __name__ == "__main__":
  setup_logging()
  th = Runoob(conf={'base_dir': r'E:\hzw',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         })
  th.start()
  th.join()

