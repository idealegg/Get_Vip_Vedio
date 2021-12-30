# -*- coding:utf-8 -*-
from pywinauto.application import Application
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import keyboard
from pywinauto import mouse
import pyperclip


def input_passwd():
    keyboard.send('enter')
    time.sleep(2)
    print(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    input_c = w.child_window(control_type='Edit', title='输入')
    input_c.set_edit_text('')
    #keyboard.write('')
    keyboard.send('enter')
    time.sleep(2)

def lock_win():
    keyboard.send('alt+l')

def auto_send2(session='...', word='hi', send=False):
    print(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    print(u"查找window WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    if 1: #not w.is_normal():
        print(u"restore window WeChatMainWndForPC")
        w.restore()
    #w = app.top_window()
    #sys.flags.utf8_mode = True
    #w.dump_tree(filename='a.txt')
    #w.dump_tree()
    #w1 = w.child_window(title="...")
    #w1.dump_tree()
    print(u"等待 window to be ready")
    w.wait('ready', timeout=timeout)
    print(u"查找 搜索(Edit)")
    search_c = w.child_window(control_type='Edit', title='搜索')
    print(u"等待 搜索(Edit) to be ready")
    search_c.wait('exists ready', timeout=timeout)
    #chat_list.draw_outline('red')
    search_c.click_input()
    #print(u"设置焦点 搜索(Edit)")
    #search_c.set_focus()
    print(u"输入 搜索(Edit)")
    search_c.type_keys(session, with_spaces=True)
    #time.sleep(1)
    #chat_list = w.child_window(control_type='List', title='会话')
    print(u"查找 搜索结果(List)")
    chat_list = w.child_window(control_type='List', title='搜索结果')
    print(u"等待 搜索结果(List) to be ready")
    chat_list.wait('exists ready', timeout=timeout)
    #c=chat_list.items()[2]
    print(u"查找 条目: %s" % session)
    c = next(filter(lambda x: x.window_text() == session, chat_list))
    #c.wait('exists ready', timeout=timeout) # AttributeError: 'ListItemWrapper' object has no attribute 'wait'
    #c.draw_outline(colour='red')
    print(u"选择 条目: %s" % session)
    c.click_input()
    #time.sleep(1)
    print(u"查找 输入(Edit)")
    input_c = w.child_window(control_type='Edit', title='输入')
    print(u"等待 输入(Edit) to be ready")
    input_c.wait('exists ready', timeout=timeout)
    #chat_list.draw_outline('red')
    input_c.click_input(coords=(10, 10))
    #print(u"设置焦点 输入(Edit)")
    #input_c.set_focus()
    if send:
        word += '~'
    print(u"输入 输入(Edit)")
    input_c.type_keys(word)

def move_up_down(steps, c):
    if steps > 0:
        for i in range(steps):
            c.send_keystrokes('{DOWN}')
    else:
        for i in range(-steps):
            c.send_keystrokes('{UP}')


def to_send():
    session = 'Tower HMI Team'
    if debug:
        session = '...'
    word = u'不发烧，不咳嗽，不生病，一切正常'
    print(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    app_win32 = Application(backend='win32').connect(class_name="WeChatMainWndForPC")
    print(u"查找window WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    w_win32 = app_win32.window(class_name='WeChatMainWndForPC')
    print(u"restore window WeChatMainWndForPC")
    if not w.is_normal():
        w.restore()
    print(u"等待 window to be ready")
    w.wait('ready', timeout=timeout)
    chat_list = w.child_window(control_type='List', title='会话')
    print(u"等待 搜索结果(List) to be ready")
    #chat_list.wait('exists ready', timeout=timeout)
    #chat_list.scroll('up', 'page', 20)
    chat_list.wait('exists visible', timeout=timeout)
    #c=chat_list.items()[2]
    print(u"查找 条目: %s" % session)
    print("length of chat list: %s" % len(chat_list.items()))
    move_up_down(-200, w_win32)
    #chat_list.wait('exists visible', timeout=timeout)
    while not list(filter(lambda x: (x.window_text() == session) and x.is_selected(), chat_list.items())):
            move_up_down(1, w_win32)
            #chat_list.wait('exists visible', timeout=timeout)
    print(u"查找 输入(Edit)")
    input_c = w.child_window(control_type='Edit', title='输入')
    print(u"等待 输入(Edit) to be ready")
    input_c.wait('exists ready', timeout=timeout)
    while not input_c.has_keyboard_focus(): # 需要获取键盘焦点
        w_win32.send_keystrokes('{TAB}')
    print(u"输入 输入(Edit)")
    w_win32.send_chars(word)
    w_win32.send_keystrokes('%S')
    if debug:
        input_c.click_input()


if __name__ == "__main__":
    timeout = 10
    debug = False
    #to_send()
    scheduler = BlockingScheduler()
    scheduler.add_job(to_send, 'cron', hour=20, minute=0, second=0)
    scheduler.start()