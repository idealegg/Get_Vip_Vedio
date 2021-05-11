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

def split_mp4(mp4):
	cmd = "avconv -i %s 2>&1|grep Duration" % mp4
	tmp = os.popen(cmd)
	duration = 0
	offset = 0
	th_list = []
	for line in tmp:
		print(line)
		if line.count("Duration:"):
			res = re.search("Duration:\s*(\d{2}):(\d{2}):(\d{2}).(\d{2}),", line)
			if res:
				duration = int(res.group(1)) * 3600 + int(res.group(2)) * 60 + int(res.group(3)) + int(res.group(4))/100 
				print("Get a duration: %s" % duration)
				break				
	while duration > (offset+1)*max_dur:
		slice_n = "".join([mp4.replace(".mp4", ''), '_', str(offset+1), ".mp4"])
		slice_n2 = "".join([mp4.replace(".mp4", ''), '_', str(offset+1), "_2", ".mp4"])
		cmd = "avconv -ss %s -i %s -c copy -t %s -y %s 2>&1" %(get_offset(offset*max_dur), mp4, max_dur, slice_n)
		cmd1 = "avconv -i %s -vf transpose=1 -y %s 2>&1" %(slice_n, slice_n2)
		cmd2 = "rm %s" % slice_n
		th = threading.Thread(target=do_task, args=([cmd, cmd1, cmd2],))
		th_list.append(th)
		th.start()
		offset += 1
	for th in th_list:
		th.join()

def main(mp4s):
	for mp4 in mp4s:
		split_mp4(mp4)

if __name__ == "__main__":
	main([
		u"09dota提高班召唤师卡尔的华丽舞步.mp4",
		u"09的影魔体验1第一视角.mp4",
		])