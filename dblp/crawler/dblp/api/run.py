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
    # p = multiprocessing.Process(target=run, args=(hook,))
    # p.start()
    # p.join()
    # article = db_client.get_article_by_hook(hook)
    # return jsonify(html=article["abstract"])
    #return jsonify({
    #    "html": "\r\n\t\t\t<div style=\"margin-left:10px; margin-top:10px; margin-right:10px; margin-bottom: 10px;\" class=\"tabbody\">\r\n\r\n             <div style=\"display:inline\"><p>In theory, database transactions protect application data from corruption and integrity violations. In practice, database transactions frequently execute under weak isolation that exposes programs to a range of concurrency anomalies, and programmers may fail to correctly employ transactions. While low transaction volumes mask many potential concurrency-related errors under normal operation, determined adversaries can exploit them programmatically for fun and profit. In this paper, we formalize a new kind of attack on database-backed applications called an <i>ACIDRain</i> attack, in which an adversary systematically exploits concurrency-related vulnerabilities via programmatically accessible APIs. These attacks are not theoretical: ACIDRain attacks have already occurred in a handful of applications in the wild, including one attack which bankrupted a popular Bitcoin exchange. To proactively detect the potential for ACIDRain attacks, we extend the theory of weak isolation to analyze latent potential for non-serializable behavior under concurrent web API calls. We introduce a language-agnostic method for detecting potential isolation anomalies in web applications, called Abstract Anomaly Detection (2AD), that uses dynamic traces of database accesses to efficiently reason about the space of possible concurrent interleavings. We apply a prototype 2AD analysis tool to 12 popular self-hosted eCommerce applications written in four languages and deployed on over 2M websites. We identify and verify 22 critical ACIDRain attacks that allow attackers to corrupt store inventory, over-spend gift cards, and steal inventory.</p></div> \r\n            \r\n\t\t\t\r\n            </div>\r\n          "
    #})
    return jsonify({"h":"sdf"})
