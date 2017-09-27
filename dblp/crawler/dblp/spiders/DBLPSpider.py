# -*- coding: utf-8 -*-
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
                for line in fin.xreadlines():
                    if not str(line).startswith("#"):
                        self.conference_list.append(line.strip())
        if self.jour_file:
            with open(self.jour_file, 'r') as fin:
                for line in fin.xreadlines():
                    if not str(line).startswith("#"):
                        self.journal_list.append(line.strip())

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
            ret = bib_obj.entries[0]
            ret.update(response.meta)
            return ret
