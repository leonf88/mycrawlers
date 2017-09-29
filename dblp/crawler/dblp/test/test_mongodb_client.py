from ..utils.mongo_client import MongoDBClient
from .. import settings


def test_mongo_client():
    client = MongoDBClient(
        settings.MONGODB_URL,
        settings.MONGODB_DB,
        settings.MONGODB_COLLECTION
    )
    client.open()
    coll = client.get_collection()

    test_recs = [{
        "_key": "article", "_dname": "iiswc2014", "_pname": "iiswc1",
        "_type": "conference", "title": "Processors1", "id": "1"
    }, {
        "_key": "article", "_dname": "iiswc2014", "_pname": "iiswc1",
        "_type": "conference", "title": "Processors2", "id": "2"
    }, {
        "_key": "article", "_dname": "iiswc2015", "_pname": "iiswc1",
        "_type": "conference", "title": "Processors2", "id": "3"
    }, {
        "_key": "article", "_dname": "iiswc2015", "_pname": "iiswc2",
        "_type": "conference", "title": "Processors2", "id": "4"
    }]

    conf_name = set(map(lambda e: e["_pname"], test_recs))
    for name in conf_name:
        client.add_conference_name(name)
        proc_rec = filter(lambda e: e["_pname"] == name, test_recs)
        ids = []
        for rec in proc_rec:
            client.add_conference_proceeding(name, rec["_dname"])
            ids.append(rec["id"])
            client.add_article(rec)
        proc_name = set(map(lambda e: e["_dname"], proc_rec))
        assert len(client.get_conference_proceedings(name)) == len(proc_name)
    assert len(client.get_conference_names()) == len(conf_name)

    client.close()
