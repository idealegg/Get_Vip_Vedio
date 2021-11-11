# -*- coding:utf-8 -*-
import time
import RedirectOut.RedirectOut
from GetSensBase.GetSensBase import GetSensBase


if __name__ == "__main__":
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  th = GetSensBase(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 1,
                         'session_number': 4,
                         'threading_num': 8,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'key'],
                         'sen_info_path': 'sens_info_m1907.txt',
                         })
  th.start()
  th.join()