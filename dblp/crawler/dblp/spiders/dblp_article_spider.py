# -*- coding: utf-8 -*-
import re
import json
import urlparse
import scrapy
import bibtexparser
from .dblp_parse import DBLPParser


class DBLPArticleSpider(scrapy.Spider):
    name = 'dblp_article'

    def __init__(self, settings, hook="", *args, **kwargs):
        super(DBLPArticleSpider, self).__init__(*args, **kwargs)
        self.hook = hook
        self.parser = DBLPParser(settings, self.logger)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):
        if self.hook is not "":
            article = self.parser.db_client.get_article_by_hook(self.hook)
            if article:
                self.logger.info("start url %s", article["link"])
                yield scrapy.Request(article["link"], meta={"bib": article})

    def parse(self, response):
        return self.parser.parse_article(response)
