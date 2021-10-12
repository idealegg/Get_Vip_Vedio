#!*---coding:utf8--*
import cv2
from PIL import ImageEnhance, Image, ImageDraw, ImageFont
import sys
import numpy as np
import time
import os
import shutil
import re


max_dur = 14 * 60
brightness = 1.4
color = 1.4
contrast = 1.4
sharpness = 2.0
sharpness_times = 1.0

num2chn = {
1   : '一',
2   : '二',
3   : '三',
4   : '四',
5   : '五',
6   : '六',
7   : '七',
8   : '八',
9   : '九',
10  : '十',
}


def img_enhance(image):
    #亮度增强
    #enh_bri = ImageEnhance.Brightness(image)
    #image_brightened = enh_bri.enhance(brightness)
    #色度增强
    enh_col = ImageEnhance.Color(image)
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
    #encoder = 'X264'
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


def draw_text(txt, width=930, height=100):
    out='out.png'
    #ttf=r'C:\Windows\Fonts\simhei.ttf' # 黑体
    ttf=r'C:\Windows\Fonts\STXINGKA.TTF' # 行楷
    fillColor = "#ffc416" 
    font_size = height -4
    leng = 0
    for ch in txt:
        leng += 0.5 if ch.isascii() else 1
    if int(leng) < leng:
        leng = int(leng) + 1
    if width//font_size < leng:
        font_size = width // leng
    setFont = ImageFont.truetype(ttf, font_size)
    #生成大小为400x400RGBA是四通道图像，RGB表示R，G，B三通道，A表示Alpha的色彩空間
    image = Image.new(mode='RGBA', size=(width, height), color=(255, 255, 255, 0))
    # ImageDraw.Draw 简单平面绘图
    draw = ImageDraw.Draw(im=image)
    draw.text((2,2),txt,font=setFont,fill=fillColor,direction=None) # direction -文字的方向。它可以是'rtl'（从右到左），'ltr'（从左到右）或'ttb'（从上到下）。需要libraqm。
    image.save(out)


def add_slide(mp4, text):
    slice_n = mp4.replace(".mp4", "_slide.mp4")
    draw_text(text)
    os.system('avconv -i %s -vf transpose=1 -y %s' % ('out.png', 'out1.png'))
    os.system('avconv -i %s -vf "movie=out1.png[watermark];[in][watermark] overlay=620:0[out] " -y %s' % (mp4, slice_n))
    os.system('rm %s %s %s'%(mp4, 'out.png', 'out1.png'))
    os.system('mv %s %s' %(slice_n, mp4))

def add_profile(mp4):
    slice_n = mp4.replace(".mp4", "_profile.mp4")
    os.system('avconv -i %s -vf "movie=2009_2.png[watermark];[in][watermark] overlay=540:780[out] " -y %s' % (mp4, slice_n))
    os.system('rm %s'%mp4)
    os.system('mv %s %s' %(slice_n, mp4))

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
                sharpness_times = 930 * 620 / old_width / old_height
    while duration - endt > offset:
        index = str(offset // max_dur +1)
        slice_n = "".join([mp4.replace(".mp4", ''), '_', index, ".mp4"])
        slice_n2 = "".join([mp4.replace(".mp4", ''), '_', index, "_2", ".mp4"])
        cmd = "avconv -i %s -ss %s -t %s -vf \"scale=930:620,pad=930:720:0:100:black,transpose=1\" -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n)
        #cmd = "avconv -i %s -ss %s -t %s -c copy -y %s 2>&1" %(mp4, get_offset(offset), max_dur if ((duration - endt) > (offset + max_dur)) else int(duration - endt -offset), slice_n2)
        #cmd1 = "avconv -i %s -vf transpose=1 -y %s 2>&1" %(slice_n2, slice_n)
        #cmd2 = "rm %s" % slice_n2
        do_task([cmd])
        mp4_enhance(slice_n)
        slice_title = "%s（%s）"%(mp4_inf['title'], num2chn[int(index)])
        add_slide(slice_n, slice_title)
        offset += max_dur


def main(mp4s):
    for mp4 in mp4s:
        split_mp4(mp4)

if __name__ == "__main__":
    if 1:
        main([    
                 # {'name': u"【09dota第一视角】宙斯兽王屠夫.mp4", 'start': 90 + max_dur * 0, 'end': 0},
         {'name': u"【09dota提高班】复仇之魂.mp4", 'start': 30 + max_dur * 0, 'end': 0, 'title': '09提高班 复仇之魂'},
         ])
    else:
        #add_slide("【09dota超清提高班】纯爷们第一视角_1.mp4", '09提高班 半人马酋长（一）')
        #draw_text("09提高班 半人马酋长（一）")
        for i in range(3, 4):
            add_profile("【09dota超清提高班】纯爷们第一视角_%s_slide.mp4"%i)
        #mp4_enhance('1.mp4')





