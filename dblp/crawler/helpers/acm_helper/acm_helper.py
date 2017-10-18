#!/usr/bin/env python

import sys
import re
import os
import requests
import urlparse
from lxml import etree

redownload = True

ua = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)"
headers = {
    'User-Agent': ua,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
}
s = requests.session()
s.headers = headers


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def download(url, filename):
    if os.path.exists(filename) and not redownload:
        print "exist file: {}, skip donwload.".format(filename)
        return filename
    print "downloading file: ", filename
    url = url.replace("https", "http")
    r = s.get(url, stream=True)
    total_length = int(r.headers['content-length'])
    with open(filename, 'wb') as f:
        cnt = 0
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                cnt += 1024
                progress(cnt, total_length, "downloading")
    print("")
    return filename


def _format_filename(name):
    return re.sub('[:,\'\!\@#\$\%\^&\*\(\)\/]', '', name.lower()).replace(' ', '_')


def run(url):
    r = s.get(url, headers=headers)
    html = r.content
    selector = etree.HTML(html)
    title = _format_filename(selector.xpath(
        '//div[@id="divmain"]//h1[@class="mediumb-text"]//text()')[0])
    pdf_url = selector.xpath('//a[@name="FullTextPDF"]/@href')
    if len(pdf_url) != 0:
        pdf_url = urlparse.urljoin(r.url, pdf_url[0])
    download(pdf_url, title + ".pdf")


if __name__ == '__main__':
    with open('urls.txt', 'r') as fin:
        for url in fin.xreadlines():
            if url.strip() is "" or url.startswith("#"):
                continue
            run(url)
