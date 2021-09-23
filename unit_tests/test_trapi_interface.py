import unittest
import json
from trapi_model.query_graph import QueryGraph
from lookup_app.trapi_interface import TrapiInterface
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph

class TestTrapiInterface(unittest.TestCase):
    def setupClass(cls):
        super(TestTrapiInterface, cls).setUpClass()

    def test_curies(self):
        interface = TrapiInterface(trapi_version='1.1')
        curies = interface.get_curies()
        self.assertIsInstance(curies, dict)

    def test_meta_knowledge_graph(self):
        interface = TrapiInterface(trapi_version='1.1')
        meta_kg = interface.get_meta_knowledge_graph()
        self.assertIsInstance(meta_kg, MetaKnowledgeGraph)

    def test_get_response(self):
        interface = TrapiInterface(trapi_version='1.1')
        queryfile = "gene_to_pathway_wildcard.json"
        query_json = None
        with open(queryfile, 'r') as infile:
            query_json = json.load(infile)
        
        query_graph = QueryGraph(query_json)
        identified_queries_dict = self.test_identify_queries(query_graph)

    def test_identify_queries(self, trapi_interface:TrapiInterface, query_graph:QueryGraph):
        identified_queries_dict = trapi_interface.identify_queries(query_graph)
        self.assertIsInstance(identified_queries_dict)
        return identified_queries_dict
