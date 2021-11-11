# coding=utf-8
import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader
from Util.myLogging import *


def get_url_list(html_path):
    with open(html_path, 'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        links = list(map(lambda x: (x['href'], x.text.strip()), soup.find_all('a', class_='list_item js_post')))
        if not links:
            links = list(map(lambda x: (x.find_all('a')[-1]['href'], x.find_all('a')[-1].text.strip()),
                            filter(lambda x: x.contents
                                  and x.find_all('a')
                                  and (x.find_all('a')[-1].find_all('strong') or x.find_all('a')[-1].find_parents('strong')),
                                       soup.find_all('p'))))
        logger.info(links)
    return links


def parse_url_to_html(url, name):
    try:
        response = requests.get(url)
        logger.info("%s %s" % (response, url))
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
        logger.info(ose)


def download_one(file_name):
    start = time.time()
    logger.info(file_name)
    urls = get_url_list("%s.html" % file_name)
    for index, url in enumerate(urls):
      parse_url_to_html(url[0], str(index) + ".html")
    htmls =[]
    pdfs = []
    for i, url in enumerate(urls):
        htmls.append(str(i) + '.html')
        pdfs.append(file_name+str(i)+'.pdf')
        save_pdf(str(i) + '.html', file_name+str(i)+'.pdf')
        logger.info(u"转换完成第"+str(i)+'个html')
    merger = PdfFileMerger()
    for i, pdf in enumerate(pdfs):
        with open(pdf, 'rb') as fpdf:
            merger.append(fpdf, bookmark=urls[i][1])  # 这里会占用pdf文件导致删除失败
            logger.info(u"合并完成第" + str(i) + '个pdf' + pdf)
    with open("%s.pdf" % file_name, "wb") as output:
        merger.write(output)
    logger.info(u"输出PDF成功！")
    try:
        for html in htmls:
            os.remove(html)
            logger.info(u"删除临时文件"+html)
        for pdf in pdfs:
            os.remove(pdf)
            logger.info(u"删除临时文件"+pdf)
    except Exception as es:
        logger.info(es)
    total_time = time.time() - start
    logger.info(u"总共耗时：%f 秒" % total_time)


if __name__ == '__main__':
    setup_logging()
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
