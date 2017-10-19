#!/usr/bin/env python

from lxml import etree
from . import DownloadHelper


def _gu1(sel):
    if sel is None or len(sel) == 0:
        return None
    else:
        return sel[0]


class UsenixDowloader(DownloadHelper):
    def __init__(self,  *args, **kwargs):
        super(UsenixDowloader, self).__init__(source="usenix", *args, **kwargs)

    def parse(self, url):
        req = self.session.get(url)
        html = req.content
        selector = etree.HTML(html)
        ret = self.parse_17(selector)
        if not ret:
            ret = self.parse_16(selector)
        if not ret:
            print "failed to download ", url

    def parse_17(self, sel):
        title = _gu1(sel.xpath('//h1[contains(@id, "page-title")]/text()'))
        pdf_url = _gu1(sel.xpath("//span[@class='file']/a[1]/@href"))
        slides_url = _gu1(
            sel.xpath("//div[@class='usenix-schedule-slides']/a[1]/@href"))
        bib_text = ''.join(
            sel.xpath('//div[contains(@class, "bibtex-text-entry")]/text()'))
        return self.download_simple(title, pdf_url, slides_url, bib_text)

    def parse_16(self, sel):
        title = _gu1(sel.xpath('//h1[contains(@class, "page-title")]/text()'))
        pdf_url = _gu1(sel.xpath("//span[@class='file']/a[1]/@href"))
        slides_url = _gu1(
            sel.xpath("//div[@class='usenix-schedule-slides']/a[1]/@href"))
        bib_text = ''.join(
            sel.xpath('//div[contains(@class, "bibtex-text-entry")]/text()'))
        return self.download_simple(title, pdf_url, slides_url, bib_text)
