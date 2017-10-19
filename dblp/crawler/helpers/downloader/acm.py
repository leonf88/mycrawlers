#!/usr/bin/env python

import urlparse
from lxml import etree
from . import DownloadHelper, format_filename


class ACMDowloader(DownloadHelper):
    def __init__(self,  *args, **kwargs):
        super(ACMDowloader, self).__init__(source="acm", *args, **kwargs)

    def parse(self, url):
        r = self.session.get(url)
        html = r.content
        selector = etree.HTML(html)
        title = selector.xpath(
            '//div[@id="divmain"]//h1[@class="mediumb-text"]//text()')
        pdf_url = selector.xpath('//a[@name="FullTextPDF"]/@href')
        if len(pdf_url) != 0:
            pdf_url = urlparse.urljoin(r.url, pdf_url[0])

        if title is None:
            print "title is empty."
            return None
        if type(title) is list:
            if len(title) != 0:
                title = title[0].strip()
            else:
                print "title is empty."
                return None

        filename_prefix = format_filename(title)
        self.download(pdf_url, filename_prefix + ".pdf")
