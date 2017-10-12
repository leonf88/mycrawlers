#!/usr/bin/env python
# coding: utf8

import urllib, urllib2, sys, os, re, urlparse
import json
from pyquery import PyQuery
from sets import Set

reload(sys)
sys.setdefaultencoding('utf8')

class JOSCrawler:
    """Crawler of JOS documents, dump into file and repeated download"""

    max_record = 10

    def __init__(self, max_record):
        self.docs = []
        self.max_record = max_record
        pass

    def getJURLs(self, p_url):
    # to the page:     http://www.jos.org.cn/ch/reader/issue_list.aspx
    # to main page: http://www.jos.org.cn/ch/reader/issue_browser.aspx
    # to one page:     http://www.jos.org.cn/ch/reader/issue_list.aspx?year_id=2014&quarter_id=1
    # {'Y': {'name':'url',...},...}
        p_content = urllib2.urlopen(p_url).read()
        p_content = p_content.decode('utf8')
        pq = PyQuery(p_content)

        p_info = {}
        for tr_tag in map(lambda tr: PyQuery(tr), PyQuery(pq('#QueryUI')('table')[1])('tr')):
            year = PyQuery(tr_tag('b')[0]).text().strip()
            p_info[year] = {}
            for oneJ in map(lambda li: PyQuery(li), tr_tag('li')):
                name = oneJ('a').text()
                sub_URL = oneJ('a') .attr('href')
                p_info[year][name] = urlparse.urljoin(p_url, sub_URL)

        return p_info
    # {'fname_chs':fname_chs, 'fname_en': fname_en, 'abst_chs': abst_chs, 'abst_en': abst_en}
    def getDocInfo(self, d_url):
        # TODO get the author information
        print d_url
        p_content = urllib2.urlopen(d_url).read()
        p_content = p_content.decode('utf8')
        pq = PyQuery(p_content)
        d_info = {}
        d_info['fname_chs'] = pq('#FileTitle').text()
        d_info['fname_en'] = pq('#EnTitle').text()
        d_info['abst_chs'] = pq('#Abstract').text()
        d_info['abst_en'] = pq('#EnAbstract').text()
        return d_info

    def getJDocs(self, j_url):
    # {jouranl_name:
    #    {
    #        jouranl_column:[
    #                { doc:{'dname': dname, 'durl', durl, 'dInfo': {...}}},
    #                 ...
    #            ],
    #        ...
    #    },
    #    ...
    # }
        p_content = urllib2.urlopen(j_url).read()
        p_content = p_content.decode('utf8')
        pq = PyQuery(p_content)
        j_info = {}
        td_n = pq('#table3').children('tbody').children('tr').children('td')
        j_name = PyQuery(td_n.children('p')[0]).text()
        j_info[j_name] = {}
        coln = len(td_n.children('p'))
        for i in range(1,coln):
            column = PyQuery(td_n.children('p')[i]).text()
            if(column == None):
                continue
            if j_info[j_name].has_key(column) is False:
                j_info[j_name][column] = []
            # for d in map(lambda tr: PyQuery(tr), PyQuery(td_n('#table24')[i])('tr')('table')):
            #     if(d('a')):
            #         d_name = PyQuery(d('a')[0]).text()
            #         d_abst = urlparse.urljoin(j_url, PyQuery(d('a')[1]).attr('href'))
            #         d_down = urlparse.urljoin(j_url, PyQuery(d('a')[2]).attr('href'))
            #         j_info[j_name][column].append({'dname': d_name, 'durl': d_down, 'dInfo':self.getDocInfo(d_abst)})
            cnt = 0
            for d in map(lambda tr: PyQuery(tr), PyQuery(td_n('#table24')[i])('tr')):
                if cnt % 4 == 1:
                    d_name = PyQuery(d('a')[0]).text()
                elif cnt % 4 == 3:
                    if len(d('a')) == 0:
                        continue
                    d_abst = urlparse.urljoin(j_url, PyQuery(d('a')[0]).attr('href'))
                    d_down = urlparse.urljoin(j_url, PyQuery(d('a')[1]).attr('href'))
                    j_info[j_name][column].append({'dname': d_name, 'durl': d_down, 'dInfo':self.getDocInfo(d_abst)})
                cnt += 1

        return j_info

    def run(self, p_url, r_file = 'jos.json', w_file = 'jos.json'):
        self.docs = self.incrGetDocs(p_url, r_file)
        self.write(self.docs, w_file)

    def write(self, data, w_file = 'jos.json'):
        """write the documents on disk with json format"""
        cnt = 0
        jf = open(w_file, 'w')
        for item in sorted(data, key=lambda item: item['jname']+" "+item['jissue'], reverse=True):
            jf.write(json.dumps(item, ensure_ascii=False) + "\r\n")
            jf.flush()
            cnt += 1
        jf.close()

        print "Write [%d] Records" % cnt

    def incrGetDocs(self, p_url, r_file = 'jos.json'):
        docs = []
        if os.path.exists(r_file) and os.path.isfile(r_file):
            docs = self.read(r_file)
        readed_docs = {}
        for k, s in map(lambda doc: [doc[u'jname'], doc[u'jissue']], docs):
            if readed_docs.has_key(k) is False:
                readed_docs[k]=[]
            readed_docs[k].append(s)
        p_info = self.getJURLs(p_url)

        except_docs = []
        for jname in p_info.keys():
            for jissue in p_info[jname].keys():
                if (jname not in readed_docs) or (jissue not in readed_docs[jname]):
                    except_docs.append({"jname":jname, "jissue": jissue, "url": p_info[jname][jissue]})
                    # self.docs.append(, "content": self.getJDocs(p_info[jname][jissue])})

        # Set the max number of output records each time
        max_len = min(self.max_record, len(except_docs))
        except_docs = except_docs[0:max_len]
        except_docs = self.download(except_docs)
        docs.extend(except_docs)

        return docs

    def download(self, except_docs):
        cnt = 0
        total_docs = len(except_docs)
        for item in except_docs:
            item['content'] = self.getJDocs(item['url'])
            cnt += 1
            # print progress
            rate = float(cnt) / float(total_docs)
            rate_num = int(rate * 100)
            print '\r%-20s%-10s%3d/%d......%3d%%' % (item['jname'], item['jissue'], cnt, total_docs, rate_num),
            sys.stdout.flush()
        return except_docs

    def read(self, r_file='jos.json'):
        """read the documents from file with json format"""
        jf = open(r_file, 'r')
        docs = []
        with open(r_file) as file:
            for line in file:
                obj = json.loads(line.encode('utf8'), encoding = 'utf8')
                docs.append(obj)
        return docs

