import re
import hashlib
import json
import logging
import bibtexparser
import scrapy
from ..utils.mongo_client import MongoDBClient


class DBLPParser(object):
    def __init__(self, settings, logger):
        self.db_client = MongoDBClient(
            settings.get("MONGODB_URL"),
            settings.get("MONGODB_DB"),
            settings.get("MONGODB_COLLECTION")
        )
        self.db_client.open()
        self.logger = logger

    def get_db_handler(self):
        return self.db_client

    def finish(self):
        self.db_client.close()

    def get_conf_list(self, response):
        """
        URL format: `domain/db/conf/<dname>` or `domain/db/journals/<dname>`
        """
        ttype = response.url.split('/')[-2]
        if ttype is 'conf':
            for e in response.xpath("//a[contains(text(), '[contents]')]/@href"):
                yield response.follow(link, callback=self.get_articles, meta=response.meta)
        elif ttype is 'journals':
            for e in response.xpath("//div[@id='main']/ul/li/a/@href"):
                yield response.follow(link, callback=self.get_articles, meta=response.meta)
        else:
            self.logger.info("unknown type [%s].", ttype)

    def get_articles(self, response):
        """
        URL format: `domain/db/conf/<dname>/<pname>`
        """
        ttype = response.url.split('/')[-3]
        dname = response.url.split('/')[-2]
        pname = response.url.split('/')[-1].split('.')[0]
        title = response.xpath(
            '//header[@class="headline noline"]/h1/text()').extract_first()
        if ttype == u'conf':
            ttype = "conference"
            self.db_client.add_conference_name(dname)
            self.db_client.add_conference_proceeding_title(dname, title, pname)
        elif ttype == u'journals':
            ttype = "journal"
            self.db_client.add_journal_name(dname)
            self.db_client.add_journal_volume_title(dname, title, pname)

        meta = {
            "_key": "article",
            "_type": ttype,
            "_pname": pname,
            "_dname": dname,
        }

        # sessions
        #   - session name
        #       - article list
        sessions = []

        # TODO how to get the child request object and assemble in parent
        heads = response.xpath(
            '//header[not(contains(@class, "headline noline"))]')
        if len(heads) == 0:
            article_list = response.xpath('//ul[@class="publ-list"]')
            articles = []
            for e in article_list.xpath('./li[contains(@class, "entry")]'):
                title = e.xpath(
                    './/span[@class="title"]/text()').extract_first()
                link = e.xpath(
                    './/a[contains(text(), "BibTeX")]/@href').extract_first()
                hook = hashlib.md5(link).hexdigest()
                meta["_hook"] = hook
                articles.append({"title": title, "_hook": hook})
                yield response.follow(link, callback=self.get_bibtex_from_dblp, meta=meta)
            sessions.append({"name": "", "articles": articles})
        else:
            for e in heads:
                article_list = e.xpath('following-sibling::ul[1]')
                session_name = e.css("::text").extract_first()
                articles = []
                for e in article_list.xpath('./li[contains(@class, "entry")]'):
                    title = e.xpath(
                        './/span[@class="title"]/text()').extract_first()
                    link = e.xpath(
                        './/a[contains(text(), "BibTeX")]/@href').extract_first()
                    hook = hashlib.md5(link).hexdigest()
                    meta["_hook"] = hook
                    articles.append({"title": title, "_hook": hook})
                    yield response.follow(link, callback=self.get_bibtex_from_dblp, meta=meta)

                sessions.append({"name": session_name, "articles": articles})
        self.db_client.add_issue(ttype, dname, pname, sessions)
        #
        # for k in sessions.keys():
        #     for e in sessions[k]:
        #         meta["hook"] = e["hook"]
        # yield response.follow(e["link"], callback=self.get_bibtex_from_dblp,
        # meta=meta)

    def get_bibtex_from_dblp(self, response):
        """
        URL format: `domain/rec/bibtex/conf/<dname>/<article_id>`
        Get the article bibinformation from dblp.
        Store the article information.
        """
        bibtexts = response.xpath(
            "//div[@id='bibtex-section']//text()").extract()
        bibtexts = filter(lambda e: e.strip() != "", bibtexts)

        bib_obj = bibtexparser.loads(bibtexts[0])

        if len(bib_obj.entries) != 0:
            bib_dict = bib_obj.entries[0]
            bib_dict.update(response.meta)

            self.db_client.add_article(bib_dict)
            if 'link' in bib_dict:
                article_link = bib_dict['link']

                if article_link.endswith('.pdf'):
                    # TODO pdf parse
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
                # TODO search by google scholar
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
            # abst = "".join(response.xpath("//p//text()").extract())
            abst = response.body
        elif 'dl.acm.org/citation' in response.url:
            return self.parse_acm(response)
            # self.logger.info("skip url %s", response.url)
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
