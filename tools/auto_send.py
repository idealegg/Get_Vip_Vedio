from pywinauto.application import Application
import time
from apscheduler.schedulers.blocking import BlockingScheduler


def auto_send(session='...', word='hi', send=False):
    app = Application(backend='uia').connect(class_name="WeChatMainWndForPC")
    w = app.window(class_name='WeChatMainWndForPC')
    #w1 = w.child_window(title="...")
    #w1.dump_tree()
    search_c = w.child_window(control_type='Edit', title='搜索')
    #chat_list.draw_outline('red')
    search_c.click_input()
    search_c.type_keys(session, with_spaces=True)
    #time.sleep(1)
    #chat_list = w.child_window(control_type='List', title='会话')
    chat_list = w.child_window(control_type='List', title='搜索结果')
    #c=chat_list.items()[2]
    c = next(filter(lambda x: x.window_text() == session, chat_list))
    #c.draw_outline(colour='red')
    c.click_input()
    #time.sleep(1)
    input_c = w.child_window(control_type='Edit', title='输入')
    #chat_list.draw_outline('red')
    input_c.click_input()
    if send:
        word += '~'
    input_c.type_keys(word)

def do_work():
    auto_send('Tower HMI Team', u'不发烧，不咳嗽，不生病，一切正常', True)


if __name__ == "__main__":
    #auto_send('Tower HMI Team', u'不发烧，不咳嗽，不生病，一切正常')
    scheduler = BlockingScheduler()
    scheduler.add_job(do_work, 'cron', hour=20, minute=30)
    scheduler.start()