from typing import Dict

# Classes
class ESQueryBuilder:

    class Const:
        DEFAULT_PAGE_SIZE = 25

    def __init__(self):
        self.query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "_source": [],
            "sort": [],
            "from": 0,
            "size": self.Const.DEFAULT_PAGE_SIZE,

        }

    def add_match(self, field, value):
        match_query = {
            "match": {
                field: value
            }
        }
        self.query["query"]["bool"]["must"].append(match_query)

    def add_term(self, field, value):
        term_query = {
            "term": {
                field: value
            }
        }
        self.query["query"]["bool"]["must"].append(term_query)

    def add_wildcard(self, field, value):
        term_query = {
            "wildcard": {
                field: {
                    "value": "*" + value + "*",
                    "case_insensitive": True
                }
            }
        }
        self.query["query"]["bool"]["must"].append(term_query)

    def set_retrieve_id_only(self):
        self.query["_source"] = False

    def add_return_field(self, field):
        if not self.query["_source"]: self.query["_source"] = []
        self.query["_source"].append(field)

    def build(self):
        return self.query
    
class ESQueryResponse:

    def __init__(self, response: Dict):
        self.timed_out      = (bool)    (response.get("timed_out", False))
        self.time_taken     = (int)     (response.get("took", 0))
        self.count          = (int)     (response["hits"]["total"]["value"])
        self.hits           =           response["hits"]["hits"]
