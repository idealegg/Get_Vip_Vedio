# -*- coding:utf-8 -*-
from pywinauto.application import Application
import pywinauto
from apscheduler.schedulers.blocking import BlockingScheduler
import pyautogui
import keyboard
from Util.myLogging import *
import ctypes, sys, os, time
import psutil
import pyperclip
import json


default_conf ={"only_dir": True,
               "only_file": False,
               "base_dir": r"F:\Wechat\WeChat Files\wxid_7xianm6x0wvl21\FileStorage\Image",
               "conf_dir": os.path.join("Conf", "upload_baidu_yun.json"),
               "drag_time": 200,
               "interval_time": 100,
               "completed_targets": [],
               "max_file_limit": 500,
               "split_file_count": 495,
               "des_pos": [729, 529]}
default_conf["title"] = os.path.basename(default_conf['base_dir'])
timeout = 10

class UploadBaiduYun:
    class_name = "CabinetWClass"
    class_name2 = "DuiHostWnd"
    title2 = "欢迎使用百度网盘"

    def __init__(self,  conf=default_conf):
        self.conf = conf
        self.title = self.conf['title']
        self.base_dir = self.conf['base_dir']
        self.only_dir = self.conf['only_dir']
        self.only_file = self.conf['only_file']
        self.conf_dir = self.conf['conf_dir']
        self.only_dir = self.conf['base_dir']
        self.targets = os.listdir(self.base_dir)
        if self.only_dir:
            self.targets = list(filter(lambda x: os.path.isdir(x), self.targets))
        if self.only_file:
            self.targets = list(filter(lambda x: os.path.isfile(x), self.targets))
        if self.conf["completed_targets"]:
            self.targets = list(filter(lambda x: x in self.conf["completed_targets"], self.targets))
        self.completed_targets = self.conf["completed_targets"]
        self.cur_item = None
        self.cur_target = None
        self.chat_list = None
        self.chat_list2 = None
        self.f_count = 0
        self.app = None
        self.app_win32 = None
        self.w = None
        self.w_win32 = None
        self.app2 = None
        self.app_win322 = None
        self.w2 = None
        self.w_win322 = None

    def scroll_to_start_item(self):
        while self.cur_target in self.completed_targets:
            #self.w_win32.send_keystrokes('{DOWN}')
            self.cur_item.select()
            keyboard.send('down')
            self.cur_item = list(filter(lambda x: x.is_selected(), self.chat_list.items()))[0]
            self.cur_target = self.cur_item.window_text()

    def need_split(self):
        cur_dir_path = os.path.join(self.base_dir, self.cur_target)
        self.f_count = os.listdir(cur_dir_path)
        return self.f_count >= self.conf["max_file_limit"]

    def new_baidu_yun_dir(self):
        self.w_win322.restore()
        #self.w2.click_input()
        pyautogui.moveTo(self.conf['des_pos'][0], self.conf['des_pos'][1])
        self.w2.right_click_input()
        self.w_win322.send_keystrokes('{DOWN}')
        self.w_win322.send_keystrokes('{DOWN}')
        self.w_win322.send_keystrokes('{ENTER}')
        #time.sleep(self.conf["interval_time"]/1000.0)
        self.w_win322.restore()
        time.sleep(5)
        logger.info(u"send_chars: %s" % self.cur_target)
        #self.w_win322.send_chars(self.cur_target)
        #self.w_win322.send_chars("123")
        pyperclip.copy(self.cur_target)
        #pyperclip.paste()
        self.w_win322.send_keystrokes('^V')
        logger.info(u"sleep 5s")
        time.sleep(5)
        self.w_win322.send_keystrokes('{ENTER}')
        time.sleep(self.conf["interval_time"]/1000.0)
        self.w_win322.send_keystrokes('{ENTER}')

    def process_split(self):
        self.new_baidu_yun_dir()
        self.w_win32.send_keystrokes('{ENTER}')
        time.sleep(self.conf["interval_time"])
        self.chat_list2 = self.w.child_window(control_type='List', title='项目视图')
        cur_item = self.chat_list2.items()[0]
        cur_item.click_input()
        while self.f_count > 0 :
            for i in range(self.conf["split_file_count"] - 1):
                self.w_win32.send_keystrokes('{RIGHT}')
            keyboard.press('shift')
            cur_item = list(filter(lambda x: x.is_selected(), self.chat_list2.items()))[0]
            cur_item.click_input()
            keyboard.release('shift')
            cur_pos = cur_item.rectangle().mid_point()
            pyautogui.dragTo(cur_pos.x, cur_pos.y, self.conf["drag_time"]/1000.0, button='left')
            self.w_win32.send_keystrokes('{RIGHT}')
            cur_item = list(filter(lambda x: x.is_selected(), self.chat_list2.items()))[0]
            cur_item.click_input()
            self.f_count -= self.conf["split_file_count"]


    def upload_one_dir(self):
        if self.cur_target in self.completed_targets:
            return
        cur_pos = self.cur_item.rectangle().mid_point()
        logger.info("to move %s" % self.cur_target)
        pyautogui.moveTo(cur_pos.x, cur_pos.y, self.conf["drag_time"] / 1000.0 / 4.0)
        #time.sleep(self.conf["interval_time"]/1000.0)
        logger.info("to drag %s" % self.cur_target)
        pyautogui.dragTo(self.conf['des_pos'][0], self.conf['des_pos'][1], self.conf["drag_time"] / 1000.0, button='left')
        time.sleep(self.conf["interval_time"]/1000.0 )
        self.completed_targets.append(self.cur_target)

    def move_to_next(self):
        self.w.restore()
        #self.w_win32.send_keystrokes('{DOWN}')
        self.cur_item.select()
        keyboard.send('down')
        self.cur_item = list(filter(lambda x: x.is_selected(), self.chat_list.items()))[0]
        self.cur_target = self.cur_item.window_text()
        self.cur_item.click_input()

    def init_dir_window(self):
        logger.info(u"查找app WeChatMainWndForPC")
        self.app = Application(backend='uia').connect(class_name=UploadBaiduYun.class_name, title=self.title)
        self.app_win32 = Application(backend='win32').connect(class_name=UploadBaiduYun.class_name, title=self.title)
        logger.info(u"查找window %s" % UploadBaiduYun.class_name)
        self.w = self.app.window(class_name=UploadBaiduYun.class_name)
        self.w_win32 = self.app_win32.window(class_name=UploadBaiduYun.class_name)
        logger.info(u"restore window %s" % UploadBaiduYun.class_name)
        self.w.restore()
        logger.info(u"等待 window to be ready")
        self.w.wait('ready', timeout=timeout)
        self.chat_list = self.w.child_window(control_type='List', title='项目视图')
        logger.info(u"等待 项目视图(List) to be ready")
        logger.info("length of chat list: %s" % len(self.chat_list.items()))
        logger.info(u"查找 输入(Edit)")
        self.cur_item = self.chat_list.items()[0]
        self.cur_target = self.cur_item.window_text()
        self.cur_item.click_input()

    def init_baidu_yun_window(self):
        #self.app2 = Application(backend='uia').connect(class_name=UploadBaiduYun.class_name2, title=UploadBaiduYun.title2)
        self.app2 = Application(backend='uia').connect(path=r'E:\BaiduNetdisk\BaiduNetdisk.exe')
        #self.app_win322 = Application(backend='win32').connect(class_name=UploadBaiduYun.class_name2, title=UploadBaiduYun.title2)
        self.app_win322 = Application(backend='win32').connect(path=r'E:\BaiduNetdisk\BaiduNetdisk.exe')
        logger.info(u"查找window %s" % UploadBaiduYun.class_name2)
        self.w2 = self.app2.window(class_name=UploadBaiduYun.class_name2, title=UploadBaiduYun.title2)
        self.w_win322 = self.app_win322.window(class_name=UploadBaiduYun.class_name2, title=UploadBaiduYun.title2)

    def to_upload(self):
        self.scroll_to_start_item()
        while True:
            self.upload_one_dir()
            self.move_to_next()


