# -*- coding:utf-8 -*-
import os
import re


'''
ffmpeg -i input1.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input1.ts
ffmpeg -i input2.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input2.ts
ffmpeg -i input3.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input3.ts
ffmpeg -i "concat:input1.ts|input2.ts|input3.ts" -c copy -bsf:a aac_adtstoasc -movflags +faststart output.mp4
'''

st_pattern = re.compile('lasttimestamp\s*:\s*(\d+)')


def convert2ts(f4v):
  ret = [None, 0]
  ts = os.path.basename(f4v)
  ts = ts.replace('f4v', 'ts')
  fd = os.popen('avconv -i %s -c copy -bsf:v h264_mp4toannexb -f mpegts -y %s 2>&1' % (f4v, ts))
  for line in fd:
    print line
    # lasttimestamp   : 374
    res = re.search(st_pattern, line)
    if res:
      ret = [ts, int(res.group(1), 10)]
  fd.close()
  return ret


def concatf4v(ts_list, durition, target):
  fd = os.popen('avconv -i "concat:%s" -c copy -bsf:a aac_adtstoasc -movflags +faststart -ss 00:02:10 -t %d -y %s' %
                ('|'.join(ts_list), durition - 240, os.path.join(target, ts_list[0].replace('_0', '').replace('ts', 'mp4'))))
  for line in fd:
    print line
  for ts in ts_list:
    os.remove(ts)
  fd.close()


def merge(f4v_list, target):
  ts_list = []
  durition = 0
  for f4v in f4v_list:
    print f4v
    ts, dur = convert2ts(f4v)
    ts_list.append(ts)
    durition = dur
  concatf4v(ts_list, durition, target)


if __name__ == "__main__":
  import RedirectOut.RedirectOut
  import time
  # target = "C:\\works\\qsv2flv\\merge"
  store_dir = "D:\\movies\\haizeiwang"
  check_dirs = [store_dir, "C:\\works\\Get_Vip_Vedio.orig"]
  target = "D:\\movies\\haizeiwang\\merge"
  RedirectOut.RedirectOut.__redirection__(os.path.join(target, 'out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S")))
  # file_list = map(lambda x: os.path.join(target, x), map(lambda x: '78_%1d.f4v' % x, range(4)))
  sens = {}
  for file in os.listdir(check_dirs[1]):
    if file.endswith('.f4v'):
      key = file[:-6]
      if sens.has_key(key):
        sens[key].append(os.path.join(check_dirs[1], file))
      else:
        sens[key] = []
        sens[key].append(os.path.join(check_dirs[1], file))
  keys = sens.keys()
  keys.sort(cmp=lambda x, y: cmp(int(x[:-2], 10), int(y[:-2], 10)))
  for key in keys:
    if sens[key]:
      sens[key].sort()
      merge(sens[key], target)