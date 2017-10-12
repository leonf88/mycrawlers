## Crawler for the *Journal of the Software*

增量爬取软件学报文章信息，并生成 json 和 tex 文件。

#### JOSCrawler.py

> dependency: pyquery

    $ sudo apt-get install libxml2-dev
    $ sudo apt-get install libxslt1-dev
    $ sudo pip install pyquery

使用：运行脚本，生成 tex 格式文件，使用 xelatex 创建 PDF 文档（可以使用 Makefile 来生成文档）


