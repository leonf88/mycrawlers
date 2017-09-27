import pymongo


class MongoDBClient:

    def __init__(self, mongo_uri, mongo_db, mongo_coll):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_coll = mongo_coll

    def open(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close(self):
        self.client.close()

    def get_max_by_field(self, field):
        return self.db[self.mongo_coll].find_one(
            sort=[(field, pymongo.DESCENDING)])[field]


if __name__ == '__main__':
    mongo_uri = "mongodb://localhost:27018/"
    mongo_db = "lz"
    mongo_coll = "lz"
    client = MongoDBClient(mongo_uri, mongo_db, mongo_coll)
    client.open()
    print client.get_max_by_field("update_time") > "2017-09-11"
    # ret = client.db[mongo_coll].delete_many(
    #     {"update_time": "2017-09-26"}
    # )
    print ret.deleted_count
    print client.get_max_by_field("update_time")
    client.close()
