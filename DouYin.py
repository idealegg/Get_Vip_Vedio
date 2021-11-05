# -*- coding:utf-8 -*-
import requests
import json
import os
import time
import re
import string

"""
1.根据用户页面分享的字符串提取短url
2.根据短url加上302获取location,提取sec_id
3.拼接视频列表请求url
params = {
    'sec_uid' : 'MS4wLjABAAAAbtSlJK_BfUcuqyy8ypNouqEH7outUXePTYEcAIpY9rk',
    'count' : '200',
    'min_cursor' : '1612108800000',
    'max_cursor' : '1619251716404',
    'aid' : '1128',
    '_signature' : 'PtCNCgAAXljWCq93QOKsFT7QjR'
}
"""
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"
}


def get_good_name(s, to_replace=True):
    replace_char = '-'
    res = []
    for ch in s:
            if u'\u4e00' <= ch <= u'\u9fff' or ch in string.printable[:62]+'_-.':
                res.append(ch)
            elif to_replace and res and res[-1] != 'replace_char':
                res.append(replace_char)
    return ''.join(res)


def download_one(string):
    #string  = '在抖音，记录美好生活！ https://v.douyin.com/eSN7g1c/'
    #string = input('粘贴分享链接：')
    shroturl = re.findall('[a-z]+://[\S]+', string, re.I | re.M)[0]
    print(shroturl)
    startpage = requests.get(url=shroturl, headers=headers, allow_redirects=False)
    location = startpage.headers['location']
    print(location)
    sec_uid = re.findall('(?<=sec_uid=)[a-z，A-Z，0-9, _, -]+', location, re.M | re.I)[0]
    print(sec_uid)
    getname = requests.get(url='https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                           headers=headers).text
    userinfo = json.loads(getname)
    print(userinfo)
    name = userinfo['user_info']['nickname']
    name = get_good_name(name, False)
    print(name)
    outdir2 = os.path.join(outdir, name)
    if not os.path.exists(outdir2):
        os.mkdir(outdir2)
    else:
        print('directory exist')
    """new function"""
    year = (
        '2018',
        '2019',
        '2020', '2021')
    month = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
    timepool = [x + '-' + y + '-01 00:00:00' for x in year for y in month]
    print(timepool)
    k = len(timepool)
    vn = 0
    for i in range(k):
        if i < k - 1:
            print('begintime=' + timepool[i])
            print('endtime=' + timepool[i + 1])
            beginarray = time.strptime(timepool[i], "%Y-%m-%d %H:%M:%S")
            endarray = time.strptime(timepool[i + 1], "%Y-%m-%d %H:%M:%S")
            t1 = int(time.mktime(beginarray) * 1000)
            t2 = int(time.mktime(endarray) * 1000)
            print(t1, t2)
            params = {
                'sec_uid': sec_uid,
                'count': 200,
                'min_cursor': t1,
                'max_cursor': t2,
                'aid': 1128,
                '_signature': 'PtCNCgAAXljWCq93QOKsFT7QjR'
            }
            awemeurl = 'https://www.iesdouyin.com/web/api/v2/aweme/post/'
            req = requests.get(url=awemeurl, params=params, headers=headers)
            print(req)
            if req.status_code != 200:
                exit(1)
            data = json.loads(req.content)
            print(data)
            # print(type(data))
            awemenum = len(data['aweme_list'])
            print(awemenum)
            for i in range(awemenum):
                videotitle = data['aweme_list'][i]['desc'].replace("?", "").replace("\"", "").replace(":", "")
                #videotitle = re.sub('[| ;,:?()*^.]', '-', videotitle)
                videotitle = get_good_name(videotitle)
                videourl = data['aweme_list'][i]['video']['play_addr']['url_list'][0]
                print(videotitle)
                print(videourl)
                #start = time.time()
                print(b'%s ===>downloading' % videotitle.encode('utf8'))
                vn += 1
                vfile = os.path.join(outdir2, '%s_%s.mp4' % (vn, videotitle))
                if not os.path.isfile(vfile):
                    try:
                        with requests.get(url=videourl, headers=headers) as req2:
                            print(req2)
                            if req2.status_code == 200:
                                with open(vfile, 'wb') as v:
                                    v.write(req2.content)
                    except Exception as e:
                        print(e)
                        print('download error')



if __name__ == "__main__":
    outdir = r'E:\hzw\DouYin'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    #download_one("https://v.douyin.com/RhnwkwN/")
    #download_one("https://v.douyin.com/RhW2j6g/")
    #download_one("https://v.douyin.com/RhWjYvW/")
    #download_one("https://v.douyin.com/RhW1MSY/")
    #download_one("https://v.douyin.com/RhWdXaN/")
    #download_one("https://v.douyin.com/Rh7Ab8R/")
    #download_one("https://v.douyin.com/Rh765QE/")
    #download_one("https://v.douyin.com/Rh7uy2P/")
    #download_one("https://v.douyin.com/Rh74BWN/")
    #download_one("https://v.douyin.com/Rh7yvqV/")
    #download_one("https://v.douyin.com/Rh7ySdt/")
    #download_one("https://v.douyin.com/Rh7MBUW/")
    #download_one("https://v.douyin.com/Rh7jG5r/")
    #download_one("https://v.douyin.com/Rh7nAw3/")
    #download_one("https://v.douyin.com/Rh7vTt3/")
    #download_one("https://v.douyin.com/Rh7wKqU/")
    #download_one("https://v.douyin.com/Rh7GVRj/")
    #download_one("https://v.douyin.com/Rhv1pUt/")
    #download_one("https://v.douyin.com/Rh7TQQY/")
    #download_one("https://v.douyin.com/Rh7tWfR/")
    #download_one("https://v.douyin.com/Rh7GN8h/")
    #download_one("https://v.douyin.com/Rh7EGmE/")
    #download_one("https://v.douyin.com/Rh7gUvQ/")
    #download_one("https://v.douyin.com/Rh7nt9r/")
    #download_one("https://v.douyin.com/Rhvechf/")
    #download_one("https://v.douyin.com/RhvdaSW/")
    #download_one("https://v.douyin.com/Rh77Pvp/")
    #download_one("https://v.douyin.com/Rh7G7kx/")
    #download_one("https://v.douyin.com/Rh7KFcx/")
    #download_one("https://v.douyin.com/Rh7GFw8/")
    download_one("https://v.douyin.com/RBKfm4E/")
    download_one("https://v.douyin.com/RBKA3Ge/")
    download_one("https://v.douyin.com/RBK2nXK/")
    download_one("https://v.douyin.com/RBKB9B6/")
    download_one("https://v.douyin.com/RBKAGM9/")
    download_one("https://v.douyin.com/RBKCK6J/")
    download_one("https://v.douyin.com/RBK2Ltf/")
    download_one("https://v.douyin.com/RBKpvpe/")
    download_one("https://v.douyin.com/RBKVD6q/")
    download_one("https://v.douyin.com/RBKnYsM/")
    download_one("https://v.douyin.com/RBKv3xb/")
    download_one("https://v.douyin.com/RBKGYXP/")
    download_one("https://v.douyin.com/RBK7xeo/")
    download_one("https://v.douyin.com/RBKWwjp/")
    download_one("https://v.douyin.com/RBE1HVY/")
    download_one("https://v.douyin.com/RBKt2p6/")
    download_one("https://v.douyin.com/RBKvnVJ/")
    download_one("https://v.douyin.com/RBKnWhQ/")
    download_one("https://v.douyin.com/RBKWPdX/")
    download_one("https://v.douyin.com/RBKEwqM/")
    download_one("https://v.douyin.com/RBKwFHu/")
    download_one("https://v.douyin.com/RBEd9DP/")
    download_one("https://v.douyin.com/RBEdQSu/")
    download_one("https://v.douyin.com/RBEkWb5/")
    download_one("https://v.douyin.com/RBEhBSQ/")
    download_one("https://v.douyin.com/RBEhD5p/")
    download_one("https://v.douyin.com/RBE2uJA/")
    download_one("https://v.douyin.com/RBE6hBe/")
    download_one("https://v.douyin.com/RBEULcY/")
    download_one("https://v.douyin.com/RBE5UQy/")
    download_one("https://v.douyin.com/RBE8jU5/")
    download_one("https://v.douyin.com/RBEhV6q/")
    download_one("https://v.douyin.com/RBEH6Kw/")
    download_one("https://v.douyin.com/RBEaDWY/")
    download_one("https://v.douyin.com/RBEFWxj/")
    download_one("https://v.douyin.com/RBEjb9Q/")
    download_one("https://v.douyin.com/RBE8KPo/")
    download_one("https://v.douyin.com/RBENLvA/")
    download_one("https://v.douyin.com/RBESPcM/")
    download_one("https://v.douyin.com/RBEmbNf/")
    download_one("https://v.douyin.com/RBEmxL3/")
    download_one("https://v.douyin.com/RBE85aE/")
    download_one("https://v.douyin.com/RBEyuRW/")
    download_one("https://v.douyin.com/RBE4vXr/")
    download_one("https://v.douyin.com/RBE4CJj/")
    download_one("https://v.douyin.com/RBET8HL/")
    download_one("https://v.douyin.com/RBE9xXq/")
    download_one("https://v.douyin.com/RBEq3GS/")
    download_one("https://v.douyin.com/RBE4S8k/")
    download_one("https://v.douyin.com/RBEEvE8/")
    download_one("https://v.douyin.com/RBEGeek/")
    download_one("https://v.douyin.com/RBEsxgN/")
    download_one("https://v.douyin.com/RBEsF3Q/")
    download_one("https://v.douyin.com/RBEp8jK/")
    download_one("https://v.douyin.com/RBEgng4/")
    download_one("https://v.douyin.com/RBEvLK7/")
    download_one("https://v.douyin.com/RBEWW7t/")
    download_one("https://v.douyin.com/RBE4kfx/")
    download_one("https://v.douyin.com/RBE7us1/")
    download_one("https://v.douyin.com/RBEptSn/")
    download_one("https://v.douyin.com/RBEvKtY/")
    download_one("https://v.douyin.com/RBEELEf/")
    download_one("https://v.douyin.com/RBE7FXw/")