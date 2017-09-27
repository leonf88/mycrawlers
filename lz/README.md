1. Use mongodb as the storage, `./data` is the directory. Start mongodb like

    > mongod --dbpath ./data

2. Start the lz spider

    > scrapy crawl lz

3. mongodb usage

    > db.scrapy_items.find({"description": {$regex : ".*story.*"}}, {title:1, download_urls: 1, _id: 0})
    # dump the database as file
    > mongoexport -d lz -c lz -o db.bson
