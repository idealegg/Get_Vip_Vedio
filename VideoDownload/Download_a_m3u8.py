# -*- coding:utf-8 -*-
from Common.GetSensBase import GetSensBase
from Util.myLogging import *


if __name__ == "__main__":
  setup_logging()
  #RedirectOut.RedirectOut.__redirection__('out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S"))
  th = GetSensBase(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 1,
                         'session_number': 4,
                         'threading_num': 8,
                         'wait_session_sleep_time': 0.1,
                         'sen_field_name': ['sen', 'name', 'url', 'key'],
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_m1907.txt'),
                         })
  th.start()
  th.join()