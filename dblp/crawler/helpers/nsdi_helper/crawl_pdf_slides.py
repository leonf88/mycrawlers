#!/usr/bin/env python

import os
import requests
import re
from lxml import etree

redownload = False


def download(url, filename):
    if os.path.exists(filename) and not redownload:
        print "exist file: {}, skip donwload.".format(filename)
        return filename
    print "downloading file: ", filename
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return filename


def _format_filename(name):
    return re.sub('[:,\'\!\@#\$\%\^&\*\(\)]', '', name.lower()).replace(' ', '_')


def download_page(title, pdf_url, slides_url, bib_text):
    if len(title) != 0:
        title = title[0].strip()
    else:
        return None
    filename_prefix = _format_filename(title)
    download(pdf_url, filename_prefix + ".pdf")
    download(slides_url, filename_prefix + "_slides.pdf")
    with open(filename_prefix + '.bib', 'w') as fout:
        fout.write(bib_text)
    return title


def parse_17(selector):
    title = selector.xpath('//h1[contains(@id, "page-title")]/text()')
    pdf_url = selector.xpath("//span[@class='file']/a[1]/@href")[0]
    slides_url = selector.xpath(
        "//div[@class='usenix-schedule-slides']/a[1]/@href")[0]
    bib_text = ''.join(selector.xpath(
        '//div[contains(@class, "bibtex-text-entry")]/text()'))
    return download_page(title, pdf_url, slides_url, bib_text)


def parse_16(selector):
    title = selector.xpath('//h1[contains(@class, "page-title")]/text()')
    pdf_url = selector.xpath('//span[@class="file"]/a[1]/@href')[0]
    slides_url = selector.xpath(
        "//div[@class='usenix-schedule-slides']/a[1]/@href")[0]
    bib_text = ''.join(selector.xpath(
        '//div[contains(@class, "bibtex-text-entry")]/text()'))
    return download_page(title, pdf_url, slides_url, bib_text)


with open("urls.txt", "r") as fin:
    for line in fin.xreadlines():
        if line[0] is "#":
            continue
        url = line.strip()
        req = requests.get(url)
        html = req.content
        selector = etree.HTML(html)
        ret = parse_17(selector)
        if not ret:
            ret = parse_16(selector)
        if not ret:
            print "failed to download ", url
