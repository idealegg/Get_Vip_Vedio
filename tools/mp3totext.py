#encoding:utf-8    #设置编码方式
import hashlib
import json
import os
import random
import time
import requests
from requests_toolbelt import MultipartEncoder
from moviepy.video.io.VideoFileClip import VideoFileClip
 
# *********MP4文件的路径地址，注意路径转义 每次修改这个路径*********
mp4FilePath = 'E:\\download\\douyin2的副本\\douyin2的副本\\306026.mp4'
 
 
# 分隔符，上传文件需要
boundary = '----WebKitFormBoundarydXKxqoF1Oi2HdYCd'
 
header = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'http://voice.xunjiepdf.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9'
}
 
# 上传时用这个header，这个boundary要和请求中files的boundary保持一致，否则上传会报错
update_header = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'content-type': 'multipart/form-data; boundary=' + boundary,
    'accept-language': 'zh-CN,zh;q=0.9'
}
 
# 用于请求的基地址BaseUrl
BASE_URL = 'https://user.api.hudunsoft.com'
 
# md5转Text
MD5_TO_TEXT_URL = BASE_URL + '/v1/alivoice/md5Totext'
 
# 查询任务进度
TASK_INFO = BASE_URL + '/v1/alivoice/getTaskInfo'
 
# 上传相关的url
UPLOAD_AUDIO_FILE = BASE_URL + '/v1/alivoice/uploadaudiofile?r=' + str(random.uniform(0, 1))
 
# 这里只用到了一个post请求，所以封装成一个方法
def post(url, body, header):
    requests.packages.urllib3.disable_warnings()
    return requests.post(url=url, data=body, headers=header, verify=False)
 
# 任务开始、结束、删除，都使用这个方法,只需要传入file_info及action动作即可  action：'Begin'、'End'、'Delete'
def upload_operate(file_info, action):
    body = {'action': action,
            'fileName': file_info['fileName'],
            'md5': file_info['md5']
            }
    return post(UPLOAD_AUDIO_FILE, body, header)
 
# 根据文件路径返回文件名称
def get_file_name(file_path):
    return os.path.basename(file_path)
 
# 计算文件的MD5值
def get_file_md5(filename):
    m = hashlib.md5()  # 创建md5对象
    with open(filename, 'rb') as fp:
        while True:
            data = fp.read(4096)  # 每次读取4MB
            if not data:
                break
            m.update(data)  # 更新md5对象
    fp.close()
    return m.hexdigest()
 
# 获取文件大小  返回结果单位：byte字节
def get_file_size(filePath):
    fsize = os.path.getsize(filePath)
    return fsize
 
# 获取当前任务进度
def get_task_info(file_info):
    body = {'client': 'web',
            'source': '335',
            'soft_version': 'v3.0.1.1',
            'device_id': '33c5ba842f15511aa539830082a32500',
            'taskId': file_info['md5']}
    res = post(TASK_INFO, body, header)
    if res.status_code == 200:
        info = json.loads(res.text)
        print(info)
        if info['code'] == 0:
            fileTextList = info['data']['file_text']
            s = ''
            for i in fileTextList:
                s = s + i['text']
            print('音频转义之后的文字结果为：')
            print(s)
        else:
            print('延时2s轮询查询')
            time.sleep(2)
            get_task_info(file_info)
    else:
        print(res)
 
# 开始音频转语音任务
def md5_to_text(file_info):
 
    body = {'client': 'web',
            'source': '335',
            'soft_version': 'v3.0.1.1',
            'device_id': '33c5ba842f15511aa539830082a32500',
            'md5': file_info['md5'],
            'fileName': file_info['fileName'],
            'title': file_info['fileName']}
    res = post(MD5_TO_TEXT_URL, body, header)
    # 说明创建转义成文本的任务成功
    if res.status_code == 200:
        info = json.loads(res.text)
        print(info)
        # 开始查询转义的任务进度
        get_task_info(file_info)
    else:
        print(res)
 
# 删除上传的mp3音频文件任务
def delete_mp3_file(file_info):
    res = upload_operate(file_info, 'Delete')
    if res.status_code == 200:
        print('删除成功')
    else:
        print(res)
 
# 结束上传mp3音频文件任务
def stop_upload_mp3_file(file_info):
    res = upload_operate(file_info, 'End')
    if res.status_code == 200:
        info = json.loads(res.text)
        print(info)
        # 结束任务成功之后，开始做音频转文字的任务
        md5_to_text(file_info)
    else:
        print(res)
 
# 上传mp3音频文件
def upload_mp3_file(file_info):
    url = BASE_URL + '/v1/alivoice/uploadaudiofile?r=' + str(random.uniform(0, 1))
    f = open(file=file_info['filePath'], mode='rb')
    data = f.read()
    multipart_encoder = MultipartEncoder(
        fields={
            'action': (None, 'Store'),
            'pos': (None, '0'),
            'size': (None, str(file_info['size'])),
            'md5': (None, file_info['md5']),
            'file': ('blob', data, 'application/octet-stream'),
        },
        boundary=boundary
    )
 
    res = post(url, multipart_encoder, update_header)
    # 说明上传成功
    if res.status_code == 200:
        info = json.loads(res.text)
        print(info)
        # 调用结束上传任务
        stop_upload_mp3_file(file_info)
    else:
        print(res)
 
# 开始mp3音频文件任务
def start_mp3_file(file_info):
    res = upload_operate(file_info, 'Begin')
    if res.status_code == 200:
        info = json.loads(res.text)
        print(info)
        if info['pos'] >= 0:
            # 创建任务成功开始之后，开始上传音频文件
            upload_mp3_file(file_info)
        else:
            # 说明之前已上传成功过，那就直接去创建生成text的任务
            md5_to_text(file_info)
    else:
        print(res)
 
# 将mp4文件转为mp3音频文件,生成路径仍在原路径中(需要先下载moviepy库)
def mp4_to_mp3(path):
    try:
       video = VideoFileClip(path)
       audio = video.audio
       # 设置生成的mp3文件路径
       newPath = path.replace('mp4', 'mp3')
       audio.write_audiofile(newPath)
       return newPath
    except Exception as e:
        print(e)
        return None
 
 
if __name__ == '__main__':
    # 将 mp4文件路径，转成的mp3文件路径
 
    mp3FilePath = mp4_to_mp3(mp4FilePath)
    # 创建一个文件信息对象，方面后续读取音频文件信息
    file_info = {}
    file_info['md5'] = get_file_md5(mp3FilePath)  # mp3对应的md5值
    file_info['fileName'] = get_file_name(mp3FilePath)  # MP3文件的文件名称
    file_info['size'] = get_file_size(mp3FilePath)     # 文件大小
    file_info['filePath'] = mp3FilePath  # 文件路径
    # 创建上传MP3文件的任务
    start_mp3_file(file_info)
