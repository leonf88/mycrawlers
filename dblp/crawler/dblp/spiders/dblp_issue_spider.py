# -*- coding: utf-8 -*-
import re
import json
import urlparse
import scrapy
import bibtexparser
from .dblp_parse import DBLPParser


class DBLPIssueSpider(scrapy.Spider):
    name = 'dblp_issue'

    def __init__(self, settings, start_url="", *args, **kwargs):
        super(DBLPIssueSpider, self).__init__(*args, **kwargs)
        if start_url is not "":
            self.logger.info("start url %s", start_url)
            self.start_urls.append(start_url)
        self.parser = DBLPParser(settings, self.logger)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def parse(self, response):
        return self.parser.get_articles(response)
