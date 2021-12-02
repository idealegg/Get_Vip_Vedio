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

    def get_url_list(self, f):
        urls = {}
        fname = "%s_%s.pdf" % (self.sen, 0)
        urls[fname] = {
              'url': self.info['url'],
              'level': 1,
              'label': self.info['name'],
              'index': 0,
              'file': fname,
              }
        logger.info("%s" % urls)
        with open(f, 'w') as jf:
            json.dump(urls, jf)


if __name__ == "__main__":
  setup_logging()
  th = Csdn(conf={'base_dir': r'D:\material\learning\python\web_downloads',
                         'check_downloaded_retry': 1,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                  'remove_pdf': False,
                  'remove_html': False,
                  'headers': {
                        'Host': 'blog.csdn.net',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': 'https://www.baidu.com/link?url=ilQrSEJwssoykwT5yzSW0_-anH_dYK3jZZwDLpdcuuMTlO7IU9AmAr95X4xLXO5PqkZwoo--erHJY3arQdw2Ka_X3DKZpAvHmJb8dkONi2m&wd=&eqid=f37fa5b80009a7b90000000661a864fb',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                  },
                  'cookies':{
                          "__gads": "ID=1f3393905fb107c0-2240577f41cb00d0:T=1630554504:RT=1630554504:S=ALNI_MbmZ_122vrFITzCbu4MUxi-dich8Q",
                          "AU": "873",
                          "BAIDU_SSP_lcr": "https://www.baidu.com/link?url=ilQrSEJwssoykwT5yzSW0_-anH_dYK3jZZwDLpdcuuMTlO7IU9AmAr95X4xLXO5PqkZwoo--erHJY3arQdw2Ka_X3DKZpAvHmJb8dkONi2m&wd=&eqid=f37fa5b80009a7b90000000661a864fb",
                          "BT": "1634286825697",
                          "c_dl_fpage": "/download/zenliang/7834707",
                          "c_dl_fref": "https://blog.csdn.net/renlonggg/article/details/73550306",
                          "c_dl_prid": "1637549575485_550949",
                          "c_dl_rid": "1638153835485_111923",
                          "c_dl_um": "-",
                          "c_first_page": "https://blog.csdn.net/zhoulei124/article/details/89055403",
                          "c_first_ref": "www.baidu.com",
                          "c_page_id": "default",
                          "c_pref": "https://www.baidu.com/link",
                          "c_ref": "https://www.baidu.com/link",
                          "c_segment": "11",
                          "dc_session_id": "10_1638425858005.201192",
                          "dc_sid": "cd22a1a6091fffa33450f009bee33631",
                          "dc_tos": "r3h5he",
                          "Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac": "6525*1*10_21018629380-1630554444801-889467!5744*1*u013361444",
                          "Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac": "1638425859",
                          "Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac": "1638339463,1638344111,1638344151,1638425859",
                          "Hm_lvt_e5ef47b9f471504959267fd614d579cd": "1634645239,1635836096",
                          "Hm_up_6bcd52f51e9b3dce32bec4a3997715ac": "{\"islogin\":{\"value\":\"1\",\"scope\":1},\"isonline\":{\"value\":\"1\",\"scope\":1},\"isvip\":{\"value\":\"0\",\"scope\":1},\"uid_\":{\"value\":\"u013361444\",\"scope\":1}}",
                          "log_Id_click": "205",
                          "log_Id_pv": "549",
                          "log_Id_view": "1846",
                          "p_uid": "U010000",
                          "ssxmod_itna": "eqjhAIqmx0xUxQqGKGHRx6Qke97B0W=D2i1D0yiPGzDAxn40iDtrxd2DDqPittYngDcx1iRnThtaS9E3gRzSSh4KwfIWix0aDbqGkinFG4GGAxBYDQxAYDGDDPDoZPD1D3qDk0xYPGWCqGfDDoDYR=nDitD4qDBCEdDKqGgCwDYn264M32M+jtY3lqyD0UoxBLqt=uKraa1lqPnDB6OxBjlUu=S+eDHAixoio7UDqDRIPGMfmKDAR6xnEH1D75ylSd4m08D0Tk3BOozGBRbGA54SxqYKihdqE5oCYq0EH5DG38QKTD==",
                          "ssxmod_itna2": "eqjhAIqmx0xUxQqGKGHRx6Qke97B0W=D2DnIoBxDsQQD0Dj4mRrlyhu3idqDgeL5hkeBooA=il/PC0rpMCelEth=pa7Ej1NdUkBtYy7A=ABjMD9MFaixaQq4NkLrNYKFRMGsy0ROj6+Q0xhCqKBhAoFbaxeii=eaKxY8lPBz20Hr7PB1Rm0dLBOQGU4CRY+ABPvELfm=7EuEx4drLQeFPhkvLF7L2Ub63=n13xnOP=DhxzCGbEO0yeBiikqsmoa2PoaUItW9m2m9+/WGQBfjUIlf5eSj31e0CIa2lFjty2Af1E3R6bjteuOnhQmWZR4CnH+b52FyDyHGeqVUqs4Yp0yf7GCb+6jmbl7SS9AKifUqIW+oXwXeuoc2URRgDFxzT5yROYqeQgey4nmb10vNsA8Uy3WqVWuqxTPwFdXaTUxdzHSfTBAo4rvoD07i05XitqiK/7xuGx9GLzaWyrjefj2GDXDDLxD2zhDD",
                          "UN": "u013361444",
                          "UserInfo": "a700b3bce5754392a7fe23c4ec001e19",
                          "UserName": "u013361444",
                          "UserNick": "huangdian8018",
                          "UserToken": "a700b3bce5754392a7fe23c4ec001e19",
                          "uuid_tt_dd": "10_21018629380-1630554444801-889467"
                      }
                  })
  th.start()
  th.join()
