# -*- coding: utf-8 -*-
import scrapy
from ..items import LZItem
from ..utils.mongodb_client import MongoDBClient


class LZSpider(scrapy.Spider):
    name = "lz"
    start_urls = None

    def __init__(self, mongo_uri, mongo_db, mongo_coll):
        mongo_client = MongoDBClient(mongo_uri, mongo_db, mongo_coll)
        mongo_client.open()
        self.max_update_time = mongo_client.get_max_by_field("update_time")
        mongo_client.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_coll=crawler.settings.get('MONGO_COLLECTION', 'scrapy_items')
        )

    def parse(self, response):
        for m in response.xpath("//tr[contains(@bgcolor, 'F5FAFE')]"):
            tds = m.css("td")
            try:
                if len(tds) == 5:
                    item = LZItem(
                        title=tds[0].css("a::text").extract_first(),
                        ctype=tds[1].css("::text").extract_first(),
                        region=tds[2].css("::text").extract_first(),
                        page_url=response.urljoin(tds[0].css(
                            "a::attr(href)").extract_first()),
                        update_time=tds[4].css("::text").extract_first()
                    )

                    if item["update_time"] <= self.max_update_time:
                        return

                    if item["page_url"] is not None:
                        item_page = response.urljoin(item["page_url"])
                        yield response.follow(item_page, callback=self.parse_item, meta={"item": item})
            except:
                self.log("error from item: " + str(m))

        for x in response.css(".pagegbk"):
            if x.css("::text").extract_first() == u"下一页":
                next_page = x.css("::attr(href)").extract_first()
                self.log(next_page)
                yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):
        item = response.meta["item"]
        item["description"] = response.xpath(
            "//div[@class='intro']").extract_first()
        item["download_urls"] = response.css("div#pllist li a::text").extract()
        item["image_url"] = response.css("img.img::attr(src)").extract_first()
        return item
