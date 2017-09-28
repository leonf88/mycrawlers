# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import re
import random
import base64

from scrapy import signals


class RandomUserAgentMiddleware(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, settings):
        self.settings = settings
        self.user_agent = self.settings['USER_AGENT_LIST']

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        o = cls(settings)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent)
        if ua:
            headers = {
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Accept-Encoding': 'gzip, deflate',
            }
            for k in headers.keys():
                request.headers.setdefault(k, headers[k])
            # request.headers.setdefault(b'User-Agent', ua)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
