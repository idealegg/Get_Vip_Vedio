# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class Runoob(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(Runoob, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find_all('div', class_="article-body")
        found = container is not None
        logger.info(container)
        body = soup.find('body')
        if found:
            body.contents = container
        return soup, found

    def find_menu_container(self, s):
        return s.find('div', class_='design', attrs={'id': 'leftcolumn'})



if __name__ == "__main__":
  setup_logging()
  th = Runoob(conf={'base_dir': r'E:\hzw',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         })
  th.start()
  th.join()

