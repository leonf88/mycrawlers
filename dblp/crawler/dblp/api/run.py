import multiprocessing

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ..spiders.dblp_article_spider import DBLPArticleSpider
from ..utils.mongo_client import MongoDBClient

from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)

settings = get_project_settings()
db_client = MongoDBClient(settings.get("MONGODB_URL"), settings.get(
    "MONGODB_DB"), settings.get("MONGODB_COLLECTION"))
db_client.open()


def run(hook):
    process = CrawlerProcess(get_project_settings())

    process.crawl('dblp_article', hook=hook)
    # the script will block here until the crawling is finished
    process.start()


@app.route("/update_abstract", methods=["GET"])
def update_abstract():
    hook = request.args["hook"]
    p = multiprocessing.Process(target=run, args=(hook,))
    p.start()
    p.join()
    article = db_client.get_article_by_hook(hook)
    return jsonify(html=article["abstract"])
