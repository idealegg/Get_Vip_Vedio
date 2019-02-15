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
  print f4v
  print type(f4v)
  ts = os.path.basename(f4v)
  ts = ts.replace('f4v', 'ts')
  print ts
  print type(ts)
  fd = os.popen('avconv -i "%s" -c copy -bsf:v h264_mp4toannexb -f mpegts -y "%s" 2>&1' % (f4v, ts))
  for line in fd:
    print line
    # lasttimestamp   : 374
    res = re.search(st_pattern, line)
    if res:
      ret = [ts, int(res.group(1), 10)]
  fd.close()
  return ret


def concatf4v(ts_list, durition, target, convert_flag=True, cut_flag=True):
  origin = os.getcwd()
  new_dir = os.path.dirname(ts_list[0])
  if not new_dir:
    new_dir = '.'
  print "origin: %s, new dir: %s" % (origin, new_dir)
  os.chdir(new_dir)
  ts_list_new = map(lambda x: os.path.basename(x), ts_list)
  if not os.path.isdir(target):
    new_target = target
  else:
    new_target = os.path.join(target, ts_list_new[0].replace('_0', '').replace('ts', 'mp4'))
  print "concatf4v: ts_list: [%s]" % '|'.join(ts_list_new)
  print "durition: %d, target: %s, convert_flag: %s, cut_flag: %s" % (durition, new_target, convert_flag, cut_flag)
  cmd = 'avconv -i "concat:%s" -c copy -bsf:a aac_adtstoasc -movflags +faststart %s -y %s 2>&1' % (
                 '|'.join(ts_list_new),
                 "-ss 00:02:10 -t %d" % (durition - 240) if cut_flag else '',
                 new_target)
  print "cmd: %s" % cmd
  fd = os.popen(cmd)
  for line in fd:
    print line
  fd.close()
  os.chdir(origin)
  if convert_flag:
    for ts in ts_list:
      os.remove(ts)


def merge(src_list, target, convert_flag=True, cut_flag=True):
  ts_list = []
  durition = 0
  print src_list
  if convert_flag:
    for f4v in src_list:
      print f4v
      ts, dur = convert2ts(f4v)
      ts_list.append(ts)
      durition = dur
  else:
    ts_list = src_list
  concatf4v(ts_list, durition, target, convert_flag, cut_flag)


if __name__ == "__main__":
  import RedirectOut.RedirectOut
  import time
  # target = "C:\\works\\qsv2flv\\merge"
  store_dir = r"C:\Downloads\store"
  check_dirs = [store_dir, "C:\\works\\Get_Vip_Vedio.orig", "D:\\movies\\haizeiwang\\lost", r"D:\movies\haizeiwang\1_76"]
  target = r"C:\Downloads\merge"
  RedirectOut.RedirectOut.__redirection__(os.path.join(target, 'out_%s.log' % time.strftime("%Y-%m-%d_%H%M%S")))
  # file_list = map(lambda x: os.path.join(target, x), map(lambda x: '78_%1d.f4v' % x, range(4)))
  sens = {}
  index = 0 # choose source file
  for file in os.listdir(check_dirs[index]):
    if file.endswith('.f4v'):
      key = file[:-6]
      if sens.has_key(key):
        sens[key].append(os.path.join(check_dirs[index], file))
      else:
        sens[key] = []
        sens[key].append(os.path.join(check_dirs[index], file))
  keys = sens.keys()
  keys.sort(cmp=lambda x, y: cmp(int(x[:-2], 10), int(y[:-2], 10)))
  for key in keys:
    if sens[key]:
      sens[key].sort()
      merge(sens[key], target)