# -*- coding: utf-8 -*-
import re
import json
import urlparse
import scrapy
import bibtexparser


class DBLPSimpleSpider(scrapy.Spider):
    name = 'dblp_issue'

    def __init__(self, start_url="", *args, **kwargs):
        super(DBLPSimpleSpider, self).__init__(*args, **kwargs)
        if start_url is not "":
            self.logger.info("start url %s", start_url)
            self.start_urls.append(start_url)

    def parse(self, response):
        meta = {}
        ttype = response.url.split('/')[-3]
        if ttype == 'conf':
            meta["_type"] = "conference"
        elif ttype == 'jour':
            meta["_type"] = "journal"
        meta["_dname"] = response.url.split('/')[-2]
        meta["_pname"] = response.url.split('/')[-1].split('.')[0]

        # TODO storage structure
        # proceedings
        #   - session
        #       - article list
        for e in response.xpath('//header[not(contains(@class, "headline noline"))]'):
            article_list = e.xpath('following-sibling::ul[1]')
            meta["_session"] = e.css("::text").extract_first()
            for link in article_list.xpath("./a[contains(text(), 'BibTeX')]/@href"):
                yield response.follow(link, callback=self.get_bibtex, meta=meta)

    def get_bibtex(self, response):
        bibtexts = response.xpath(
            "//div[@id='bibtex-section']//text()").extract()
        bibtexts = filter(lambda e: e.strip() != "", bibtexts)

        bib_obj = bibtexparser.loads(bibtexts[0])

        if len(bib_obj.entries) != 0:
            bib_dict = bib_obj.entries[0]
            bib_dict.update(response.meta)
            # return ret

            if 'link' in bib_dict:
                article_link = bib_dict['link']

                if article_link.endswith('.pdf'):
                    self.logger.info(
                        "cannot parse the pdf link currently, try scholar for %s", response.url)
                elif 'acm' in article_link:
                    yield scrapy.Request(
                        article_link,
                        callback=self.parse_acm,
                        meta={"bib": bib_dict}
                    )
                else:
                    yield scrapy.Request(
                        article_link,
                        callback=self.parse_article,
                        meta={"bib": bib_dict}
                    )
            else:
                # search by google scholar
                self.logger.info(
                    "can not find the link in the bibtex, try scholar for %s", response.url)
        else:
            self.logger.info("no bib entry for %s", response.url)

    def parse_acm(self, response):
        """
        Get the dl.acm abstract link
        """
        if 'dl.acm.org/citation' in response.url:
            body = response.body
            items = re.findall(
                '.*abstract\',\'bindExpr\':\[\'(.*)\'\]\}.*', body, re.MULTILINE)
            if len(items) != 0:
                # redirect to abstract page
                yield response.follow(
                    items[0],
                    callback=self.parse_article,
                    meta=response.meta
                )

    def parse_article(self, response):
        """
        Extract the abstract and key words from the article link
        """
        bib_item = response.meta["bib"]
        abst = ""
        key_words = []
        if 'link.springer.com' in response.url:
            # from the springer
            abst = response.xpath(
                "//section[@class='Abstract']/p/text()"
            ).extract_first()
            key_words = response.xpath(
                "//div[@class='KeywordGroup']/span[@class='Keyword']/text()"
            ).extract()
            key_words = map(lambda e: e.strip(), key_words)
        elif 'ieeexplore.ieee.org' in response.url:
            # from the ieeexplore
            body = response.body
            items = re.findall(
                '.*global.document.metadata=(.*);$', body, re.MULTILINE)
            if len(items) != 0:
                meta = json.loads(items[0])
                if "abstract" in meta and "keywords" in meta:
                    abst = meta["abstract"]
                    for kwd in meta["keywords"]:
                        if kwd["type"].strip() == "Author Keywords":
                            key_words = kwd["kwd"]
                else:
                    self.logger.info(
                        "no keywords or abstract in meta-information, skip %s", response.url)
            else:
                self.logger.info(
                    "cannot get the metadata from %s", response.url)
        elif 'dl.acm.org/tab_abstract' in response.url:
            # dl.acm
            # abst = response.xpath("//p/text()").extract_first()
            abst = "".join(response.xpath("//p//text()").extract())
        elif 'dl.acm.org/citation' in response.url:
            # return self.parse_acm(response)
            self.logger.info("skip url %s", response.url)
        elif 'www.usenix.org' in response.url:
            # usenix
            for field in response.xpath("//div[contains(@class,'field')]"):
                field_header = field.xpath(
                    "./div[@class='field-label']/text()").extract_first()
                if field_header:
                    field_header = field_header.strip().lower()
                    if 'abstract' in field_header:
                        abst = "".join(field.xpath(
                            "./div[@class='field-items']//text()").extract())
                        break

        bib_item['abstract'] = abst
        bib_item['key_words'] = key_words

        return bib_item

    def _get_year(self, str):
        m = re.search('.*?(\d+).*?', str)
        ys = m.group(1)
        if len(ys) < 2:
            if ys < 20:
                y = 2000 + int(ys)
            else:
                y = 1900 + int(ys)
        else:
            y = int(ys)
        return y
