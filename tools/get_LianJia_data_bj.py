# *-- coding: utf8 -- *
import requests
import os
import sys
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import numpy as np
import time


districts = {
'haidian' : u'海淀',
'chaoyang' : u'朝阳',
'fengtai' : u'丰台',
'changping' : u'昌平',
'shunyi' : u'顺义',
'shijingshan' : u'石景山',
'fangshan' : u'房山',
'daxing' : u'大兴',
}

headers=[
         u'小区', u'商圈', 
         u'总价', 
         u'首付', u'等额本息月供', u'等额本金月供',
         u'单价', 
         u'户型', u'大小', u'朝向', u'装修',u'楼层', u'建年',u'楼型', 
         u'标签',
         u'贷款', 
#         'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 
         u'标题', 
#         u'链接', 
         u'发布信息',
         ]
         
         
def analysis_data(sp):
    hs=sp.select('div.clear.info')
    out=[]
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
        dt[u'总价']=h.contents[5].contents[0].text
        dt[u'单价']=h.contents[5].contents[1]['data-price']
        val = int(dt[u'总价'][:3])
        dt[u'贷款']=val * 0.95 * 0.65
        dt[u'首付']=val - dt[u'贷款'] + val * 0.95 * 0.01  # 估值 0.95， 契税 1%
        i = 0.049 /12  # 标准利率 4.9%
        n = 30 * 12           # 贷款 30年
        p = dt[u'贷款']*10000
        dt[u'等额本息月供']= "%.2f" % (p*i*((1+i) ** n/((1+i)**n-1)),)
        dt[u'等额本金月供']= u"%.2f (每年递减%.2f)" %((p/n)+p*i,  p/n * i)
        out.append(dt)
        
    return out   
    
    
def get_district_data(dis):
    url = 'https://bj.lianjia.com/ershoufang/%s/mw1y2sf1l2l3a2a3a4p1p2p3/' % dis
    req= requests.get(url)
    sp=bs(req.content, 'html.parser')

    pg_box=sp.select('.page-box .house-lst-page-box')
    if not pg_box:
        print("error, no pg-box")
        exit(1)
    # [<div class="page-box house-lst-page-box" comp-module="page" page-data='{"totalPage":8,"curPage":1}' page-url="/ershoufang/fangshan/pg{page}mw1y2sf1l2l3a2a3a4p1p2p3"></div>]

    pg_data=json.loads(pg_box[0]['page-data'])
    output=[]
    print("%s, Page [%s/%s]:\n" % (dis, 1, pg_data['totalPage']))
    output.extend(analysis_data(sp))

    for pg in range(2, pg_data['totalPage'] + 1):
        url = 'https://bj.lianjia.com/ershoufang/%s/pg%dmw1y2sf1l2l3a2a3a4p1p2p3/' % (dis, pg)
        print("%s, Page [%s/%s]:\n" % (dis, pg, pg_data['totalPage']))
        req= requests.get(url)
        sp=bs(req.content, 'html.parser')
        output.extend(analysis_data(sp))
        
    print("%s, Data download ok!\n" % dis)

    out={}
    out[u'区']=[]
    for h in headers:
        out[h]=[]
        
    for dt in output:
        out[u'区'].append(districts[dis])
        for h in headers:
            out[h].append(dt[h])
            
            
    df=pd.DataFrame(out,index=range(1, len(output)+1))
    f_name = "%s_%s" % (dis, time.strftime("%y%m%d-%H%M%S", time.localtime()))
    #df.to_csv('%s_utf8.csv' % f_name, encoding='utf8', columns=[u'区'] + headers, index=False)
    df.to_csv('%s_gbk.csv' % f_name, encoding='gbk', columns=[u'区'] + headers, index=False)

    print("%s, Data save ok!\n" % dis)
    return out


if __name__ == "__main__":
    output = {}
    output[u'区']=[]
    for h in headers:
        output[h]=[]
    for dis in districts.keys():
        out=get_district_data(dis)
        for h in [u'区'] + headers:
            output[h].extend(out[h])
    df=pd.DataFrame(output,index=range(1, len(output[u'区'])+1))
    f_name = "Total_%s" % (time.strftime("%y%m%d-%H%M%S", time.localtime()), )
    df.to_csv('%s_gbk.csv' % f_name, encoding='gbk', columns=[u'区'] + headers, index=False)
        
#F=P*(1+i)^n
#
#F=A((1+i)^n-1)/i
#
#P=F/(1+i)^n
#
#P=A((1+i)^n-1)/(i(1+i)^n)
#
#A=Fi/((1+i)^n-1)
#
#A=P(i(1+i)^n)/((1+i)^n-1)
#
#F：终值(Future Value)，或叫未来值，即期末本利和的价值。
#
#P：现值(Present Value)，或叫期初金额。
#
#A ：年金(Annuity)，或叫等额值。
#
#i：利率或折现率
#
#N：计息期数


#p*i*((1+i) ** n/((1+i)**n-1))

#(p/n)+p*i    p/n * i