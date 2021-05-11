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
brightness = 1.5
color = 1.5
contrast = 1.5
sharpness = 2.0
sharpness_times = 1.0


def img_enhance(image):
    #亮度增强
    enh_bri = ImageEnhance.Brightness(image)
    image_brightened = enh_bri.enhance(brightness)
    #色度增强
    enh_col = ImageEnhance.Color(image_brightened)
    image_colored = enh_col.enhance(color)
    #对比度增强
    enh_con = ImageEnhance.Contrast(image_colored)
    image_contrasted = enh_con.enhance(contrast)
    # 锐度增强
    enh_sha = ImageEnhance.Sharpness(image_contrasted)
    image_sharped = enh_sha.enhance(sharpness*sharpness_times)
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
    global sharpness_times
    mp4 = mp4_inf['name']
    cmd = "avconv -i %s 2>&1|grep -e Video -e Duration" % mp4
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
        elif line.count('Video'):
            res = re.search("\s(\d+)x(\d+)\s", line)
            if res:
                old_width = int(res.group(1))
                old_height = int(res.group(2))
                print("w h: %sx%s"%(old_width, old_height))
                sharpness_times = 1280 * 720 / old_width / old_height
    while duration - endt > offset:
        index = str(offset // max_dur +1)
        slice_n = "".join([mp4.replace(".mp4", ''), '_', index, ".mp4"])
        slice_n2 = "".join([mp4.replace(".mp4", ''), '_', index, "_2", ".mp4"])
        cmd = "avconv -i %s -ss %s -t %s -s 720x1280 -vf transpose=2 -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n)
        #cmd = "avconv -i %s -ss %s -t %s -c copy -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n2)
        #cmd1 = "avconv -i %s -vf transpose=1 -y %s 2>&1" %(slice_n2, slice_n)
        #cmd2 = "rm %s" % slice_n2
        do_task([cmd])
        mp4_enhance(slice_n)
        offset += max_dur


def main(mp4s):
    for mp4 in mp4s:
        split_mp4(mp4)

if __name__ == "__main__":
    if 1:
        main([
{'name': u"【09dota超清提高班】纯爷们第一视角.mp4", 'start': 30 + max_dur * 0, 'end': 0},
        ])
    else:
        mp4_enhance("tmp.mp4")





