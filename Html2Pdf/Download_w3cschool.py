# coding=utf-8
import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader, PdfFileWriter
import psutil


# wkhtmltopdf --enable-local-file-access -B 30 -T 30 --footer-html footer.html --footer-right [page] --header-html header.html --footer-spacing 10 --header-spacing 10 cover https://www.baidu.com toc --toc-header-text "目录" --disable-dotted-lines --toc-text-size-shrink 1 xxxx.html xxxx.pdf
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"Host": "www.w3cschool.cn",
"Pragma": "no-cache",
"sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "none",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",}


def parse_url_to_html(url, name, prefix):
    try:
        response = requests.get(url)
        print("%s %s" % (response, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.find(class_="main-container font0")
        body = soup.find('body')
        body.contents = container
        imgs = soup.find_all('img')
        for img in imgs:
            if img.has_attr('data-src'):
                img['src'] = img['data-src']
                img['data-src'] = ''
            if img.has_attr('src') and not img['src'].startswith("http"):
                img['src'] = prefix + img['src']
        html = soup.prettify(encoding='utf8')
        with open(name, 'wb') as f:
            f.write(html)
        return name
    except Exception as e:
        logging.error("解析错误", exc_info=True)


def get_url_list(url, prefix):
    """
    获取所有URL目录列表
    :return:
    """
    #url = "https://www.liaoxuefeng.com/wiki/1016959663602400"
    response = requests.get(url,
                            headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="dd-list")[0]
    print(menu_tag)
    urls = []
    for li in menu_tag.find_all('a'):
        level = 0
        it = li
        while it.parent != menu_tag:
            level += 1
            it = it.parent
        if li.has_attr('href'):
            url = (prefix + li.get('href'), li.text.strip(), level)
        else:
            url = (None, li.text.strip(), level)
        urls.append(url)
        print("%*d %s" % (level, level, li))
    return urls


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
        print(ose)


def save_pdf2(htmls, file_name):
    print(htmls)
    confg = pdfkit.configuration(wkhtmltopdf=r'E:\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'enable-local-file-access': None,
        'enable-javascript': None,
        'javascript-delay': 1000,
        'no-stop-slow-scripts': None,
        'load-error-handling': 'ignore',
        'dpi': 600,
        'image-dpi': 1200,
    }
    try:
        pdfkit.from_url(htmls, file_name, options=options, configuration=confg)
    except OSError as ose:
        print(ose)


def main(iurl, file_name, prefix):
    start = time.time()
    urls = get_url_list(iurl, prefix)
    for i in range(len(urls)):
        if urls[i][0] is not None:
            save_pdf2(urls[i][0], file_name + str(i) + '.pdf')
            print (u"转换完成第"+str(i)+'个html')
    output = PdfFileWriter()
    opdfs = []
    begin_page = 0
    parents = []
    to_add_labels = []
    for i in range(len(urls)):
        pdf = file_name+str(i)+'.pdf'
        if urls[i][0] is not None:
            opdfs.append(open(pdf, 'rb'))
            opdf = PdfFileReader(opdfs[-1])
            for p in range(opdf.getNumPages()):
                output.addPage(opdf.getPage(p))
            while len(to_add_labels):
                to_add_label = to_add_labels.pop(0)
                while len(parents) and to_add_label[1] <= parents[-1][1]:
                    parents.pop()
                parents.append((output.addBookmark(to_add_label[0], begin_page, parents[-1][0] if len(parents) else None),
                                to_add_label[1]))
            while len(parents) and urls[i][2] <= parents[-1][1]:
                parents.pop()
            parents.append(
                (output.addBookmark(urls[i][1], begin_page, parents[-1][0] if len(parents) else None), urls[i][2]))
            begin_page = output.getNumPages()
        else:
            to_add_labels.append((urls[i][1], urls[i][2]))
        print (u"合并完成第"+str(i)+'个pdf'+pdf)
    outpdf = open(u'%s.pdf' % file_name, 'wb')
    output.write(outpdf)
    outpdf.close()
    for f in opdfs:
        f.close()
        os.unlink(f.name)
    print (u"输出PDF成功！")
    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)


if __name__ == '__main__':
    #main('https://www.liaoxuefeng.com/wiki/1016959663602400', u'Python教程')
    #main('https://www.w3cschool.cn/android/', u'Android教程', u'https://www.w3cschool.cn')
    #main('https://www.w3cschool.cn/uawnhh/', u'Android基础入门教程', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/android_sdk/', u'Android SDK 上手指南', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/android_training_course/', u'Android官方培训课程中文版', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/lyxftz/', u'Android 开发最佳实践', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/android_evolution/', u'解析 Android 架构设计原则', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/pbqxiq/', u'Android最佳实践', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/csharp/', u'C# 教程', u'https://www.w3cschool.cn')
    main('https://www.w3cschool.cn/wkcsharp/', u'C# 入门手册', u'https://www.w3cschool.cn')
    #main('https://www.liaoxuefeng.com/wiki/1022910821149312', u'JavaScript教程')
    #main('https://www.liaoxuefeng.com/wiki/896043488029600', u'Git教程')
