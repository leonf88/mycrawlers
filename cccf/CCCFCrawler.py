#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib, urllib2, sys, os, re, shutil
import json
from pyquery import PyQuery

reload(sys)
sys.setdefaultencoding('utf8')

#__default_url = "http://www.ccf.org.cn/sites/ccf/zgjsjxhtx.jsp"
__default_url = "http://history.ccf.org.cn/sites/ccf/zgjsjxhtx.jsp"
__title_format = "^(\d+)年第(\d+)期\s*（总第(\d+)期）".decode("utf8")
__ccf_domain = "http://history.ccf.org.cn"


def err(str=None):
    if str is not None:
        print str
    # down url example: http://www.ccf.org.cn/sites/ccf/jsjtbbd.jsp?contentId=2732460526829
    print "Usage: %s (<down url>)" % sys.argv[0]
    sys.exit(-1)

# Return the list of content links, each tuple has the format below:
# [id, title, url]
def extURLs(p_url):
    rc = re.compile(__title_format)
    links = []
    while True:
        p_content = urllib2.urlopen(p_url).read()
        pq = PyQuery(p_content)
        next_href = None
        for a_tag in map(lambda a: PyQuery(a), pq('#pt6781FootPager')('a')):
            txt = a_tag.text().strip()  # .decode('utf8')
            if txt == u'下一页':
                next_href = __ccf_domain + a_tag.attr('href')
                break

        for a_tag in map(lambda a: PyQuery(a), pq('#pt6781')('li')('a')):
            title = a_tag.attr('title').strip()  # .decode('utf8')
            href = a_tag.attr('href')
            m = rc.match(title)
            if m is None:
                print "%s is not match the title format '%s'" % (title, __title_format)
            else:
                links.append((int(m.group(3)), title, href))

            # TODO break
        if next_href is None:
            break
        else:
            p_url = next_href

    return sorted(links, key=lambda x:x[0], reverse=True)

def extInfo(link):
    # TODO extract the information in HTML format, which is different from the current ID format.
    idx = link[0]
    title = link[1]
    p_url = link[2]
    p_content = urllib2.urlopen(p_url).read()
    pq = PyQuery(p_content)
    # introduction
    intr = PyQuery(pq('#pt2390field')[0]).text().strip()

    def __func(id):
        t = []
        for a_tag in map(lambda a: PyQuery(a), pq('#' + id)('a')):
            s_pq = PyQuery(urllib2.urlopen(a_tag.attr('href').replace('freetybgcont', 'freexiazai')).read())
            u_sfx = s_pq('#pt3437field a').attr('href')
            dlink = None
            if u_sfx is not None:
                dlink = __ccf_domain + u_sfx
            t.append({'text':a_tag.text().strip(), 'url':dlink})
        return t

    return {'1title':{'index':idx, 'name':title, 'url':p_url},
            '2intro':intr,
            '30sbjct':{'name':'专题', 'data':__func('pt6109')},
            '31invit':{'name':'特邀报告', 'data':__func('pt0859')},
            '40cover':{'name':'封面报道', 'data':__func('pt8671')},
            '50progm':{'name':'专栏', 'data':__func('pt7906')},
            '51view':{'name':'视点', 'data':__func('pt4094')},
            '60trend':{'name':'动态', 'data':__func('pt7859')},
            '70trans':{'name':'译文', 'data':__func('pt2171')},
            '80forum':{'name':'学会论坛', 'data':__func('pt5765')},
            '90spec':{'name':'特别报道', 'data':__func('pt0156')}
            }

def dmpJson(p_url, w_file='ccf.json'):
    jf = open(w_file, 'w')
    cnt = 0
    urls = extURLs(p_url)
    sum = len(urls)
    for lk in urls:
        tuple = extInfo(lk)
        jf.write(json.dumps(tuple, ensure_ascii=False) + "\n")
        jf.flush()
        cnt += 1
        # print progress
        rate = float(cnt) / float(sum)
        rate_num = int(rate * 100)
        print '\r%-20s%3d/%d......%3d%%' % (tuple['1title']['name'], cnt, sum, rate_num),
        sys.stdout.flush()

    jf.close()
    print "Write [%d] Records" % cnt
    return w_file

