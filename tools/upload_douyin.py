#!*---coding:utf8--*
import cv2
from PIL import ImageEnhance, Image, ImageDraw, ImageFont
import sys
import numpy as np
import time
import os
import shutil
import json
import requests


video = ''
cookies = "passport_csrf_token_default=2583726e0df3708bdf2687440a61761d; passport_csrf_token=2583726e0df3708bdf2687440a61761d; n_mh=E4LH3KUbk0MHVlJw1YGj2YpaOb2Qsxh_0INe1GvW2LA; sso_uid_tt=b3bd67d8401acf2dc0591c29132fe646; sso_uid_tt_ss=b3bd67d8401acf2dc0591c29132fe646; toutiao_sso_user=fe817d36feee72d2f359495944b19f50; toutiao_sso_user_ss=fe817d36feee72d2f359495944b19f50; odin_tt=7b9b92cc9e35534fc87a7f3677963e1fa293c4debbeea13a541d66072c140af3e0c98a4124cd1677599f4fffed0efb0b78581ef95725ccc00f5023960481341b; passport_auth_status_ss=c0886d398f63830f9a9b6d440e8daac7,; sid_guard=2cc3e90c2cbd9ded446dda52e4f31ebf|1618379799|5184000|Sun,+13-Jun-2021+05:56:39+GMT; uid_tt=7ac3126e96ecd6c52062b5ba5929f4a1; uid_tt_ss=7ac3126e96ecd6c52062b5ba5929f4a1; sid_tt=2cc3e90c2cbd9ded446dda52e4f31ebf; sessionid=2cc3e90c2cbd9ded446dda52e4f31ebf; sessionid_ss=2cc3e90c2cbd9ded446dda52e4f31ebf; passport_auth_status=c0886d398f63830f9a9b6d440e8daac7,; ttwid=1|D08Dbs-XKExtwZYGeUI-SCI-caIQ_xgehT1XWOPRdUU|1620701638|0f46f9b2d020fe9e540e7f283af72a8ed8937719f17f9d1e78fd95336135f66a; csrf_token=QDBoCBtBGZBEvHRUriMMQHnQvpMvtAxV"
headers = {
    'Cookie': cookies,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}
# 1. 获取认证信息
url = 'https://media.douyin.com/web/api/media/upload/auth/'
req = requests.get(url, headers=headers)
print(req)
print(req.content)
if req.status_code != 200:
    exit(1)
j1 = json.loads(req.content)
if 'status_code' not in j1 or j1['status_code'] != 0:
    exit(2)
with open('auth.json', 'wb') as fd:
    fd.write(req.content)
ak = j1['ak']
auth = j1['auth']
# 2. 获取视频上传参数
url = 'https://vas-lf-x.snssdk.com/video/openapi/v1/'
params = {
    "action": "GetVideoUploadParams",
    "use_edge_node": 1,
}
headers = {
    'authorization': auth,
    'x-tt-access': ak,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}
req = requests.get(url, params=params, headers=headers)
print(req)
print(req.content)
if req.status_code != 200:
    exit(3)
j2 = json.loads(req.content)
if 'message' not in j2 or j2['message'] != 'ok':
    exit(4)
with open('param.json', 'wb') as fd:
    fd.write(req.content)
vid = j2['data']['edge_nodes'][0]['vid']
oid = j2['data']['edge_nodes'][0]['oid']
tos_sign = j2['data']['edge_nodes'][0]['tos_sign']
tos_host = j2['data']['edge_nodes'][0]['tos_host']
extra_param = j2['data']['edge_nodes'][0]['extra_param']
token = j2['data']['edge_nodes'][0]['token']

# 3. 上传视频
url = "https://%s/%s" % (tos_host, oid)
headers = {
    'Content-Type': 'application/octet-stream',
    'Authorization': tos_sign,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}
with open(video, 'rb') as fd:
    vdata = fd.read()
req = requests.post(url, data=vdata, headers=headers)
print(req)
print(req.content)
if req.status_code != 200:
    exit(5)

# 4. 更新视频上传信息
url = 'https://vas-lf-x.snssdk.com/video/openapi/v1/?action=UpdateVideoUploadInfos&%s' % extra_param
headers = {
    'authorization': auth,
    'x-tt-access': ak,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}
j3 = {
    "vid": vid,
    "oid": oid,
    "token": token,
    "poster_ss": 0,
    "is_exact_poster": "true",
    "user_reference": ""
}
req = requests.post(url, data=vdata, headers=headers)
print(req)
print(req.content)
if req.status_code != 200:
    exit(6)

# 5. 发布视频
url = 'https://media.douyin.com/web/api/media/aweme/create/'
headers = {
 'cookie': cookies,
 'csrf_token': csrf_token,
}
pdata={
    'video_id': vid,
    'poster': oid,
    'poster_delay': 0,
    'text': '',
    'text_extra': [{'start':0,'end':3,'user_id':"",'type':1,'hashtag_name':'音乐'}],
    'challenges': ['1550712576368642'],
    'mentions': [],
    'visibility_type': 0,
    'third_text': '遇见就是一种缘分',
    'download': 0,
    'upload_source': 1,
    'mix_id': '',
    'mix_order': '',
    'is_preview': 0,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
}