def dmpTex(r_file, w_file=None):
    if w_file is None:
        w_file = 'jos.tex'
    out_f = open(w_file, 'w')
    in_f = open(r_file, 'r')

    out_f.write('''\\documentclass[a4paper]{article}
\\usepackage{ctex}
\\usepackage[colorlinks,linkcolor=red]{hyperref}
\\usepackage[top=2cm, bottom=2cm, left=2.5cm, right=2.5cm]{geometry}

\\begin{document}

\\title{软件学报历年目录}
\\author{Fan Liang}
\\date{\\today}
\\maketitle

''')
    def __makeStr(name, data):
        str = '\\subsection{%s}\n' % name
        for j_col in data:
               if j_col is not None:
                   str += "\href{%s}{%s}\n\n" % (j_col['durl'], j_col['dname'].replace('#',' '))
        return str

    # 在线出版
    # 综述文章
    # 本期目录
    # 模式识别与人工智能
    # 理论计算机科学
    # 专刊文章
    def __writeTopics(jname, t):
        if t in obj[jname] and len(obj[jname][t]) != 0:
            out_f.write('''
\\section{\\textbf{%s}}
''' % (jname))
            out_f.write(__makeStr(t, obj[jname][t]))
            out_f.flush()

    # topics = Set()
    for line in in_f:
        obj1 = json.loads(line.encode('utf8'), encoding="utf8")
        obj = obj1['content']
        jname = obj.keys()[0]
        # __writeTopics(jname, u'理论计算机科学')
        out_f.write('''
\\section{\\textbf{%s}}
''' % (jname))
        for t in sorted(obj[jname].keys(), reverse=True):
               out_f.write(__makeStr(t, obj[jname][t]))
               out_f.flush()

    out_f.write("\n\end{document}")
    out_f.close()

if __name__ == '__main__':
    max_record = 10
    main_page = "http://www.jos.org.cn/ch/reader/issue_browser.aspx"
    crawler = JOSCrawler(max_record)
    crawler.run(main_page)
    dmpTex('jos.json')
