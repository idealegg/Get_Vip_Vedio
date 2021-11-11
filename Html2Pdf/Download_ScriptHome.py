# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class ScriptHome(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(ScriptHome, self).__init__(conf)

    def replace_body(self, soup):
        container = soup.find('div')
        logger.info(container)
        body = soup.find('body')
        body.contents = container
        return soup

    def find_menu_container(self, s):
        return s.find_all('ul')[0]

    def find_all_hrefs(self, container):
        return container.find_all('a')

    def format_header(self, soup):
        return soup

if __name__ == "__main__":
  setup_logging()
  th = ScriptHome(conf={'base_dir': r'E:\hzw\ScriptHome',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'url',
                         'concat_from_right': True,
                        'encoding': None,
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_ScriptHome.txt'),
                         })
  th.start()
  th.join()

