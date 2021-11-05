# coding=utf-8
import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader


def get_url_list(html_path):
    """
    获取所有URL目录列表
    :return:
    """
    with open(html_path, 'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        links = list(map(lambda x: (x['href'], x.text.strip()), soup.find_all('a', class_='list_item js_post')))
        if not links:
            links = list(map(lambda x: (x.find_all('a')[-1]['href'], x.find_all('a')[-1].text.strip()),
                            filter(lambda x: x.contents
                                  and x.find_all('a')
                                  and (x.find_all('a')[-1].find_all('strong') or x.find_all('a')[-1].find_parents('strong')),
                                       soup.find_all('p'))))
        print(links)
    return links


def parse_url_to_html(url, name):
    """
    解析URL，返回HTML内容
    :param url:解析的url
    :param name: 保存的html文件名
    :return: html
    """
    try:
        response = requests.get(url)
        print("%s %s" % (response, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs = soup.find_all('img')
        for img in imgs:
            if img.has_attr('data-src'):
                img['src'] = img['data-src']
                img['data-src'] = ''
            if img.has_attr('src') and not img['src'].startswith("http"):
                img['src'] = "https://mp.weixin.qq.com" + img['src']
        html = soup.prettify(encoding='utf8')
        with open(name, 'wb') as f:
            f.write(html)
        return name
    except Exception as e:
        logging.error("解析错误", exc_info=True)


def save_pdf(htmls, file_name):
    """
    把所有html文件保存到pdf文件
    :param htmls:  html文件列表
    :param file_name: pdf文件名
    :return:
    """
    confg = pdfkit.configuration(wkhtmltopdf=r'E:\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'enable-local-file-access': None,
        'enable-javascript': None,
        'javascript-delay': 1000,
        'no-stop-slow-scripts': None
    }
    try:
        pdfkit.from_file(htmls, file_name, options=options, configuration=confg)
    except OSError as ose:
        print(ose)


def download_one(file_name):
    start = time.time()
    print(file_name)
    urls = get_url_list("%s.html" % file_name)
    for index, url in enumerate(urls):
      parse_url_to_html(url[0], str(index) + ".html")
    htmls =[]
    pdfs = []
    for i, url in enumerate(urls):
        htmls.append(str(i) + '.html')
        pdfs.append(file_name+str(i)+'.pdf')
        save_pdf(str(i) + '.html', file_name+str(i)+'.pdf')
        print (u"转换完成第"+str(i)+'个html')
    merger = PdfFileMerger()
    for i, pdf in enumerate(pdfs):
       merger.append(pdf, bookmark=urls[i][1])
       print (u"合并完成第"+str(i)+'个pdf'+pdf)
    with open("%s.pdf" % file_name, "wb") as output:
        merger.write(output)
    print (u"输出PDF成功！")
    try:
        for html in htmls:
            os.remove(html)
            print (u"删除临时文件"+html)
        for pdf in pdfs:
            os.remove(pdf)
            print (u"删除临时文件"+pdf)
    except Exception as es:
        print(es)
    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)


if __name__ == '__main__':
    menus = (
        #u'秦并天下',
        #u'楚汉双雄',
        u'强汉开疆',
        u'光武中兴',
        u'三国争霸',
        u'两晋悲歌',
    )
    for menu in menus:
        download_one(menu)
