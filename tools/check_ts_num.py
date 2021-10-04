# -*- coding:utf-8 -*-

import os
import sys
import shutil
import re
import threading


store_dir = r'E:\hzw\store'

cur_dir = os.getcwd()
os.chdir(store_dir)
f_list = os.listdir('.')
m3u8_list = list(filter(lambda x: x.endswith('.m3u8'), f_list))
for m3u8 in m3u8_list:
	sen = m3u8.replace('.m3u8', '')
	ts_list1 = list(filter(lambda x: x.startswith('%s_' % sen) and x.endswith('.ts'), f_list))
	ts_num2 = 0
	with open(m3u8, 'r') as fd:
		for line in fd:
			if not line.startswith('#'):
				ts_num2 += 1
	no_downloads = []
	for i in range(ts_num2):
		ts_name = "%s_%d.ts"%(sen, i)
		if ts_name not in ts_list1:
			no_downloads.append(ts_name)
	print("sen:[%s]m3u8: [%s], ts: [%s]"%(sen, ts_num2, len(ts_list1)))
	print("no downloads: [%s]" % no_downloads)