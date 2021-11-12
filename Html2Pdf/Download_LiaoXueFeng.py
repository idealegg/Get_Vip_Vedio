# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class LiaoXueFeng(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(LiaoXueFeng, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find_all(class_="x-wiki-content")[0]
        found = container is not None
        body = soup.find('body')
        body.contents = container
        return soup, found

    def find_menu_container(self, s):
        return s.find_all(class_="uk-nav uk-nav-side")[1]


if __name__ == "__main__":
  setup_logging()
  th = LiaoXueFeng(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_LiaoXueFeng.txt'),
                         'headers':{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",}
      })
  th.start()
  th.join()

