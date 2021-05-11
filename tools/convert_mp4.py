#!*---coding:utf8--*
import cv2
from PIL import ImageEnhance, Image
import sys
import numpy as np
import time
import os
import shutil
import re


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
        cmd = "avconv -i %s -ss %s -t %s -vf transpose=2 -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n)
        #cmd = "avconv -i %s -ss %s -t %s -c copy -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n2)
        #cmd1 = "avconv -i %s -vf transpose=1 -y %s 2>&1" %(slice_n2, slice_n)
        #cmd2 = "rm %s" % slice_n2
        do_task([cmd])
        offset += max_dur

def img_enhance(image):
    # 锐度增强
    enh_sha = ImageEnhance.Sharpness(image)
    sharpness = 3.0
    image_sharped = enh_sha.enhance(sharpness)
    # image_sharped.show()
    return image_sharped

def mp4_enhance(mp4):
    start_time = time.time()
    cap = cv2.VideoCapture(mp4)
    slice_n = mp4.replace(".mp4", "_eh.mp4")
    aac = mp4.replace(".mp4", ".aac")
    encoder = 'mp4v'
    fourcc = cv2.VideoWriter_fourcc(*encoder) #“DIVX"、”MJPG"、“XVID”、“X264", 'm', 'p', '4', 'v'
    fps = 25
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    videoWriter = cv2.VideoWriter(slice_n, fourcc, fps, (video_width, video_height))
    num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("[%s]Num of frame: [%s]" % (mp4, num))
    i=0
    while(cap.isOpened()):
        #print("\r[%s/%s]" % (i, num), end='')
        i+=1
        ret, frame = cap.read()  # 读出来的frame是ndarray类型
        if ret:
            image = Image.fromarray(np.uint8(frame))  # 转换成PIL可以处理的格式
            image_enhanced = img_enhance(image)  # 调用编写的画质增强函数
            frame = np.asarray(image_enhanced)
            videoWriter.write(frame)
        else:
            break
    cap.release()
    videoWriter.release()
    end_time = time.time()
    print("enhance time: %.2f"%(end_time - start_time))
    os.system('avconv -i %s -c copy -y %s' % (mp4, aac))
    os.system('avconv -i %s -i %s -c copy -y %s' % (slice_n, aac, mp4))
    os.system('rm %s' % slice_n)
    os.system('rm %s' % aac)


def main(mp4s):
    for mp4 in mp4s:
        split_mp4(mp4)

if __name__ == "__main__":
    if 0:
        main([
        #{'name': u"09dota提高班网通1房拆黑小骷髅第一视角.mp4", 'start': 26, 'end': 0},
        #{'name': u"09dota提高班召唤师卡尔的华丽舞步.mp4", 'start': 38, 'end': 0},
        #{'name': u"【09dota提高班】顶着延迟加卡的蝴蝶小强.mp4", 'start': 38 + max_dur *0, 'end': 0},
        #{'name': u"【09dota提高班】速成输出王黑鸟.mp4", 'start': 10 + max_dur * 2, 'end': 35},
        #{'name': u"【09dota提高班】蚂蚁-新版本Carry英雄.mp4", 'start': 38 + max_dur * 0, 'end': 0},
        #{'name': u"【09dota提高班】WE新人的犀利狗和09的稳重狗.mp4", 'start': 38 + max_dur * 4, 'end': 44},
        # {'name': u"【09dota提高班】多变的收割机痛苦女王.mp4", 'start': 0 + max_dur * 0, 'end': 90},
        # {'name': u"【09dota提高班】54分钟42杀的痛苦女王.mp4", 'start': 0 + max_dur * 0, 'end': 12},
        # {'name': u"【09dota超清提高班】帅气敌法篇.mp4", 'start': 22 + max_dur * 0, 'end': 30},
        # {'name': u"【09dota提高班】死灵龙一样打C.mp4", 'start': 22 + max_dur * 0, 'end': 167},
         # {'name': u"【09dota超清提高班】蝙蝠骑士的妖娆火焰.mp4", 'start': 22 + max_dur * 0, 'end': 0},
         # {'name': u"【09dota提高班】VIPER的单杀是一种信仰.mp4", 'start': 82 + max_dur * 0, 'end': 70},
         {'name': u"【09dota超清提高班】暴力火卡.mp4", 'start': 22 + max_dur * 0, 'end': 0},
         {'name': u"【09dota超清提高班】恶魔巫师.mp4", 'start': 32 + max_dur * 0, 'end': 0},
        ])
    else:
        for i in range(1, 10):
            mp4_enhance("【09dota超清提高班】恶魔巫师_%s.mp4"% i)




