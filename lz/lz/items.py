# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LZItem(scrapy.Item):
    # define the fields for your item here like:
    # information from the lelezy
    title = scrapy.Field()
    ctype = scrapy.Field()
    region = scrapy.Field()
    page_url = scrapy.Field()
    image_url = scrapy.Field()
    image_path = scrapy.Field()
    download_urls = scrapy.Field()  # maybe array
    update_time = scrapy.Field()
    description = scrapy.Field()
    designation = scrapy.Field()
    # basic video information from the orignal productor
    actors = scrapy.Field()
    gallery = scrapy.Field()
    original_url = scrapy.Field()
