#!/usr/bin/env python
# coding: utf8

import urllib, urllib2, csv, sys, os
import threading
from pyquery import PyQuery
from urlparse import urlparse

def err(str=None):
    if str is not None:
        print str
    # down url example: http://www.ccf.org.cn/sites/ccf/jsjtbbd.jsp?contentId=2732460526829
    print "Usage: %s [down url] [target dirname]" % sys.argv[0]
    sys.exit(-1)

def downPDF(f_name, durl):
    print "Download %s ..." % f_name
    pq = PyQuery(urllib2.urlopen(durl).read())
    dlink = "http://history.ccf.org.cn/" + pq('#pt3437field a').attr('href')
    if urlparse(dlink).path.split('/')[-1] == '1.pdf':
        fpath = os.path.join(tar_path, "1-" + f_name + ".pdf")
    else:
        fpath = os.path.join(tar_path, f_name + ".pdf")

    urllib.urlretrieve(dlink, fpath)

def main_dwn():
    if os.path.exists(tar_path) is False:
        os.makedirs(tar_path)
    else:
        if os.path.isdir(tar_path) is False:
            err("Error: %s is a file! " % tar_path)

    ts = []
    for f_name in name_link_map:
        durl = name_link_map[f_name]
        t = threading.Thread(target=downPDF, args=(f_name, durl))
        ts.append(t)

    for t in ts:
        t.start()

    for t in ts:
        t.join()

def extract_url(p_url):
    p_content = urllib2.urlopen(p_url).read()
    pq = PyQuery(p_content)
    for a_tag in map(lambda a: PyQuery(a), pq('#pt6109')('a')):
        name_link_map[u"专题-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt0859')('a')):
        name_link_map[u"特邀报告-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt8671')('a')):
        name_link_map[u"封面报道-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt7906')('a')):
        name_link_map[u"专栏-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt4094')('a')):
        name_link_map[u"视点-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt7859')('a')):
        name_link_map[u"动态-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt2171')('a')):
        name_link_map[u"译文-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')
    for a_tag in map(lambda a: PyQuery(a), pq('#pt5765')('a')):
        name_link_map[u"学会论坛-" + a_tag.text().strip()] = a_tag.attr('href').replace('freetybgcont', 'freexiazai')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s [down url] [target dirname]" % sys.argv[0]
        sys.exit(-1)

    p_link = sys.argv[1]
    tar_path = sys.argv[2]
    name_link_map = {}

    extract_url(p_link)
    main_dwn()
