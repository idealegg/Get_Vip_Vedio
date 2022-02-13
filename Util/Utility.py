# -*- coding: utf-8 -*-

import json
import logging.config
import os
import functools
import sys


def get_json(f_path, return_str=True):
    fd = open(f_path, 'r' if return_str else 'rb')
    j = json.load(fd)
    fd.close()
    return j

def save_json(obj, f_path, is_bin=False):
    fd = open(f_path, 'wb' if is_bin else 'w')
    json.dump(obj, fd)
    fd.close()
