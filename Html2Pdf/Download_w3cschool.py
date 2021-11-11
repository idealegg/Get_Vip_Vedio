# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class W3cschool(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(W3cschool, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find(class_="main-container font0")
        body = soup.find('body')
        body.contents = container
        return soup

    def find_menu_container(self, s):
        return s.find(class_="dd-list")


if __name__ == "__main__":
  setup_logging()
  th = W3cschool(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'url',
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_w3cschool.txt'),
                         'headers':{
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.w3cschool.cn",
    "Pragma": "no-cache",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",}
      })
  th.start()
  th.join()