def loadJson(r_file):
    objs = []
    with open(r_file) as file:
        for line in file:
            obj = json.loads(line.encode('utf8'), encoding="utf8")
            objs.append(obj)

    return objs

def incrDmpJson(p_url, w_file='ccf.json'):
    # backup the JSON file
    # TODO check file exist
    if os.path.isfile(w_file):
        print "Backup the file %s" % w_file
        shutil.copy2(w_file, w_file + ".bak")
        # get the basic URLs incrementally
        objs = loadJson(w_file)
        old_titles = map(lambda obj:obj['1title']['name'], objs)
        exist_titles = set(old_titles)
        curUrls = extURLs(p_url)
        newUrls = filter(lambda url:url[1] not in exist_titles, curUrls)
    else:
        objs=[]
        newUrls = extURLs(p_url)

    print "Get %d new records" % len(newUrls)

    cnt, sum = 0, len(newUrls)
    print "Download %d records into JSON Objects" % sum
    for lk in newUrls:
        o = extInfo(lk)
        objs.append(o)
        # print progress
        cnt += 1
        rate = float(cnt) / float(sum)
        rate_num = int(rate * 100)
        print '\r%-20s%3d/%d......%3d%%' % (o['1title']['name'], cnt, sum, rate_num),
        sys.stdout.flush()

    objs.sort(cmp=lambda b, a:cmp(a['1title']['index'], b['1title']['index']))

    jf = open(w_file, 'w')
    for tuple in objs:
        jf.write(json.dumps(tuple, ensure_ascii=False) + "\n")
        jf.flush()
    jf.close()
    print "Write [%d] Records" % cnt
    return w_file

def dmpTex(r_file, w_file=None):
    if w_file is None:
        w_file = 'ccf.tex'
    out_f = open(w_file, 'w')
    in_f = open(r_file, 'r')

    out_f.write('''\\documentclass[a4paper]{article}
\\usepackage{ctex}
\\usepackage[colorlinks,linkcolor=red]{hyperref}
\\usepackage[top=2cm, bottom=2cm, left=2.5cm, right=2.5cm]{geometry}

\\begin{document}

\\title{CCF通讯历年主题列表}
\\author{Fan Liang}
\\date{\\today}
\\maketitle

''')
    def __makeStr(m):
        # TODO the text should filter the symbols which is illegal for latex
        str = '\\subsection{%s}\n' % m['name']
        for t in m['data']:
            if t['url'] is not None:
                str += "\href{%s}{%s}\n\n" % (t['url'], t['text'].replace('&', '\&'))
            else:
                str += "%s\n\n" % t['text'].replace('&', '\&')
        return str

    for line in in_f:
        obj = json.loads(line.encode('utf8'), encoding="utf8")
        out_f.write('''
\\section{\\href{%s}{\\textbf{%s}}}
%s
''' % (obj['1title']['url'], obj['1title']['name'], obj['2intro']))
        for t in sorted(obj.keys())[2:]:
            if len(obj[t]['data']) != 0:
                out_f.write(__makeStr(obj[t]))
                out_f.flush()
    out_f.write("\n\end{document}")
    out_f.close()

# def chg():
#     objs = loadJson('ccf.json.bak2')
#     print len(objs)
#     i = 93
#     for o in objs:
# #         print o['1title']['name'],o['1title']['index']
#         o['1title']['index'] = i
#         i -= 1
#
#     jf = open('ccf.json', 'w')
#     cnt, sum = 0, len(objs)
#     print "Dump %d records into JSON file" % sum
#     for tuple in objs:
#         jf.write(json.dumps(tuple, ensure_ascii=False) + "\n")
#         jf.flush()
#         cnt += 1
#         # print progress
#         rate = float(cnt) / float(sum)
#         rate_num = int(rate * 100)
#         print '\r%-20s%3d/%d......%3d%%' % (tuple['1title']['name'], cnt, sum, rate_num),
#         sys.stdout.flush()
#     jf.close()

if __name__ == '__main__':
#     chg()
    incrDmpJson(__default_url, 'ccf.json')
    dmpTex('ccf.json')

