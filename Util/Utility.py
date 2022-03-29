# -*- coding: utf-8 -*-

import json
import logging.config
import os
import functools
import sys
import binascii as bs


def get_json(f_path, return_str=True):
    fd = open(f_path, 'r' if return_str else 'rb')
    j = json.load(fd)
    fd.close()
    return j

def save_json(obj, f_path, is_bin=False):
    fd = open(f_path, 'wb' if is_bin else 'w')
    json.dump(obj, fd)
    fd.close()

def to_str(bt, encoding='utf8'):
    if isinstance(bt, bytes):
      bt = bt.decode(encoding)
    return bt

def to_bytes(s, encoding='utf8'):
    if isinstance(s, str):
      s = s.encode(encoding)
    return s

def decode_hex2str(hbytes):
    return bs.unhexlify(hbytes).decode('unicode_escape')