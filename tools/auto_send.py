# -*- coding:utf-8 -*-
from pywinauto.application import Application
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import sys


def auto_send(session='...', word='hi', send=False):
    print(u"查找app WeChatMainWndForPC")
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    print(u"查找window WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    if not w.is_normal():
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

def do_work():
    auto_send('Tower HMI Team', u'不发烧，不咳嗽，不生病，一切正常', True)


if __name__ == "__main__":
    timeout = 30
    #auto_send('Tower HMI Team', u'不发烧，不咳嗽，不生病，一切正常')
    scheduler = BlockingScheduler()
    scheduler.add_job(do_work, 'cron', hour=20, minute=30)
    scheduler.start()