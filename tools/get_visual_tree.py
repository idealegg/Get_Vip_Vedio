# -*- coding:utf-8 -*-
from pywinauto.application import Application
from pywinauto import uia_defines
import os
import time
import keyboard
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
import traceback


def dfs_showdir(path, depth=0):
    if depth == 0:
        print("root:[" + path + "]")

    for item in os.listdir(path):
        if '.git' not in item:
            print("|      " * depth + "|--" + item)

            newitem = path + '/' + item
            if os.path.isdir(newitem):
                dfs_showdir(newitem, depth + 1)

def expand_action(c):
    c.expand()
    while not c.is_expanded():
        time.sleep(0.1)

def iter_win2(tree, depth=0):
    outs.append("|  " * depth + "|--" + tree.window_text())
    state = tree.get_expand_state()
    if state == uia_defines.expand_state_collapsed:
        expand_action(tree)
    elif state == uia_defines.expand_state_leaf_node:
        return
    cs = tree.children(class_name='TreeViewItem')
    for c in cs:
        iter_win2(c, depth + 1)


def iter_win(tree, depth=0, parent=None):
    print(tree.window_text())
    tree.select()
    textblocks = tree.children(class_name="TextBlock")
    if (len(textblocks)):
        text = textblocks[0].window_text()
    else:
        text = tree.window_text()
    outs.append("|  " * depth + "|--" + text)
    #widget_item = QTreeWidgetItem(parent)
    #widget_item.setText(0, text)
    cs = tree.children(class_name='TreeViewItem')
    for c in cs:
        #iter_win(c, depth + 1, widget_item)
        iter_win(c, depth + 1, parent)


def get_visual_tree(parent=None, v=None):
    pname = "EurocatT (正在运行) - Microsoft Visual Studio"
    print(u"查找app %s" % pname )
    app = Application(backend='uia').connect(title=pname)
    w = app.top_window()
    print(u"restore window %s" % pname)
    w.maximize()
    print(u"等待 window to be ready")
    w.wait('ready', timeout=timeout)
    print(u"查找 live_visual_tree")
    live_visual_tree = w.child_window(class_name="GenericPane", title='Live Visual Tree')
    #print(u"等待 live_visual_tree to be ready")
    #live_visual_tree.wait('exists ready', timeout=timeout)
    print(u"查找 TreeView")
    tree = live_visual_tree.child_window(class_name='TreeView')
    #print(u"等待 TreeView to be ready")
    #tree.wait('exists ready', timeout=timeout)
    wins = tree.children(class_name='TreeViewItem')
    for win in wins[::-1]:
        win.right_click_input()
        keyboard.send('up+enter')
        time.sleep(0.5)
    print(u"等待 TreeView to be ready")
    tree.wait('exists ready', timeout=timeout)
    print(u"iter TreeView")
    if parent is not None:
        wins = tree.children(class_name='TreeViewItem', title_re='.*%s.*' % parent)
    for win in wins:
        print(win)
        iter_win(win, parent=v)
    #tree.dump_tree(filename=outfile)


if __name__ == "__main__":
    if 0:
        timeout = 10
        outs = []
        #outfile = r'D:\123.txt'
        try:
            #get_visual_tree(v=t)
            get_visual_tree()
        except:
            traceback.print_exc()
        f = open(r'D:\1234.txt', 'wb')
        f.write('\n'.join(outs).encode('utf8'))
        f.close()
        #qd.show()
        #ret = app.exec_()
        #sys.exit(ret)
    else:
        app = QApplication()
        qd = QDialog(None)
        t = QTreeWidget(None)
        t.setColumnCount(1)
        t.setColumnWidth(0, 800)
        t.setHeaderLabels(['name[Type]'])
        layout = QVBoxLayout()
        layout.addWidget(t)
        qd.setLayout(layout)
        qd.setWindowTitle('Visual Tree')
        qd.resize(1200, 800)
        t.clear()
        with open(r'D:\1234.txt', 'rb') as f:
            ps = [t]
            d = -1
            for l in f:
                l = l.decode('utf8').strip()
                c = l.count('|  ')
                for i in range(d - c + 1):
                    ps.pop()
                d = c
                w = QTreeWidgetItem(ps[-1])
                w.setText(0, l[3 * (c + 1):])
                ps.append(w)
                w.setExpanded(True)
        qd.show()
        ret = app.exec_()
        sys.exit(ret)
