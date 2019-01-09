# -*- coding:utf-8 -*-
import hashlib


def get_token(md5str):
  #生成一个md5对象
  m1 = hashlib.md5()
  #使用md5对象里的update方法md5转换
  m1.update(md5str.encode("utf-8"))
  return m1.hexdigest()


def GetSign(str):
  _0x9ba7 = [
    "\x64\x20\x31\x3D\x5B\x22\x5C\x62\x5C\x33\x5C\x34\x5C\x63\x5C\x35\x5C\x37\x5C\x38\x5C\x33\x5C\x35\x5C\x34\x5C\x39\x5C\x61\x22\x5D\x3B\x36\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x65\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x66\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x67\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x68\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x69\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x6A\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x6B\x29\x2B\x32\x5B\x31\x5B\x30\x5D\x5D\x28\x6C\x29",
    "\x7C", "\x73\x70\x6C\x69\x74",
    "\x7C\x5F\x30\x78\x62\x37\x38\x30\x7C\x53\x74\x72\x69\x6E\x67\x7C\x78\x37\x32\x7C\x78\x36\x46\x7C\x78\x34\x33\x7C\x73\x74\x72\x7C\x78\x36\x38\x7C\x78\x36\x31\x7C\x78\x36\x34\x7C\x78\x36\x35\x7C\x78\x36\x36\x7C\x78\x36\x44\x7C\x76\x61\x72\x7C\x33\x33\x7C\x39\x37\x7C\x39\x38\x7C\x31\x30\x31\x7C\x31\x30\x32\x7C\x35\x37\x7C\x35\x36\x7C\x35\x35",
    "\x72\x65\x70\x6C\x61\x63\x65", "", "\x5C\x77\x2B", "\x5C\x62", "\x67", "\x73\x75\x62\x73\x74\x72\x69\x6E\x67",
    "\x38\x61\x62\x35\x64\x36", "\x6C\x6F\x69\x6A"]
  abc = get_token(str + "!abef987")
  _a = abc[10:22]
  _b = abc[24:30]
  return "".join(["ab59", _b, _0x9ba7[10], _a, _0x9ba7[11]])

if __name__ == "__main__":
  print GetSign('a16db66fa7b078b604db14324ae7cea9')
  print GetSign('8c3818a7671c050906ad1f641a473978')
  print GetSign('0dd41d8b988970ec309cc2b136b5f35d')
  print GetSign('604565ab54514c785f5a0e63812adb8d')