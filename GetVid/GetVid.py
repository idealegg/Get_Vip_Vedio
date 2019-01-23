#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import pprint
import time
from selenium.webdriver.common.by import By
import traceback
import chardet


executable_path = 'phantomjs-2.1.1-windows\\bin\\phantomjs.exe'


def init_driver():
  global executable_path
  '''
  ***selenium 自动操作网页***
  #设置设备代理
  '''
  dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
  dcap["phantomjs.page.settings.userAgent"] = (
  #"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"
  )
  return webdriver.PhantomJS(executable_path=executable_path,
                             service_args=['--load-images=false',
                                           '--disk-cache=true'],
                             desired_capabilities=dcap)  # 加载网址
  #options = webdriver.ChromeOptions()
  #options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"')
  #return webdriver.Chrome(chrome_options=options)


def putUrl(driver, url):
  driver.set_window_size(1124, 850)
  driver.get(url)    #此处填写文章地址


def GetSen(driver, info):
  t_info = {}
  sens2 = driver.find_elements_by_class_name('op-zx-new-tvideo-vlink')
  for sen2 in sens2:
    key = sen2.text
    if key.find("\n") != -1:
      key = key[:key.find("\n")]
    t_info[key] = sen2.get_attribute('href')
  pprint.pprint(t_info)
  info.update(t_info)
  return info


def allchecked(checked):
  for ch in checked:
    if not checked[ch]:
      return False
  return True

def nochecked1(checked, driver):
  text = ""
  elem = None
  for ch in checked:
    if not checked[ch]:
      text = ch
  print "nochecked1: ch: [%s]\n" % ch
  for sen in driver.find_elements(By.XPATH, "//div[@class='op-zx-new-tvideo-juhe-link OP_LOG_OTHERS']"):
    print "nochecked1: sen: [%s]\n" % sen.text
    if sen.text == text:
      elem = sen
  print "nochecked1: elem: [%s]\n" % elem.text
  elem.click()
  time.sleep(1.0)
  return elem


def GetSens():
  sen_info_path = "sens_info.txt"
  info={}
  if os.path.exists(sen_info_path):
    fd = open(sen_info_path, "rb")
    for line in fd:
      line.strip().strip()
      if line:
        print chardet.detect(line)
        line2 = line.decode('utf-8')
        fields = line2.split(" ")
        info[fields[0]] = fields[1].strip()
    fd.close()
    return info
  try:
    url = 'https://www.baidu.com/s?wd=%E6%B5%B7%E8%B4%BC%E7%8E%8B&rsv_spt=1&rsv_iqid=0xbffec5ef00005e64&issp=1&f=3&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&oq=python%2520get%25E8%25AF%25B7%25E6%25B1%2582%25E5%25B8%25A6%25E5%258F%2582%25E6%2595%25B0&rsv_t=28a94GR7HpLTzNrPlxmkECd%2FH7%2FxLVUT%2Fl7nNZg2lvXyLYGYmSm%2FWmgmJU%2BHYzdTE192&inputT=5673&rsv_pq=c94fc4ed00034890&rsv_sug3=21&rsv_sug1=22&rsv_sug7=101&rsv_sug2=1&prefixsug=ha&rsp=0&rsv_sug4=7286'
    driver = init_driver()
    putUrl(driver, url)
    plus_open = driver.find_element_by_class_name('op-zx-new-tvideo-more')
    print "Would click:"
    print plus_open.text
    plus_open.click()
    time.sleep(1.0)
    sens = driver.find_elements(By.XPATH,"//div[@class='op-zx-new-tvideo-juhe-link OP_LOG_OTHERS']")
    opened = driver.find_element(By.XPATH,"//div[@class='op-zx-new-tvideo-juhe-link op-zx-new-tvideo-juhe-cur-link OP_LOG_OTHERS']")
    checked = {}
    for i in range(len(sens)):
      print "No opened [%d]: %s\n" % (i, sens[i].text)
      print sens[i].text
      checked[sens[i].text] = False
    print "opened: %s\n" %opened.text
    checked[opened.text] = True
    info = GetSen(driver, info)
    while not allchecked(checked):
      elem = nochecked1(checked, driver)
      checked[elem.text] = True
      info = GetSen(driver, info)
    driver.close()
    pprint.pprint(info)
    fd=open(sen_info_path, "wb")
    keys = info.keys()
    pprint.pprint(keys)
    keys.sort(cmp=lambda x, y: cmp(int(x[:-1], 10), int(y[:-1], 10)))
    for sen in keys:
      fd.write("%s %s\n" %(sen.encode('utf8'), info[sen].encode('utf8')))
    fd.close()
    return info
  except Exception, e:
    driver.quit()
    traceback.print_exc()
    os.unlink(sen_info_path)
    raise
  finally:
    driver.quit()#
  #os.system("pause")

if __name__ == "__main__":
  executable_path = '..\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'
  #if len(sys.argv) != 2:
  #  print "Usage: %s <url>\n" % os.path.basename(sys.argv[0])
  #  exit(1)
  GetSens()