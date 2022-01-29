# -*- coding:utf-8 -*-
from pywinauto.application import Application
from apscheduler.schedulers.blocking import BlockingScheduler
import keyboard
from Util.myLogging import *
import ctypes, sys, os, time
import psutil


def input_passwd():
    keyboard.send('enter')
    time.sleep(2)
    logger.info(u"查找app WeChatMainWndForPC")
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
    logger.info(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    logger.info(u"查找window WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    if 1: #not w.is_normal():
        logger.info(u"restore window WeChatMainWndForPC")
        w.restore()
    #w = app.top_window()
    #sys.flags.utf8_mode = True
    #w.dump_tree(filename='a.txt')
    #w.dump_tree()
    #w1 = w.child_window(title="...")
    #w1.dump_tree()
    logger.info(u"等待 window to be ready")
    w.wait('ready', timeout=timeout)
    logger.info(u"查找 搜索(Edit)")
    search_c = w.child_window(control_type='Edit', title='搜索')
    logger.info(u"等待 搜索(Edit) to be ready")
    search_c.wait('exists ready', timeout=timeout)
    #chat_list.draw_outline('red')
    search_c.click_input()
    #logger.info(u"设置焦点 搜索(Edit)")
    #search_c.set_focus()
    logger.info(u"输入 搜索(Edit)")
    search_c.type_keys(session, with_spaces=True)
    #time.sleep(1)
    #chat_list = w.child_window(control_type='List', title='会话')
    logger.info(u"查找 搜索结果(List)")
    chat_list = w.child_window(control_type='List', title='搜索结果')
    logger.info(u"等待 搜索结果(List) to be ready")
    chat_list.wait('exists ready', timeout=timeout)
    #c=chat_list.items()[2]
    logger.info(u"查找 条目: %s" % session)
    c = next(filter(lambda x: x.window_text() == session, chat_list))
    #c.wait('exists ready', timeout=timeout) # AttributeError: 'ListItemWrapper' object has no attribute 'wait'
    #c.draw_outline(colour='red')
    logger.info(u"选择 条目: %s" % session)
    c.click_input()
    #time.sleep(1)
    logger.info(u"查找 输入(Edit)")
    input_c = w.child_window(control_type='Edit', title='输入')
    logger.info(u"等待 输入(Edit) to be ready")
    input_c.wait('exists ready', timeout=timeout)
    #chat_list.draw_outline('red')
    input_c.click_input(coords=(10, 10))
    #logger.info(u"设置焦点 输入(Edit)")
    #input_c.set_focus()
    if send:
        word += '~'
    logger.info(u"输入 输入(Edit)")
    input_c.type_keys(word)

def move_up_down(steps, c):
    if steps > 0:
        for i in range(steps):
            c.send_keystrokes('{DOWN}')
    else:
        for i in range(-steps):
            c.send_keystrokes('{UP}')


def start_wechat():
    if all(map(lambda x: x.name() != 'WeChat.exe', psutil.process_iter())):
        os.system(r'E:\Program Files (x86)\Tencent\WeChat\WeChat.exe')
        time.sleep(5)


def to_send():
    stop_eurocatt()
    start_wechat()
    session = 'Tower HMI Team'
    if debug:
        session = '...'
    word = u'不发烧，不咳嗽，不生病，一切正常'
    logger.info(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    app_win32 = Application(backend='win32').connect(class_name="WeChatMainWndForPC")
    logger.info(u"查找window WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    w_win32 = app_win32.window(class_name='WeChatMainWndForPC')
    logger.info(u"restore window WeChatMainWndForPC")
    w.restore()
    logger.info(u"等待 window to be ready")
    w.wait('ready', timeout=timeout)
    chat_list = w.child_window(control_type='List', title='会话')
    logger.info(u"等待 搜索结果(List) to be ready")
    #chat_list.wait('exists ready', timeout=timeout)
    #chat_list.scroll('up', 'page', 20)
    #chat_list.wait('exists visible', timeout=timeout)
    #c=chat_list.items()[2]
    logger.info(u"查找 条目: %s" % session)
    logger.info("length of chat list: %s" % len(chat_list.items()))
    logger.info(u"查找 输入(Edit)")
    input_c = w.child_window(control_type='Edit', title='输入')
    while not input_c.has_keyboard_focus():  # 需要获取键盘焦点
        w_win32.send_keystrokes('{TAB}')
    while not list(filter(lambda x: (x.window_text() == '大情人') and x.is_selected(), chat_list.items())):
        move_up_down(-1, w_win32)
    #chat_list.wait('exists visible', timeout=timeout)
    while not list(filter(lambda x: (x.window_text() == session) and x.is_selected(), chat_list.items())):
            move_up_down(1, w_win32)
            #chat_list.wait('exists visible', timeout=timeout)
    #logger.info(u"等待 输入(Edit) to be ready")
    #input_c.wait('exists ready', timeout=timeout)
    while not input_c.has_keyboard_focus(): # 需要获取键盘焦点
        w_win32.send_keystrokes('{TAB}')
    logger.info(u"输入 输入(Edit)")
    w_win32.send_chars(word)
    w_win32.send_keystrokes('%S')
    if debug:
        input_c.click_input()


def start_todesk():
    os.system(r"C:\Users\newer\Downloads\ToDesk_Lite.exe")

def stop_process(proc):
    # 以管理员权限运行"
    cmd = "taskkill /im %s /f" % proc
    if ctypes.windll.shell32.IsUserAnAdmin():
        os.system(cmd)
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", u'cmd.exe', '/C "%s"' % cmd, None, 1)

def stop_todesk():
    stop_process('ToDesk_Lite.exe')

def stop_eurocatt():
    stop_process('EurocatT.exe')

if __name__ == "__main__":
    setup_logging()
    timeout = 10
    debug = False
    if debug:
        user32 = ctypes.windll.LoadLibrary('user32.dll')
        user32.LockWorkStation()
        time.sleep(4)
        to_send()
        exit(0)
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 600
    }
    scheduler = BlockingScheduler(job_defaults=job_defaults, timezone='Asia/Shanghai')
    scheduler.add_job(to_send, 'cron', hour=19, minute=30)
    scheduler.add_job(start_todesk, 'cron', hour=20, minute=30)
    #scheduler.add_job(stop_todesk, 'cron', day_of_week='0-4', hour=8, minute=30)
    scheduler.start()