# -*- coding:utf-8 -*-
from pywinauto.application import Application
import time
import sys
import os
import keyboard
from pywinauto import mouse
import pyperclip
import json
import shutil
import pprint


class Yyxf:
    def __init__(self, jconf_p):
        self.jconf_p = jconf_p
        f = open(self.jconf_p, 'rb')
        self.conf = json.load(f)
        self.outdir = self.conf['outdir']
        #self.indir = self.conf['indir']
        self.main_win_class = self.conf['main_win_class']
        self.list_win_class = self.conf['list_win_class']
        self.item_class = self.conf['item_class']

    def init(self):
        self.name = ''
        print(u"查找app: %s" % self.main_win_class)
        self.app = Application(backend='uia').connect(class_name=self.main_win_class)
        print(u"查找window: %s" % self.main_win_class)
        self.w = self.app.window(class_name=self.main_win_class)
        self.w.restore()
        print(u"查找controls: %s" % self.list_win_class)
        w2s = self.w.children(class_name=self.list_win_class)
        print(u"查找control:" )
        self.w2 = w2s[1]
        print(self.w2.get_properties())
        self.w2.draw_outline('red')
        self.pos = 1
        self.rpos = self.pos
        self.items_per_page = 20
        self.rec = self.w2.rectangle()
        self.item_height = (self.rec.bottom - self.rec.top)/self.items_per_page
        self.mid = self.rec.mid_point()
        print(u"查找controls: %s" % self.conf['prop_win_title'])
        self.p2p = self.w.child_window(title=self.conf['prop_win_title'])
        print(u"查找controls: %s" % self.conf['delete_dialog_title'])
        self.df = self.w.child_window(title=self.conf['delete_dialog_title'])
        self.get_tasks()
        self.maps = {}

    def get_tasks(self):
        print(u"get_tasks")
        self.w2.click_input(coords=self.get_rpos())
        self.w2.right_click_input(coords=self.get_rpos())
        keyboard.send('up+enter')
        finish = False
        for i, ch in enumerate(self.p2p.children()):
            #print("[%s][%s][%s]" % (i, ch.window_text(), ch.friendly_class_name()))
            if ch.friendly_class_name() == "Edit":
                #print(ch.iface_value)
                self.indir = ch.iface_value.CurrentValue
            elif ch.window_text() == u'活动任务:':
                print("get it!")
                finish = True
            elif finish:
                self.tasks = int(ch.window_text())
                self.p2p.close()
                break
        print(self.indir)

    def check(self):
        self.init()
        while self.pos < self.tasks:
            mouse.move(self.get_pos())
            self.w2.click_input(coords=self.get_rpos())
            self.name = self.w2.window_text()
            self.adjust_pos_after_click()
            self.w2.right_click_input(coords=self.get_rpos())
            time.sleep(0.1)
            keyboard.send('up+enter')
            rate = self.p2p.child_window(control_type='Text', title_re='.*%').window_text()
            self.indir = self.p2p.children(control_type='Edit')[-1].iface_value.CurrentValue
            print("[%s/%s][%s][%s][%s]" % (self.pos, self.tasks, self.rpos, self.name, rate))
            self.maps[self.name] = rate
            self.p2p.close()
            if rate == '100%'or rate == '100.0%':
                self.stop_download()
                self.move_f()
                self.delete_f()
                self.pos += 1
            else:
                self.add_pos()
        pprint.pprint(self.maps)

    def add_pos(self):
        self.pos += 1
        self.rpos += 1

    def get_pos(self):
        #print(self.rec)
        #print(self.mid)
        ret = (self.mid.x, round(self.item_height * (self.rpos - 0.5) + self.rec.top))
        #print("item_height: %s" % self.item_height)
        #print("get_pos[%s][%s]pos: %s" % (self.pos, self.rpos, ret))
        return ret

    def get_rpos(self):
        #print(self.rec)
        #print(self.mid)
        ret = (self.mid.x - self.rec.left, round(self.item_height * (self.rpos - 0.5)))
        #print("item_height: %s" % self.item_height)
        #print("get_rpos[%s][%s]pos: %s" % (self.pos, self.rpos, ret))
        return ret

    def adjust_pos_after_click(self):
        if self.rpos > self.items_per_page - 2 and self.pos <= self.tasks - 1:
            self.rpos -= 2 - (self.items_per_page - self.rpos)

    def stop_download(self):
        print("stop_download")
        self.w2.right_click_input(coords=self.get_rpos())
        for i in range(3):
            keyboard.send('down')
        keyboard.send('enter')
        time.sleep(0.5)

    def move_f(self):
        print("move_f")
        #self.add_pos()
        shutil.move(os.path.join(self.indir, self.name), os.path.join(self.outdir, self.name))

    def delete_f(self):
        print("delete_f")
        self.w2.right_click_input(coords=self.get_rpos())
        for i in range(7):
            keyboard.send('up')
        keyboard.send('enter')
        cb = self.df.child_window(control_type='CheckBox')
        bt = self.df.child_window(control_type='Button', title='确定')
        cb.click()
        bt.click()
        time.sleep(1)


if __name__ == "__main__":
    timeout = 30
    yyxf = Yyxf(os.path.join('Conf', 'yyxf.json'))
    #while True:
    if 1:
        yyxf.check()
        #time.sleep(60)
