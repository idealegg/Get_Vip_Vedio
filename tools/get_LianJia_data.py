# *-- coding: utf8 -- *
import requests
import os
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import time
from pypinyin import lazy_pinyin
import math


districts = { 'bj': [
 u'海淀',
 u'朝阳',
 u'丰台',
 u'昌平',
 u'顺义',
 u'石景山',
 u'房山',
 u'大兴',],
    'cd': [
    '锦江', '青羊', '武侯', '高新7', '成华', '金牛', '天府新区', '高新西1', '双流', '温江', '郫都', '龙泉驿', '新都',
     '天府新区南区', '青白江', '抖江堰', '彭州', '简阳', '新津', '崇州1', '大邑', '金堂', '蒲江', '邛崃']
#doujiangyan 包含 dujiangyan 和 qingchengshan
}

# https://cd.fang.lianjia.com/loupan/jinjiang-jinniu-shuangliu/bba90eba200l3l4l5l6nht1/#shuangliu
conf = {
    'ershoufang': {
        'url': 'https://%s.lianjia.com/ershoufang/%s/%s',
        'url2': 'https://%s.lianjia.com/ershoufang/%s/%spg%s/',
        'conditions': {'cd': 'mw1y2sf1l3l4l5a4a5a6a7a8', 'bj': 'mw1y2sf1l2l3a2a3a4p1p2p3'},
        'headers': [
                    u'小区', u'商圈',
                    u'总价', u'单价', u'参考价',
                    u'首付', u'等额本息月供', u'等额本金月供', u'贷款',
                    u'户型', u'大小', u'朝向', u'装修', u'楼层', u'建年', u'楼型',
                    u'标签',
                    u'标题',
                    u'发布信息',
                    'tag3', 'tag4', 'tag5', 'tag6', 'tag7',
                    u'链接',]
    },
    'loupan': {
        'url': 'https://%s.fang.lianjia.com/loupan/%s/%s/',
        'url2': 'https://%s.fang.lianjia.com/loupan/%s/%spg%s/',
        'conditions': {'cd': 'bba90eba200l3l4l5l6nht1'},
        'headers': [
            u'小区', u'类型', u'状态',
            u'总价', u'单价', u'最大总价', u'最小总价',
            u'首付', u'等额本息月供', u'等额本金月供', u'贷款',
            u'大小', u'最大面积', u'最小面积',
            u'标签',
            'tag3', 'tag4', 'tag5', 'tag6', 'tag7',
            u'户型',
            u'地址',
            u'链接', ]
    }
}
def get_price(s):
    s1 = "".join(filter(lambda x: x.isdigit() or x == '.', s))
    return float(s1) if s1 else 0.0


def analysis_ershoufang_data(sp):
    '''
    F=P*(1+i)^n
    F=A((1+i)^n-1)/i
    P=F/(1+i)^n
    P=A((1+i)^n-1)/(i(1+i)^n)
    A=Fi/((1+i)^n-1)
    A=P(i(1+i)^n)/((1+i)^n-1)
    F：终值(Future Value)，或叫未来值，即期末本利和的价值。
    P：现值(Present Value)，或叫期初金额。
    A ：年金(Annuity)，或叫等额值。
    i：利率或折现率
    N：计息期数
    p*i*((1+i) ** n/((1+i)**n-1))
    (p/n)+p*i    p/n * i
    '''
    out = []
    selllist = sp.select('.sellListContent')
    if not len(selllist):
        return out
    hs=selllist[0].select('div.clear.info')
    for h in hs:
        dt={}
        dt[u'链接']=h.contents[0].contents[0]['href']
        dt[u'标题']=h.contents[0].contents[0].text
        tags=h.contents[1].find_all('a')
        dt[u'小区']=tags[0].text
        dt[u'商圈']=tags[1].text
        h_info=h.contents[2].contents[0].text
        h_i_s = h_info.split('|')
        (dt[u'户型'], dt[u'大小'], dt[u'朝向'], dt[u'装修'],dt[u'楼层'], dt[u'建年'],dt[u'楼型'])=h_i_s
        dt[u'发布信息']=h.contents[3].text
        tags=[''] * 5
        i=0
        for ch in h.contents[4].children:
                tags[i]=ch.text
                i+=1
                if i > 4:
                    break
        for i in range(3,8):
            dt['tag%d' % i] = tags[i-3]
        dt[u'标签']=" ".join(tags)
        dt[u'总价']=h.contents[5].contents[0].text.strip()
        dt[u'单价']=h.contents[5].contents[1]['data-price']
        dt[u'参考价'] = u'否'
        if not get_price(dt[u'单价']):
            dt[u'单价'] = '%.0f' % get_price(h.contents[5].contents[1].text.strip())
            dt[u'参考价'] = u'是'
        if not get_price(dt[u'总价']):
            dt[u'总价'] = u'%.0f万' % (get_price(dt[u'单价']) * get_price(dt[u'大小']) / 10000.0)
        val = float(dt[u'总价'].replace(u'万', ''))
        dt[u'贷款']=val * 0.95 * 0.65
        dt[u'首付']=val - dt[u'贷款'] + val * 0.95 * 0.01  # 估值 0.95， 契税 1%
        i = 0.049 /12  # 标准利率 4.9%
        n = 30 * 12           # 贷款 30年
        p = dt[u'贷款']*10000
        dt[u'等额本息月供']= u"%.0f" % (p*i*((1+i) ** n/((1+i)**n-1)),)
        dt[u'等额本金月供']= u"%.0f (每年递减%.0f)" %((p/n)+p*i,  p/n * i)
        out.append(dt)
    return out   


