# coding=utf-8
import requests
import json
import pprint


headers = {
"Accept": "application/json, text/javascript, */*; q=0.01",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cache-Control": "no-cache",
"Connection": "keep-alive",
"Content-Type": "application/json",
"Cookie": "_atl_bitbucket_remember_me=YTQxNWE5Y2I5Yjk0NmNjY2M2YzNhNzIwZjQ4ZDE0NDJkYjg1MGQ4NzoyMTYwYTU4YjQ3MjgyNmI5YjA4YmRkNjU4OWJjZDk2MDk4NjExZjAy; BITBUCKETSESSIONID=36C5BD072043EFC30E5BF443BFAF079D",
"Host": "172.17.118.204:7990",
"Pragma": "no-cache",
"Referer": "http://172.17.118.204:7990/projects/TTWSRC/repos/fdp/pull-requests/69/diff",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
"X-AUSERID": "502",
"X-AUSERNAME": "HuangD",
"X-Requested-With": "XMLHttpRequest",
}

params = {
"contextLines": "10000",
"since": "2de3a145c8df1640ea94e4e9dbdca8b7f51c67d1",
"whitespace": "show",
"withComments": "false",
}

params2 = {
"avatarSize": "48",
"markup": "true",
"limit": "1000",
"start": "0",
}
#url = 'http://172.17.118.204:7990/rest/api/latest/projects/TTWSRC/repos/fdp/pull-requests/69/changes'
#url2 = 'http://172.17.118.204:7990/rest/api/latest/projects/TTWSRC/repos/fdp/commits/6a9c1860c77746ea37252b2d72b2bc5b1db835b8/diff/TowerBUSINESS/src/com/thales/tower/business/realization/StandMsgManager.java'
'''
>>> j.keys()
dict_keys(['fromHash', 'toHash', 'contextLines', 'whitespace', 'diffs', 'truncated'])
>>> j['diffs'][0].keys()
dict_keys(['source', 'destination', 'hunks', 'truncated'])
>>> j['diffs'][0]['hunks'][0].keys()
dict_keys(['sourceLine', 'sourceSpan', 'destinationLine', 'destinationSpan', 'segments', 'truncated'])
>>> j['diffs'][0]['hunks'][0]['segments'][0].keys()
dict_keys(['type', 'lines', 'truncated'])
'''


def get_list(csci, reqid):
    url = 'http://172.17.118.204:7990/rest/api/latest/projects/TTWSRC/repos/%s/pull-requests/%s/changes' % (csci, reqid)
    headers['Referer'] = "http://172.17.118.204:7990/projects/TTWSRC/repos/%s/pull-requests/%s/diff" % (csci, reqid)
    req = requests.get(url, headers=headers, params=params2)
    print(req)
    outfiles = []
    if req.status_code == 200:
        j = json.loads(req.content)
        #pprint.pprint(j)
        outs = []
        for files in j['values']:
            '''if files['type'] == 'ADD':
                files['fromContentId'] = j['fromHash']
                outfiles.append(get_a_file(files, csci))
            elif files['type'] == 'MODIFY':
                outfiles.append(get_a_file(files, csci))
            '''
            if not files['path']['toString'].endswith('wav'):
                files['fromContentId'] = j['fromHash']
                files['contentId'] = j['toHash']
                outfiles.append(get_a_file(files, csci))
        with open(url[url.rfind('/') + 1:], 'wb') as fo:
            fo.write('\n'.join(outs).encode('utf8'))
    return outfiles


def get_a_file(f, csci):
    '''http://172.17.118.204:7990/rest/api/latest/projects/TTWSRC/repos/fdp/commits/6a9c1860c77746ea37252b2d72b2bc5b1db835b8/diff/TowerBUSINESS/src/com/thales/tower/business/realization/fpl/FplManager.java?contextLines=10000&since=2de3a145c8df1640ea94e4e9dbdca8b7f51c67d1&whitespace=show&withComments=false'''
    url = 'http://172.17.118.204:7990/rest/api/latest/projects/TTWSRC/repos/%s/commits/%s/diff/%s' % (
        csci, f['contentId'], f['path']['toString'])
    params['since'] = f['fromContentId']
    print(url)
    #pprint.pprint(params)
    req = requests.get(url, headers=headers, params=params)
    print(req)
    print(req.content)
    ofile = None
    if req.status_code == 200:
        j = json.loads(req.content)
        #pprint.pprint(j)
        outs = []
        for diffs in j['diffs']:
            for hunks in diffs['hunks']:
                for segments in hunks['segments']:
                    if segments['type'] == 'CONTEXT':
                        #outs.extend(map(lambda x: "[%s] %s"% (x['destination'],x['line']), segments['lines'][-10:]))
                        outs.extend(map(lambda x: x['line'], segments['lines'][-10:]))
                    elif segments['type'] == 'ADDED': # no handle REMOVED
                        #outs.extend(map(lambda x: "[%s] %s"% (x['destination'],x['line']), segments['lines']))
                        outs.extend(map(lambda x: x['line'], segments['lines']))
        ofile = f['path']['toString'].replace('/', '-')
        with open(ofile, 'wb') as fo:
            fo.write('\n'.join(filter(lambda x: x.strip(), outs)).encode('utf8'))
    return ofile


def main(inlist):
    outfiles =  []
    for csci, reqid in inlist:
        print("%s  [%s]" %(csci, reqid))
        outfiles.extend(get_list(csci, reqid))
        with open('total.result', 'wb') as fo2:
            for f in outfiles:
                if f:
                    with open(f, 'rb') as fo1:
                        fo2.write(fo1.read()+b'\n')


if __name__ == "__main__":
    inlist = [
        ('etcommon', 19),
        ('fdp', 69),
        ('ttwconf', 64),
        ('applications', 74),
        ('fdp', 143),
        ('etcommon', 30),
        ('fdp', 151),
        ('ttwconf', 146),
        ('applications', 192),
        ('ttwconf', 144),

    ]
    main(inlist)

