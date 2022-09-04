import os
import pickle
import json
import logging
import unittest
import requests

from trapi_model.query import Query
LOCAL_URL = 'http://localhost:8000'
#LOCAL_URL = 'http://localhost:80'
#LOCAL_URL = 'http://chp-dev.thayer.dartmouth.edu'

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

class TestChpLearn(unittest.TestCase):
    def setUp(self):
        self.query_endpoint = '/query/'
        self.curies_endpoint = '/curies/'
        self.meta_knowledge_graph_endpoint = '/meta_knowledge_graph/'

    @staticmethod
    def _get(url, params=None):
        params = params or {}
        res = requests.get(url, json=params)
        print(res.content)
        ret = res.json()
        return ret

    @staticmethod
    def _post(url, params):
        res = requests.post(url, json=params)
        if res.status_code != 200:
            return res, res.status_code
        else:
            ret = res.json()
            return ret, res.status_code

    @staticmethod
    def _strip_query(query):
        q_dict = query.to_dict()
        return {key: value for key, value in q_dict.items() if key == 'message'}

    @staticmethod
    def _print_query(query):
        print(json.dumps(query, indent=2))

    def test_curies(self):
        url = LOCAL_URL + self.curies_endpoint
        resp = self._get(url)

    def test_meta_knowledge_graph(self):
        url = LOCAL_URL + self.meta_knowledge_graph_endpoint
        resp = self._get(url)

    def test_gene_to_pathway_wildcard(self):
        with open(os.path.join(MODULE_DIR, 'test_queries.json'), 'rb') as f_:
            queries = json.load(f_)
        for query in queries:
            url = LOCAL_URL + self.query_endpoint
            resp, status = self._post(url, query)
            self._print_query(resp)

if __name__ == '__main__':
    unittest.main()