def get_ershoufang_page_num(dis, sp):
    pg_box=sp.select('.page-box .house-lst-page-box')
    if not pg_box:
        print("error, no pg-box")
        return 0
    # [<div class="page-box house-lst-page-box" comp-module="page" page-data='{"totalPage":8,"curPage":1}' page-url="/ershoufang/fangshan/pg{page}mw1y2sf1l2l3a2a3a4p1p2p3"></div>]
    pg_data=json.loads(pg_box[0]['page-data'])
    print(pg_data)
    print("%s, Page [%s/%s]:\n" % (dis, 1, pg_data['totalPage']))
    return pg_data['totalPage']


def check_gbk_str(s):
    again = True
    while again:
        try:
            s.encode('gbk')
            again = False
        except UnicodeEncodeError as e:
            s = s.replace(e.object[e.start:e.end], '-')
    return s


def analysis_loupan_data(sp):
    '''
    s1 = u'隆基泰和•紫樾书香'.encode('gbk')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeEncodeError: 'gbk' codec can't encode character '\u2022' in position 4: illegal multibyte sequence
    :param sp:
    :return:
    '''
    out = []
    selllist = sp.select('div.resblock-desc-wrapper')
    if not len(selllist):
        return out
    for h in selllist:
        dt={}
        d_name = h.find(class_='resblock-name')
        d_link = d_name.find(class_='name')
        dt[u'链接'] = d_link['href']
        dt[u'小区'] = check_gbk_str(d_link.text.strip())
        dt[u'类型'] = d_name.find(class_='resblock-type').text.strip()
        dt[u'状态'] = d_name.find(class_='sale-status').text.strip()
        dt[u'地址'] = h.find(class_='resblock-location').text.strip()
        dt[u'户型'] = h.find(class_='resblock-room').text.strip()
        dt[u'大小'] = h.find(class_='resblock-area').text.strip()
        tags = dt[u'大小'].split('-')
        dt[u'最大面积'] = '%.0f' % get_price(tags[1]) if len(tags) > 1 else ''
        dt[u'最小面积'] = '%.0f' % get_price(tags[0]) if len(tags) else ''
        tags=[''] * 5
        i=0
        for ch in h.find(class_='resblock-tag').find_all('span'):
                tags[i]=ch.text
                i+=1
                if i > 4:
                    break
        for i in range(3,8):
            dt['tag%d' % i] = tags[i-3]
        dt[u'标签']=" ".join(tags)
        d_price = h.find(class_='resblock-price')
        dt[u'总价'] = d_price.find(class_='second')
        dt[u'总价'] = dt[u'总价'].text.strip() if dt[u'总价'] else '0'
        tags = dt[u'大小'].split('-')
        dt[u'最大总价'] = u'%.0f万' % get_price(tags[1]) if len(tags) > 1 else '0'
        dt[u'最小总价'] = u'%.0f万' % get_price(tags[0]) if len(tags) else '0'
        d_m_price = d_price.find(class_='main-price')
        dt[u'单价']=d_m_price.find(class_='number').text.strip()
        dt[u'单价描述'] = d_m_price.find(class_='desc')
        dt[u'单价描述'] = dt[u'单价描述'].text.strip() if dt[u'单价描述'] else ''
        val = (float(dt[u'最大总价'].replace(u'万', '')) + float(dt[u'最小总价'].replace(u'万', '')))/2.0
        dt[u'贷款']=val * 0.95 * 0.65
        dt[u'首付']=val - dt[u'贷款'] + val * 0.95 * 0.01  # 估值 0.95， 契税 1%
        i = 0.049 /12  # 标准利率 4.9%
        n = 30 * 12           # 贷款 30年
        p = dt[u'贷款']*10000
        dt[u'等额本息月供']= u"%.0f" % (p*i*((1+i) ** n/((1+i)**n-1)),)
        dt[u'等额本金月供']= u"%.0f (每年递减%.0f)" %((p/n)+p*i,  p/n * i)
        out.append(dt)
    return out


