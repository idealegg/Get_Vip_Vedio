# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class ScriptHomeCSS(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(ScriptHomeCSS, self).__init__(conf)

    def replace_body(self, soup):
        divs = soup.find_all('div')
        if self.info['name'] in ['css', 'Python']:
            container = divs[0]
        elif self.info['name'] == 'Shell':
            container = divs[1]
        elif self.info['name'] == 'Jscript':
            return soup, True
        found = container is not None
        logger.info(container)
        body = soup.find('body')
        body.contents = container
        return soup, found

    def find_menu_container(self, s):
        #return s.find_all('ul')[0]
        return s


if __name__ == "__main__":
  setup_logging()
  th = ScriptHomeCSS(conf={'base_dir': r'E:\hzw\ScriptHomeCSS',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         'concat_from_right': True,
                         'html_encoding': 'gb18030',
                         'save_encoding': 'utf8',
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_ScriptHomeCSS.txt'),
                         })
  th.start()
  th.join()

