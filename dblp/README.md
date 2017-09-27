1. Use mongodb as the storage, `./data` is the directory. Start mongodb like

    ```
    mongod --dbpath ./data
    ```

2. Start the dblp spider

    ```
    scrapy crawl dblp
    ```

3. mongodb usage

    ```
    db.dblp.find({"title": {$regex : ".*Bitcoin.*"}})
    db.dblp.find({"title": {$regex : ".*Bitcoin.*"}}, {title:1, author: 1, _id: 0})
    # dump the database as file
    mongoexport -d dblp -c dblp -o dblp.bson
    ```

4. Start web

    ```
    cnpm start
    ```