def get_loupan_page_num(dis, sp):
    pg_box=sp.select('.page-box')
    if not pg_box:
        print("error, no pg-box")
        return 0
    # <div class="page-box" data-current="1" data-total-count="21">
    total = math.ceil(float(pg_box[0]['data-total-count']) / 10.0)
    print("%s, Page [%s/%s]:\n" % (dis, 1, total))
    return total


def get_district_data(dis):
    dis_pinyin = "".join(lazy_pinyin(dis))
    out = {}
    url = conf[what_data]['url'] % (where_data, dis_pinyin, conf[what_data]['conditions'][where_data])
    print(url)
    req= requests.get(url)
    print(req)
    sp=bs(req.content, 'html.parser')
    total_page = eval('get_%s_page_num(dis, sp)' % what_data)
    if not total_page:
        return out
    output = []
    output.extend(eval('analysis_%s_data(sp)' % what_data))
    for pg in range(2, total_page + 1):
        url = conf[what_data]['url2'] % (where_data, dis_pinyin, conf[what_data]['conditions'][where_data], pg)
        print(url)
        print("%s, Page [%s/%s]:\n" % (dis, pg, total_page))
        req= requests.get(url)
        print(req)
        sp=bs(req.content, 'html.parser')
        output.extend(eval('analysis_%s_data(sp)' % what_data))
    print("%s, Data download ok!\n" % dis)
    out[u'区']=[]
    for h in conf[what_data]['headers']:
        out[h]=[]
    for dt in output:
        out[u'区'].append(dis)
        for h in conf[what_data]['headers']:
            out[h].append(dt[h])
    df=pd.DataFrame(out,index=range(1, len(output)+1))
    f_name = "%s_%s" % (dis, time.strftime("%y%m%d-%H%M%S", time.localtime()))
    #df.to_csv('%s_utf8.csv' % f_name, encoding='utf8', columns=[u'区'] + headers, index=False)
    df.to_csv(os.path.join(outdir, '%s_gbk.csv' % f_name), encoding='gbk', columns=[u'区'] + conf[what_data]['headers'], index=False)
    print("%s, Data save ok!\n" % dis)
    return out


def get_data():
    output = {u'区': []}
    for h in conf[what_data]['headers']:
        output[h]=[]
    for dis in districts[where_data]:
        out=get_district_data(dis)
        if out:
            for h in [u'区'] + conf[what_data]['headers']:
                output[h].extend(out[h])
    df=pd.DataFrame(output,index=range(1, len(output[u'区'])+1))
    f_name = "Total_%s_%s_%s" % (where_data, what_data, time.strftime("%y%m%d-%H%M%S", time.localtime()), )
    df.to_csv(os.path.join(outdir, '%s_gbk.csv' % f_name), encoding='gbk', columns=[u'区'] + conf[what_data]['headers'], index=False)


if __name__ == '__main__':
    outdir = r'D:\private\hd\买房\lianjia'
    #what_data = 'ershoufang'
    what_data = 'loupan'
    where_data = 'cd'
    outdir = os.path.join(outdir, what_data, where_data)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    get_data()