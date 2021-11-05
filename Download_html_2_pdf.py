# coding=utf-8
import os
import re
import time
import logging
import pdfkit
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger


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
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"
}


def parse_url_to_html(url, name):
    """
    解析URL，返回HTML内容
    :param url:解析的url
    :param name: 保存的html文件名
    :return: html
    """
    try:
        response = requests.get(url, headers=headers)
        print("%s %s" % (response, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        # 正文
        body = soup.find_all(class_="x-wiki-content")[0]
        # 标题
        title = soup.find('h4').get_text()
        # 标题加入到正文的最前面，居中显示
        center_tag = soup.new_tag("center")
        title_tag = soup.new_tag('h1')
        title_tag.string = title
        center_tag.insert(1, title_tag)
        body.insert(1, center_tag)
        imgs = soup.find_all('img')
        for img in imgs:
            if img.has_attr('data-src'):
                img['src'] = img['data-src']
                img['data-src'] = ''
        html = str(body)
        # body中的img标签的src相对路径的改成绝对路径
        pattern = r'(<img.*?[^-]\bsrc=")(.*?")'
        def func(m):
            if not m.group(2).startswith("http"):
                return m.group(1) + "http://www.liaoxuefeng.com" + m.group(2)
            else:
                return m.group(1)+m.group(2)
        html = re.compile(pattern).sub(func, html)
        html = html_template.format(content=html)
        html = html.encode("utf-8")
        with open(name, 'wb') as f:
            f.write(html)
        return name
    except Exception as e:
        logging.error("解析错误", exc_info=True)


def get_url_list(url):
    """
    获取所有URL目录列表
    :return:
    """
    #url = "https://www.liaoxuefeng.com/wiki/1016959663602400"
    response = requests.get(url,
                            headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="uk-nav uk-nav-side")[1]
    print(menu_tag)
    urls = []
    for li in menu_tag.find_all("a"):
        url = ("http://www.liaoxuefeng.com" + li.get('href'), li.text.strip())
        urls.append(url)
    return urls


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
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }
    try:
        pdfkit.from_file(htmls, file_name, options=options, configuration=confg)
    except OSError as ose:
        print(ose)


def main(iurl, file_name):
    start = time.time()
    urls = get_url_list(iurl)
    for index, url in enumerate(urls):
      parse_url_to_html(url[0], str(index) + ".html")
    htmls =[]
    pdfs =[]
    for i in range(len(urls)):
        htmls.append(str(i)+'.html')
        pdfs.append(file_name+str(i)+'.pdf')
        save_pdf(str(i)+'.html', file_name+str(i)+'.pdf')
        print (u"转换完成第"+str(i)+'个html')
    merger = PdfFileMerger()
    for i, pdf in enumerate(pdfs):
       merger.append(pdf, bookmark=urls[i][1])
       print (u"合并完成第"+str(i)+'个pdf'+pdf)
    output = open(u"%s.pdf" % file_name, "wb")
    merger.write(output)
    print (u"输出PDF成功！")
    for html in htmls:
        os.remove(html)
        print (u"删除临时文件"+html)
    for pdf in pdfs:
        try:
            os.remove(pdf)
        except Exception as e:
            print(e)
        print (u"删除临时文件"+pdf)
    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)


if __name__ == '__main__':
    #main('https://www.liaoxuefeng.com/wiki/1016959663602400', u'Python教程')
    main('https://www.liaoxuefeng.com/wiki/1252599548343744', u'Java教程')
    main('https://www.liaoxuefeng.com/wiki/1022910821149312', u'JavaScript教程')
    main('https://www.liaoxuefeng.com/wiki/896043488029600', u'Git教程')
