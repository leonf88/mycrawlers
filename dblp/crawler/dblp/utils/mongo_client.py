import pymongo


class MongoDBClient:
    """
    _key: top_list, conferences: [], journals: []
    _key: conf_list, _pname: <conference name>, data: []
    _key: jour_list, _pname: <journal name>, data: []
    _key: conf_proceeding, _pname: <>, _dname: <>, data: []
    _key: jour_volume, _pname: <>, _dname: <>, data: []
    _key: article, _type:<>, _pname: <>, _dname: <>, {}
    """

    def __init__(self, mongo_uri, mongo_db, mongo_coll):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_coll = mongo_coll

    def open(self):
        self._client = pymongo.MongoClient(self.mongo_uri)
        self._db = self._client[self.mongo_db]
        self._collection = self._db[self.mongo_coll]

    def close(self):
        self._client.close()

    def get_collection(self):
        return self._collection

    def add_conference_name(self,  dname):
        self._collection.find_one_and_update(
            {
                "_key": "top_list",
            },
            {"$addToSet": {"conferences": dname}},
            upsert=True
        )

    def add_journal_name(self,  dname):
        self._collection.find_one_and_update(
            {
                "_key": "top_list",
            },
            {"$addToSet": {"journals":  dname}},
            upsert=True
        )

    def _add_sub_header(self, key, dname, title, pname):
        self._collection.find_one_and_update(
            {
                "_key": key,
                "dname": dname
            },
            {"$addToSet": {"data": {"title": title, "pname": pname}}},
            upsert=True
        )

    def add_conference_proceeding_title(self, dname, title, pname):
        self._add_sub_header("conf_list", dname, title, pname)

    def add_journal_volume_title(self, jname, title, pname):
        self._add_sub_header("jour_list", jname, title, pname)

    def add_issue(self, ttype, dname, pname, data):
        self._collection.find_one_and_update(
            {
                "_key": "conf_proceeding",
                "_type": ttype,
                "_dname": dname,
                "_pname": pname
            },
            {"$set": {"data": data}},
            upsert=True
        )

    def add_article(self, data):
        self._collection.find_one_and_update(
            {
                "_key": "article",
                "_type": data["_type"],
                "_pname": data["_pname"],
                "_dname": data["_dname"],
                "title": data["title"]
            },
            {"$set": data},
            upsert=True
        )

    def get_conference_names(self):
        ret = self._collection.find_one({"_key": "top_list"})
        return ret["conferences"]

    def get_journal_names(self):
        ret = self._collection.find_one({"_key": "top_list"})
        return ret["journals"]

    def get_conference_proceedings(self, name):
        ret = self._collection.find_one(
            {"_key": "conf_list", "name": name})
        return ret["data"]

    def get_journal_volume(self, name):
        ret = self._collection.find_one(
            {"_key": "jour_list", "name": name})
        return ret["data"]

    def get_article_by_hook(self, id):
        return self._collection.find_one({"_hook": id})
