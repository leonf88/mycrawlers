# -*- coding: utf-8 -*-
import re
import json
import urlparse
import scrapy
import bibtexparser


class DBLPSpider(scrapy.Spider):
    name = 'dblp'
    BASE_URL = 'http://dblp.uni-trier.de'

    def __init__(self, settings):
        self.conf_file = settings.get("CONF_FILE", None)
        self.jour_file = settings.get("JOUR_FILE", None)

        self.conference_list = []
        self.journal_list = []

        if self.conf_file:
            with open(self.conf_file, 'r') as fin:
                self.conference_list = [e.strip() for e in filter(
                    lambda line: not line.startswith("#"), fin.xreadlines())]
        if self.jour_file:
            with open(self.jour_file, 'r') as fin:
                self.journal_list = [e.strip() for e in filter(
                    lambda line: not line.startswith("#"), fin.xreadlines())]

        self.logger.info("Conference List [%d], Journal List [%d]",
                         len(self.conference_list), len(self.journal_list))

    @classmethod
    def from_crawler(cls, crawler):
        spider = cls(crawler.settings)
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):
        for e in self.conference_list:
            yield scrapy.Request(urlparse.urljoin(self.BASE_URL, "/db/conf/" + e), meta={"_type": "conference", "_dname": e})

        for e in self.journal_list:
            yield scrapy.Request(urlparse.urljoin(self.BASE_URL, "/db/journals/" + e), meta={"_type": "journal", "_dname": e})

    def parse(self, response):
        if response.meta["_type"] is 'conference':
            for link in response.xpath("//a[contains(text(), '[contents]')]/@href"):
                yield response.follow(link, callback=self.parse_one_issue, meta=response.meta)

        elif response.meta["_type"] is 'journal':
            for link in response.xpath("//div[@id='main']/ul/li/a/@href"):
                yield response.follow(link, callback=self.parse_one_issue, meta=response.meta)
        else:
            self.logger.info("unknown type %s.", response.meta["_type"])

    def parse_one_issue(self, response):
        # TODO get conference section
        meta = response.meta
        meta["_pname"] = response.url.split("/")[-1].split(".")[0]
        for link in response.xpath("//a[contains(text(), 'BibTeX')]/@href"):
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
