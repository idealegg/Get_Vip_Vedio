# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase
from bs4 import BeautifulSoup


class Csdn(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(Csdn, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find(class_="blog-content-box")
        body = soup.find('body')
        body.contents = container
        return soup, True

    def find_menu_container(self, s):
        return s

    def find_all_hrefs(self, container):
        title = (container.find(class_='title-article') or container.find(class_='tit')).text
        url = self.info['url']
        return [BeautifulSoup('<a href="%s" >%s</a>' % (url, title), 'html.parser').find('a')]


if __name__ == "__main__":
  setup_logging()
  th = Csdn(conf={'base_dir': r'D:\material\learning\python\web_downloads',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                  'remove_pdf': False,
                  'remove_html': False,
                  })
  th.start()
  th.join()
