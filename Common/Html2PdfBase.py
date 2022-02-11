# coding=utf-8
import re
import threading
import traceback
import chardet
import time
import pdfkit
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from PyPDF2 import PdfFileReader, PdfFileWriter
import psutil
from Util.myLogging import *


class Html2PdfBase(threading.Thread):
    default_conf = {
        'base_dir': r'C:\store',
        'check_downloaded_retry': 3,
        'session_number': 4,
        'threading_num': 8,
        'wait_session_sleep_time': 0.5,
        'sen_field_name': ['sen', 'name', 'url', 'src_type'],
        # 'sen_info_path': os.path.join(conf_dir, 'sens_info.txt'),
        'headers': {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"},
        'request_timeout': 10.0,
        'request_retry': 10,
        'skip_request_error': False,
        'download_timeout': 60.0,
        'append_url_before': True,
        'src_type': 'file',
        'remove_pdf': True,
        'remove_html': True,
        'concat_from_right': False,
        'html_encoding': None,
        'save_encoding': 'utf-8',
        'cookies': {},
        'wk_exe': r'E:\wkhtmltopdf\bin\wkhtmltopdf.exe',
        'wk_options': {
                        'enable-local-file-access': None,
                        'enable-javascript': None,
                        'javascript-delay': 1000,
                        'no-stop-slow-scripts': None,
                        'load-error-handling': 'ignore',
                        'dpi': 600,
                        'image-dpi': 1200,
                    }
    }
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
    conf = default_conf
    base_dir = ''
    sen_list = []
    sen_no = 0
    done_file_list = []
    sen_lock = threading.Lock()
    merge_lock = threading.Lock()
    base_sen_id = 0
    rename_lock = threading.Lock()
    update_task_lock = threading.Lock()

    def __init__(self, conf=default_conf):
        super(Html2PdfBase, self).__init__()
        self._stop_event = threading.Event()
        self.class_name = self.__class__.__name__.lower()
        self.conf['sen_info_path'] = os.path.join(conf_dir, 'sens_info_%s.txt' % self.class_name)
        Html2PdfBase.conf.update(conf)
        Html2PdfBase.base_dir = os.path.join(self.conf['base_dir'], self.class_name)
        self.sen = None
        self.info = None
        self.sessions = []
        self.session_used = []
        self.session_lock = threading.Lock()
        self.task_lock = threading.Lock()
        self.thread_list = []
        self.task_list = []
        self.total_task_num = 0
        self.cur_task_num = 0
        self.headers = {}
        self.headers.update(self.conf['headers'])
        self.cookies = {}
        self.cookies.update(self.conf['cookies'])
        for k in self.cookies:
            self.cookies[k] = self.cookies[k].encode('utf-8').decode('latin-1')
        self.req_session = requests.Session()
        self.soup = None

    def replace_body(self, soup):
        return soup, True

    def format_header(self, soup):
        try:
            body = soup.find('body')
        except:
            body = soup
        return BeautifulSoup(Html2PdfBase.html_template.format(content=str(body)),
                             'html.parser',
                             from_encoding=self.conf['html_encoding'])

    def format_html(self, content):
        soup = BeautifulSoup(content, 'html.parser', from_encoding=self.conf['html_encoding'])
        soup, found = self.replace_body(soup)
        logger.info("replace body: %s" % found)
        if found:
            soup = self.format_header(soup)
            imgs = soup.find_all('img')
            for img in imgs:
                if img.has_attr('data-src'):
                    img['src'] = img['data-src']
                    img['data-src'] = ''
                if img.has_attr('src') and not img['src'].startswith("http"):
                    img['src'] = Html2PdfBase.concat_url(self.info['url'], img['src'])
        return soup.prettify(self.conf['save_encoding']) if found else None

    def find_menu_container(self, s):
        return s

    def find_all_hrefs(self, container):
        return container.find_all('a')

    def get_page_title(self, item):
        return item.text.strip()

    def get_url_list(self, f):
        url = self.info['url']
        if os.path.isfile(url):
            with open(url, 'rb') as furl:
                soup = BeautifulSoup(furl, "html.parser")
        else:
            response = requests.get(url, headers=self.headers)
            logger.info(response)
            if response.status_code != 200:
                return
            soup = BeautifulSoup(response.content, "html.parser")
        menu_tag = self.find_menu_container(soup)
        logger.info(menu_tag)
        urls = {}
        for i, item in enumerate(self.find_all_hrefs(menu_tag)):
            level = 0
            it = item
            while it and it.parent != menu_tag:
                level += 1
                it = it.parent
            text = self.get_page_title(item)
            fname = "%s_%s.pdf" % (self.sen, i)
            url = None
            if item.has_attr('href'):
                url = item.get('href')
            elif item.has_attr('data-link'):
                url = item.get('data-link')
                text = item.get('data-title')
            if url and not url.startswith('http') and self.conf['append_url_before'] and 'url' in self.info and self.info['url']:
                url = Html2PdfBase.concat_url(self.info['url'], url)
            urls[fname] = {
                  'url': url,
                  'level': level,
                  'label': text,
                  'index': i,
                  'file': fname,
                  }
            logger.info("%*d %s" % (level, level, item))
        with open(f, 'w') as jf:
            json.dump(urls, jf)

    def save_pdf(self, task):
        logger.info(task)
        confg = pdfkit.configuration(wkhtmltopdf=self.conf['wk_exe'])
        options = self.conf['wk_options']
        try:
            src_type = ('src_type' in self.info and self.info['src_type']) or self.conf['src_type']
            if src_type == 'file':
                pdfkit.from_file(os.path.join(self.base_dir, task['file'].replace('.pdf', '.html')),
                                 os.path.join(self.base_dir, task['file']),
                                 options=options,
                                 configuration=confg)
            else:
                pdfkit.from_url(task['url'],
                                os.path.join(self.base_dir, task['file']),
                                options=options,
                                configuration=confg)
        except OSError as ose:
            logger.info(ose)

    def merge_pdfs(self):
        output = PdfFileWriter()
        opdfs = []
        begin_page = 0
        parents = []
        to_add_labels = []
        tasks = self.get_all_task()
        keys = list(tasks.keys())
        keys = self.sorted(keys)
        for i, f in enumerate(keys):
            if tasks[f]['url'] is not None:
                opdfs.append(open(os.path.join(self.base_dir, f), 'rb'))
                opdf = PdfFileReader(opdfs[-1])
                for p in range(opdf.getNumPages()):
                    output.addPage(opdf.getPage(p))
                while len(to_add_labels):
                    to_add_label = to_add_labels.pop(0)
                    while len(parents) and to_add_label[1] <= parents[-1][1]:
                        parents.pop()
                    parents.append((output.addBookmark(to_add_label[0], begin_page, parents[-1][0] if len(parents) else None),
                                    to_add_label[1]))
                while len(parents) and tasks[f]['level'] <= parents[-1][1]:
                    parents.pop()
                parents.append(
                    (output.addBookmark(tasks[f]['label'], begin_page, parents[-1][0] if len(parents) else None), tasks[f]['level']))
                begin_page = output.getNumPages()
            else:
                to_add_labels.append((tasks[f]['label'], tasks[f]['level']))
            #logger.info(u"合并完成第"+str(i)+'个pdf'+f)
        outpdf = open(os.path.join(self.base_dir, u'%s.pdf' % self.info['name']), 'wb')
        output.write(outpdf)
        outpdf.close()
        logger.info(u"输出PDF成功！")
        list(map(lambda x: x.close(), opdfs))

    def sorted(self, iters):
        iters.sort(key=lambda x: int(x[x.rfind('_') + 1:x.rfind('.')], 10))
        return iters

    def init_session(self):
        self.sessions = []
        self.session_used = []
        for i in range(self.conf['session_number']):
            self.sessions.append(requests.Session())
            self.session_used.append(False)

    def close_session(self):
        if self.sessions:
            for session in self.sessions:
                session.close()
            self.session_used = [False] * len(self.session_used)
        self.sessions = []
        self.session_used = []

    def get_a_session(self):
        ret = None
        while not ret:
            self.session_lock.acquire()
            t1 = list(filter(lambda x: not x, self.session_used))
            if t1:
                i = self.session_used.index(t1[0])
                self.session_used[i] = True
                ret = self.sessions[i]
            self.session_lock.release()
            if not ret:
                time.sleep(self.conf['wait_session_sleep_time'])
            else:
                return ret

    def release_a_session(self, s):
        self.session_lock.acquire()
        i = self.sessions.index(s)
        self.session_used[i] = False
        self.session_lock.release()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_task(self):
        ret = (0, '')
        self.task_lock.acquire()
        if self.task_list:
            ret = self.task_list.pop(0)
            self.cur_task_num = len(self.task_list)
        self.task_lock.release()
        return ret

    def before_do_task(self):
        pass

    def before_start_download(self):
        pass

    def before_download_file(self):
        pass

    def after_download_file(self):
        pass

    def do_task(self):
        fd = None
        session = None
        url = ''
        i = 0
        try:
            self.before_do_task()
            logger.info("before get_task")
            i, task = self.get_task()
            logger.info("after get_task [%s] %s" % (i, task))
            while task:
                self.before_download_file()
                url = task['url']
                start_time = time.time()
                if url:
                    f_size = 0
                    logger.info("%s [%d] [%d/%d]: %s\n" % (self.sen, i, self.cur_task_num, self.total_task_num, url))
                    if self.conf['src_type'] == 'file':
                        session = self.get_a_session()
                        req2 = session.get(url=url,
                                            headers=self.headers if self.headers else None,
                                            timeout=self.conf['download_timeout'],
                                            cookies=self.cookies if self.cookies else None)
                        logger.info("%s [%d]:\n\treq: [%s]\n\tencoding: %s\n\theader: %s\n" % (
                        self.sen, i, req2, req2.encoding, req2.headers))
                        if req2.status_code == 200:
                            if 'key' in self.info and self.info['key']:
                                cryptor = AES.new(self.info['key'], AES.MODE_CBC, self.info['key'])
                                f_content = cryptor.decrypt(req2.content)
                            else:
                                f_content = req2.content
                            self.release_a_session(session)
                            f_size = len(f_content)
                            # logger.info(req.content)
                            f_content = self.format_html(f_content)
                            if f_content:
                                f_path = os.path.join(self.base_dir, "%s_%d.html" % (self.sen, i))
                                fd = open(f_path, "wb" if self.conf['save_encoding'] else 'w')
                                #fd = open(f_path, "wb")
                                fd.write(f_content)
                                fd.close()
                                fd = None
                            else:
                                self.update_task_info_url(task)
                        else:
                            self.release_a_session(session)
                            self.update_task_info_url(task)
                    self.save_pdf(task)
                    end_time = time.time()
                    logger.info(
                        "%s [%d] [%d/%d]:\n\tfile: %s\n\tstart: %s\n\tend: %s\n\tused: %.3f\n\tsize: %.3f kb\n\trate: %.3f kb/s\n" % (
                            self.sen,
                            i,
                            self.cur_task_num,
                            self.total_task_num,
                            task['file'],
                            time.ctime(start_time),
                            time.ctime(end_time),
                            end_time - start_time,
                            f_size / 1000.0,
                            f_size / (end_time - start_time) / 1000.0))
                self.after_download_file()
                i, task = self.get_task()
        except:
            logger.info("Exception in getAFile: %s [%d]: %s\n" % (self.sen, i, url))
            traceback.print_exc()
            if fd:
                fd.close()
            if session:
                self.release_a_session(session)

    @classmethod
    def get_base_sen_id(cls):
        if cls.base_sen_id != 0:
            cls.base_sen_id += 1
            logger.info("base_sen_id: %d" % cls.base_sen_id)
            return cls.base_sen_id
        for f in cls.done_file_list:
            f = "%s_." % f
            i = min(f.find("_"), f.find("."))
            id = 0
            try:
                id = int(f[:i])
            except:
                id = 0
            if id > cls.base_sen_id:
                cls.base_sen_id = id
        cls.base_sen_id += 1
        logger.info("base_sen_id: %d" % cls.base_sen_id)
        return cls.base_sen_id

    @classmethod
    def parse_sen_from_line(cls, line):
        line = line.strip()
        if line and not line.startswith(b'#'):
            logger.info(chardet.detect(line))
            line2 = line.decode('utf-8')
            fields = re.split("\s+", line2)
            info = {}
            for field_name in cls.conf['sen_field_name']:
                info[field_name] = fields.pop(0) if fields else ''
            if 'sen' in cls.conf['sen_field_name']:
                cls.sen_list.append((info['sen'], info))
            else:
                cls.sen_list.append((cls.get_base_sen_id(), info))

    @classmethod
    def gen_sens(cls):
        cls.sen_lock.acquire()
        if not cls.sen_list:
            if os.path.exists(cls.conf['sen_info_path']):
                fd = open(cls.conf['sen_info_path'], "rb")
                for line in fd:
                    cls.parse_sen_from_line(line)
                fd.close()
        cls.sen_lock.release()
        logger.info("sens: %s\n" % cls.sen_list)

    @classmethod
    def is_sen_exist(cls):
        cls.gen_sens()
        return len(cls.sen_list)

    @classmethod
    def get_a_sen(cls):
        ret = (None, None)
        cls.sen_lock.acquire()
        if cls.sen_list and cls.sen_no < len(cls.sen_list):
            cls.sen_no += 1
            ret = cls.sen_list[cls.sen_no - 1]
        cls.sen_lock.release()
        logger.info("get_a_sen: %s\n" % list(ret))
        return ret

    def gen_sen_json(self):
        pass

    @classmethod
    def concat_url(cls, url, path):
        if cls.conf['concat_from_right']:
            #logger.info("concat_from_right")
            prefix = url[:url.rfind('/')]
        else:
            #logger.info("concat_from_left")
            prefix = url[:url.find('/', len('https://'))]
        if not path.startswith('/'):
            return "%s/%s" % (prefix, path)
        else:
            return "%s%s" % (prefix, path)

    def get_all_task(self):
        f = os.path.join(self.base_dir, '%s.json' % self.sen)
        if not os.path.isfile(f):
            self.get_url_list(f)
        jf = open(f, 'r')
        s = jf.read()
        if not s.strip():
            jf.close()
            self.get_url_list(f)
            jf = open(f, 'r')
            s = jf.read()
        jf.close()
        return json.loads(s)

    def update_task_info(self, j):
        f = os.path.join(self.base_dir, '%s.json' % self.sen)
        jf = open(f, 'w')
        json.dump(j, jf)
        jf.close()

    def update_task_info_url(self, task):
        Html2PdfBase.update_task_lock.acquire()
        j = self.get_all_task()
        j[task['file']]['url'] = None
        self.update_task_info(j)
        Html2PdfBase.update_task_lock.release()

    def get_not_download(self):
        j = self.get_all_task()
        f_list = set(os.listdir(self.base_dir))
        keys = list(filter(lambda x: x not in f_list, j))
        keys.sort(key=lambda x: int(x[x.find('_')+1:x.rfind('.')]))
        self.task_list = []
        for f in keys:
            self.task_list.append((j[f]['index'], j[f]))
        self.total_task_num = len(self.task_list)
        self.cur_task_num = len(self.task_list)
        logger.info("get_not_download: [%s]" % self.task_list)

    def start_download(self):
        for i in range(self.conf['threading_num']):
            th = threading.Thread(target=self.do_task)
            self.thread_list.append(th)
            th.start()
        for th in self.thread_list:
            th.join()

    def check_dir(self):
        if not os.path.isdir(self.base_dir):
            os.mkdir(self.base_dir)

    @classmethod
    def get_exist_file(cls):
        if cls.done_file_list:
            return
        cls.done_file_list = os.listdir(cls.base_dir)
        logger.info(cls.base_dir)
        logger.info(cls.done_file_list)

    def run(self):
        start_t = time.time()
        req = None
        self.check_dir()
        self.get_exist_file()
        Html2PdfBase.gen_sens()
        while not self.stopped():
            try:
                self.sen, self.info = Html2PdfBase.get_a_sen()
                logger.info("[%s] %s" % (self.sen, self.info))
                if self.sen:
                    merge_again = False
                    f_list = []
                    self.headers = {}
                    self.headers.update(self.conf['headers'])
                    self.init_session()
                    dst_file = os.path.join(self.base_dir, "%s.pdf" % self.info['name'])
                    if not os.path.isfile(dst_file):
                        self.get_not_download()
                        retry = self.conf['check_downloaded_retry']
                        if not self.task_list:
                            logger.info("All pdf file of [%s] downloaded! So not download again!" % self.sen)
                        else:
                            while self.task_list and retry > 0:
                                logger.info("len: %d" % len(self.task_list))
                                logger.info("tasks: %s" % self.task_list)
                                self.before_start_download()
                                self.start_download()
                                self.get_not_download()
                                retry -= 1
                            merge_again = True
                    else:
                        logger.info("file %s.pdf exist! So not download again!" % self.info['name'])
                    f_n = 0
                    for file in os.listdir(self.base_dir):
                        if file.endswith('.pdf') and file.startswith("%s_" % self.sen):
                            f_n += 1
                            f_list.append(os.path.join(self.base_dir, file))
                    self.sorted(f_list)
                    if merge_again or not os.path.isfile(dst_file):
                        Html2PdfBase.merge_lock.acquire()
                        self.merge_pdfs()
                        Html2PdfBase.merge_lock.release()
                    else:
                        logger.info("file %s.pdf exist! So not merge again!" % self.info['name'])
                    self.close_session()
                    if self.conf['remove_html']:
                        for t_f in f_list:
                            t_h = t_f.replace('.pdf', '.html')
                            if os.path.isfile(t_h):
                                os.unlink(t_h)
                    if self.conf['remove_pdf']:
                        for t_f in f_list:
                            if os.path.isfile(t_f):
                                os.unlink(t_f)
                else:
                    logger.info('%s is leisure!' % self.getName())
                    self.close_session()
                    self.stop()
                    time.sleep(1)
            except:
                self.stop()
                logger.info("Exception in getSens.run\n")
                if req:
                    req.close()
                self.close_session()
                traceback.print_exc()
                break
        self.close_session()
        total_time = time.time() - start_t
        logger.info(u"总共耗时：%f 秒" % total_time)
        logger.info("getSens.run thread %s end!" % self.getName())


if __name__ == "__main__":
  setup_logging()
  th = Html2PdfBase(conf={'base_dir': r'C:\store',
                         'check_downloaded_retry': 2,
                         'wait_session_sleep_time': 0.1,
                         'src_type': 'file',
                         'sen_info_path': os.path.join(conf_dir, 'sens_info_html2pdf.txt'),
                         })
  th.start()
  th.join()