def check_dir():
    import  hashlib
    import shutil
    if 0:
        for d in [x for x in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir,x))]:
            md5s = set()
            for fp in [x for x in os.listdir(os.path.join(base_dir, d)) if x.endswith('.mp4') or x.endswith('.jpg')]:
                with open(os.path.join(base_dir, d, fp), 'rb') as fd:
                    md5s.add(hashlib.md5(fd.read()).hexdigest())
            with open(os.path.join(base_dir, d, 'md5s'), 'w') as fd:
                json.dump(list(md5s), fd)
    if 1:
        for d in [x for x in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir,x))]:
            fs = os.listdir(os.path.join(base_dir, d))
            if len(fs) >= 500:
                d2 = 2
                while len(fs) > 495:
                    d2_name = "%s_split_%s" % (d, d2)
                    os.mkdir(os.path.join(base_dir, d2_name))
                    for f in fs[-495:]:
                        shutil.move(os.path.join(base_dir, d, f), os.path.join(base_dir, d2_name))
                    fs = fs[:-495]
                    d2 += 1

def get_completed():
    '''
abc=null
null
$('body > div.nd-main-layout > div.nd-main-layout__wrapper > div.nd-main-layout__body > div > div.wp-s-core-pan.is-default-skin > div > div.wp-s-core-pan__body.is-show-header > div.wp-s-core-pan__body-contain.is-show-detail.is-has-detail > div.wp-s-core-pan__body-contain--list.is-show-nav > div > div > div > div.wp-s-pan-table__body.mouse-choose-list > table > tbody:nth-child(2)').find('.wp-s-pan-list__file-name-title-text').each(function(){abc += '"'+$(this).attr('title')+'", ';})
console.log(abc)

$('#layoutMain > div.KPDwCE > div.zJMtAEb > div > div').find('a.pl8dae').each(function(){abc += '"'+$(this).attr('title')+'", ';})
    :return:
    '''

if __name__ == "__main__":
    if 0:
        base_dir = default_conf['base_dir']
        check_dir()
    if 1:
        try:
            setup_logging()
            uby = UploadBaiduYun()
            uby.init_dir_window()
            #uby.scroll_to_start_item()
            #uby.init_baidu_yun_window()
            #uby.new_baidu_yun_dir()
            uby.to_upload()
        except:
            logger.exception("Exit to upload for error!")
        finally:
            print('"%s"' % '", "'.join(uby.completed_targets))
            logger.info('"%s"' % '", "'.join(uby.completed_targets))
            #user32 = ctypes.windll.LoadLibrary('user32.dll')
            #user32.LockWorkStation()