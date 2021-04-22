# -*- coding:utf-8 -*-
import os
import re
import shutil
import threading


'''
ffmpeg -i input1.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input1.ts
ffmpeg -i input2.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input2.ts
ffmpeg -i input3.flv -c copy -bsf:v h264_mp4toannexb -f mpegts input3.ts
ffmpeg -i "concat:input1.ts|input2.ts|input3.ts" -c copy -bsf:a aac_adtstoasc -movflags +faststart output.mp4
'''

st_pattern = re.compile('lasttimestamp\s*:\s*(\d+)')
move_lock =threading.Lock()


def convert2ts(f4v, des=None):
  ret = [None, 0]
  print f4v
  print type(f4v)
  if des:
    ts = des
  else:
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


def get_ts_info(ts):
  fd = os.popen('avconv -i "%s" 2>&1' % ts)
  info = {}
  for line in fd:
    if line.startswith('Input #0'):
      fields = line.split(',')
      info['type'] = fields[1].strip()
    elif line.strip().startswith('Duration:'):
      fields = line.split(',')
      for field in fields:
        tmps = field.split(':')
        info[tmps[0].strip()] = tmps[1].strip()
  fd.close()
  return info


def exec_concat_cmd(ts_list, duration, cut_flag, new_target):
  print "exec_concat_cmd: ts_list: [%s]" % '|'.join(ts_list)
  print "durition: %d, target: %s, cut_flag: %s" % (duration, new_target, cut_flag)
  i = 0
  j = 0
  max_ts_a_time_in_cmd = 720
  new_ts_name = '_'.join(['merge', ts_list[0].replace('_0', '_%d')])
  ts_list2 = []
  ts_list3 = []
  if len(ts_list) > max_ts_a_time_in_cmd:
    ts_info = get_ts_info(ts_list[0])
    if ('type' in ts_info and ts_info['type'] != 'mpegts') or (
      'start' in ts_info and float(ts_info['start']) > 2
    ):
      for ts in ts_list:
        flv_ts = "_".join(['flv', ts])
        ts_list3.append(flv_ts)
        os.rename(ts, flv_ts)
        convert2ts(flv_ts, ts)
    while len(ts_list) - i > 0:
      ts_num = min(len(ts_list) - i, max_ts_a_time_in_cmd)
      cmd = 'avconv -i "concat:%s" -c copy -y %s 2>&1' % (
        '|'.join(ts_list[i:i+ts_num]),
        new_ts_name % j)
      print "cmd: %s" % cmd
      fd = os.popen(cmd)
      for line in fd:
        print line
      fd.close()
      ts_list2.append(new_ts_name % j)
      i += ts_num
      j += 1
  #cmd = 'avconv -i "concat:%s" -c copy -bsf:a aac_adtstoasc -movflags +faststart %s -y %s 2>&1' % (
  cmd = 'avconv -i "concat:%s" -c copy -movflags +faststart %s -y %s 2>&1' % (
                   '|'.join(ts_list2 if len(ts_list) > max_ts_a_time_in_cmd else ts_list),
                   "-ss 00:02:10 -t %d" % (duration - 240) if cut_flag else '',
                   new_target)
  print "cmd: %s" % cmd
  fd = os.popen(cmd)
  for line in fd:
    print line
  fd.close()
  for ts in ts_list2:
    os.remove(ts)


def concatf4v(ts_list, duration, target, convert_flag=True, cut_flag=True):
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
    new_target = ts_list_new[0].replace('_0', '').replace('ts', 'mp4')
  exec_concat_cmd(ts_list_new, duration, cut_flag, new_target)
  if os.path.isdir(target):
    if os.path.isfile(os.path.join(target, new_target)):
      print "[%s] or [%s] already exists!\n" % (new_target, target)
    elif not os.path.isfile(new_target):
      print "[%s] is merged fialed!\n" % (new_target)
    else:
      move_lock.acquire()
      shutil.move(new_target, target)
      move_lock.release()
  os.chdir(origin)
  if convert_flag:
    for ts in ts_list:
      os.remove(ts)


def merge(src_list, target, convert_flag=True, cut_flag=True):
  ts_list = []
  duration = 0
  print src_list
  if convert_flag:
    for f4v in src_list:
      print f4v
      ts, dur = convert2ts(f4v)
      ts_list.append(ts)
      duration = dur
  else:
    ts_list = src_list
  concatf4v(ts_list, duration, target, convert_flag, cut_flag)


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