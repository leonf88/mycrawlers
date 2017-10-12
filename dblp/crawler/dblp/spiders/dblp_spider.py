# -*- coding: utf-8 -*-
import re
import json
import urlparse
import scrapy
import bibtexparser
from ..utils.dblp_parse import DBLPParser


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

        self.parser = DBLPParser(settings, self.logger)
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
        return self.parser.get_conf_list(response)
