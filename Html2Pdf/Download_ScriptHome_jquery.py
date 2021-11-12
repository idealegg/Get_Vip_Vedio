# coding=utf-8
from Util.myLogging import *
from Common.Html2PdfBase import Html2PdfBase


class ScriptHomeJQuery(Html2PdfBase):
    def __init__(self, conf=Html2PdfBase.default_conf):
        super(ScriptHomeJQuery, self).__init__(conf)

    def replace_body(self, soup):
        container = list(filter(lambda x: x.has_attr('rel'), soup.find_all('div')))[0]
        found = container is not None
        logger.info(container)
        body = soup.find('body')
        body.contents = container
        return soup, found

    def find_all_hrefs(self, container):
        return container.find_all(['h2', 'a'])

    #def find_menu_container(self, s):
    #    return s

#    def format_header(self, soup):
#        return soup

if __name__ == "__main__":
  setup_logging()
  th = ScriptHomeJQuery(conf={'base_dir': r'E:\hzw\ScriptHomeJQuery',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         'concat_from_right': True,
                         'html_encoding': None,
                         'save_encoding': 'utf8',
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_ScriptHome.txt'),
                         })
  th.start()
  th.join()

