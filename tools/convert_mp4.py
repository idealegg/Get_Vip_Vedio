# -*- coding:utf-8 -*-

import os
import sys
import shutil
import re
import threading


max_dur = 14 * 60


def get_offset(offset):
	sec = offset % 60
	mi = offset // 60
	ho = mi // 60
	mi = mi % 60
	return "%02d:%02d:%02d" % (ho, mi, sec)

def do_task(cmds):
	for cmd in cmds:
		print(cmd)
		os.system(cmd)

def split_mp4(mp4_inf):
	mp4 = mp4_inf['name']
	cmd = "avconv -i %s 2>&1|grep Duration" % mp4
	tmp = os.popen(cmd)
	duration = 0
	offset = mp4_inf['start']
	endt = mp4_inf['end']
	th_list = []
	for line in tmp:
		print(line)
		if line.count("Duration:"):
			res = re.search("Duration:\s*(\d{2}):(\d{2}):(\d{2}).(\d{2}),", line)
			if res:
				duration = int(res.group(1)) * 3600 + int(res.group(2)) * 60 + int(res.group(3)) + int(res.group(4))/100
				print("Get a duration: %s" % duration)
				break
	while duration - endt > offset:
		index = str(offset // max_dur +1)
		slice_n = "".join([mp4.replace(".mp4", ''), '_', index, ".mp4"])
		slice_n2 = "".join([mp4.replace(".mp4", ''), '_', index, "_2", ".mp4"])
		cmd = "avconv -i %s -ss %s -t %s -vf transpose=1 -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n)
		#cmd = "avconv -i %s -ss %s -t %s -c copy -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n2)
		#cmd1 = "avconv -i %s -vf transpose=1 -y %s 2>&1" %(slice_n2, slice_n)
		#cmd2 = "rm %s" % slice_n2
		do_task([cmd])
		offset += max_dur

def main(mp4s):
	for mp4 in mp4s:
		split_mp4(mp4)

if __name__ == "__main__":
	main([
		 {'name': u"【09dota超清提高班】纯爷们第一视角.mp4", 'start': 30 + max_dur * 0, 'end': 0},
		 {'name': u"【09dota超清提高班】月之骑士.mp4", 'start': 22 + max_dur * 0, 'end': 0},
		])