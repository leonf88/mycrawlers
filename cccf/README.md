## Crawler for the *Communication of the CCF*

从 2017.02 开始 CCF 更新了新版的计算机学会通讯，该爬虫以不再有效。故而停止维护。 现有的两个爬虫文件可以针对 [老版的 CCCF](http://history.ccf.org.cn/sites/ccf/zgjsjxhtx.jsp) 依然有效。

#### getOneIssue.py

> dependency: pyquery

    $ sudo apt-get install libxml2-dev
    $ sudo apt-get install libxslt1-dev
    $ sudo pip install pyquery

功能：下载特定一期的 CCCF 通讯文集

使用：\[down url\] 为URL为一期通讯集的地址；\[target dirname\] 为存储文档的本地路径名

#### CCCFCrawler.py
 
> dependency: pyquery

功能：获取 CCCF 通讯文集的历年主题和文章列表，并生成 json 格式的文件（例，ccf.json）和 tex 文件

使用：运行脚本，生成 tex 格式文件，使用 xelatex 创建 PDF 文档（可以使用 Makefile 来生成文档）


