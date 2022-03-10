from django.db.models import QuerySet
from enum import Enum
from collections import defaultdict
import os

from trapi_model.logger import Logger as TrapiLogger
from trapi_model.message import Message
from trapi_model.query_graph import QEdge, QueryGraph
from trapi_model.biolink.constants import *
from trapi_model.query_graph import QNode
from trapi_model.query import Query
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph
from trapi_model.knowledge_graph import KEdge, KnowledgeGraph
from trapi_model.results import Result, Results, Binding
from trapi_model.message import Message
from chp_utils.curie_database import CurieDatabase
from chp_utils.conflation import ConflationMap
from chp_data.LookUpDataHandler import DataHandler

from .trapi_exceptions import *
from .models import GeneToPathway, PathwayToGene

class QueryType(Enum):
    PATHWAY_TO_GENE_WILDCARD = 1
    GENE_TO_PATHWAY_WILDCARD = 2

class QueryIdentifier:
    @staticmethod
    def _isPathwayToGeneWildcardQuery(query_graph:QueryGraph)->bool:
        """
        Identifies if a query is a pathway to gene query
        """
        pathway_nodes_ids = query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
        gene_nodes_ids = query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])

        if pathway_nodes_ids is None:
            return False
        if gene_nodes_ids is None:
            return False
        if len(pathway_nodes_ids) != 1:
            return False
        if len(gene_nodes_ids) != 1:
            return False
        
        #check edge
        edges = query_graph.edges

        if len(edges) != 1:
            return False
        id = list(edges.keys())[0]
        edge = edges.get(id)
        
        #check predicate
        predicates = edge.predicates
        if len(predicates) != 1:
            return False
        predicate = predicates[0]
        predicate = predicate.passed_name

        if predicate != 'biolink:has_participant':
            return False

        #return True if all is swell
        return True
    @staticmethod
    def _isGeneToPathwayWildcardQuery(query_graph:QueryGraph)->bool:
        """
        Identifies if a query is a gene to pathway query
        """
        #check genes
        pathway_nodes_ids = query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
        gene_nodes_ids = query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
        
        if pathway_nodes_ids is None:
            return False
        if gene_nodes_ids is None:
            return False
        if len(pathway_nodes_ids) != 1:
            return False
        if len(gene_nodes_ids) != 1:
            return False
        
        #check edge
        edges = query_graph.edges

        if len(edges) != 1:
            return False
        id = list(edges.keys())[0]
        edge = edges.get(id)
        
        #check predicate
        predicates = edge.predicates
        if len(predicates) != 1:
            return False
        predicate = predicates[0]
        predicate = predicate.passed_name

        if predicate != 'biolink:participates_in':
            return False

        #return True if all is swell
        return True
    @staticmethod
    def getQueryType(query_graph:QueryGraph) -> QueryType:
        if QueryIdentifier._isPathwayToGeneWildcardQuery(query_graph):
            query_type:QueryType = QueryType.PATHWAY_TO_GENE_WILDCARD
        elif QueryIdentifier._isGeneToPathwayWildcardQuery(query_graph):
            query_type:QueryType = QueryType.GENE_TO_PATHWAY_WILDCARD
        else:
            raise UnidentifiedQueryType
        return query_type

class TrapiInterface:
    def __init__(self,
                 trapi_version='1.2',
                ):
        self.trapi_version = trapi_version
        # Get base handler for processing curies and meta kg requests
        self._get_curies()
        self.meta_knowledge_graph = self._get_meta_knowledge_graph()
        self.conflation_map = self._get_conflation_map()

        # Initialize interface level logger
        self.logger = TrapiLogger()
    
    def query_database(self, identified_query_tuple) -> Query:
        query_identifier:QueryIdentifier = identified_query_tuple[0]
        identified_query:Query = identified_query_tuple[1]
        database_results:QuerySet
        subject_node_curie = None
        if query_identifier == QueryType.GENE_TO_PATHWAY_WILDCARD:
            subject_node_ids = identified_query.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
            subject_node_id = subject_node_ids[0]
            subject_node:QNode = identified_query.message.query_graph.nodes[subject_node_id]
            subject_node_curie = subject_node.ids[0]
            database_results:QuerySet = GeneToPathway.objects.all().filter(gene_curie=subject_node_curie)            
        elif query_identifier ==  QueryType.PATHWAY_TO_GENE_WILDCARD:
            print('pathway query identified')
            subject_node_ids:list = identified_query.message.query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
            subject_node_id = subject_node_ids[0]
            subject_node:QNode = identified_query.message.query_graph.nodes[subject_node_id]
            subject_node_curie = subject_node.ids[0]
            database_results:QuerySet = PathwayToGene.objects.all().filter(pathway_curie=subject_node_curie) 
        query_response = self._build_response(query_identifier, identified_query,database_results)
        return query_response    

    def _build_response(self, query_type:QueryIdentifier,identified_query:Query, database_results:QuerySet):
        knowledge_graph = identified_query.message.knowledge_graph
        query_graph = identified_query.message.query_graph
        results = identified_query.message.results
        node_bindings = {}
        edge_bindings = {}
        
        wildcard_id:str
        wildcard_qnode:QNode
        
        specified_qnode:QNode
        specified_qnode_id:str
        
        qnode:QNode 
        qnode_key:str
        for qnode_key, qnode in query_graph.nodes.items():
            if qnode.ids is not None:
                specified_qnode = qnode
                specified_qnode_id = qnode.ids[0]
                name:str = self.curies_db.to_dict()[specified_qnode.categories[0].get_curie()][specified_qnode.ids[0]][0]
                knode_key:str = knowledge_graph.add_node(specified_qnode_id, name, specified_qnode.categories[0].get_curie())
                node_bindings.update({qnode_key: [knode_key]})
            else:
                wildcard_id = qnode_key
                wildcard_qnode = qnode
        qedge_key:str
        qedge:QEdge
        for qedge_key, qedge in query_graph.edges.items():
            pathway_count = 1
            for database_result in database_results:
                result_curie:str
                p_value:float
                if query_type == QueryType.GENE_TO_PATHWAY_WILDCARD:
                    result_curie = database_result.pathway_curie
                elif query_type == QueryType.PATHWAY_TO_GENE_WILDCARD:
                    result_curie = database_result.gene_curie
                p_value = database_result.p_value
                pathway_count:int = pathway_count + 1
                knode_key:str = knowledge_graph.add_node(result_curie, result_curie, wildcard_qnode.categories[0].get_curie())
                name:str = self.curies_db.to_dict()[wildcard_qnode.categories[0].get_curie()][result_curie][0]
                knode_key = knowledge_graph.add_node(
                            result_curie,
                            name,
                            qnode.categories[0].get_curie(),
                            )
                node_bindings.update({wildcard_id: [knode_key]})
                kedge_key = knowledge_graph.add_edge(
                        node_bindings[qedge.subject][0],
                        node_bindings[qedge.object][0],
                        predicate=qedge.predicates[0].get_curie()
                        )
                kedge:KEdge = knowledge_graph.edges[kedge_key]
                kedge.add_attribute(
                    attribute_type_id = 'P-Value',
                    value = p_value,
                    value_type_id = "biolink:has_p_value",
                )
                kedge.add_attribute(
                    attribute_type_id = 'biolink:aggregator_knowledge_source',
                    value = "infores:connections-hypothesis",
                    value_type_id = "biolink:InformationResource",
                    attribute_source = "infores:connections-hypothesis",
                    value_url = "http://chp.thayer.dartmouth.edu",
                    description = "The Connections Hypothesis Provider from NCATS Translator."

                )        
                kedge.add_attribute(
                    attribute_type_id = 'biolink:aggregator_knowledge_source',
                    value = 'infores:reactome',
                    value_type_id = "biolink:InformationResource",
                    value_url = 'https://reactome.org/',
                    attribute_source = "infores:connections-hypothesis",
                    description = 'Reactome is an open-source, open access, manually curated and peer-reviewed pathway database.'
                    )
                edge_bindings.update({qedge_key: [kedge_key]})
                results.add_result(node_bindings, edge_bindings)
        return identified_query

    def identify_queries(self, trapi_query:Query) -> tuple:
        # Setup messages
        identified_queries_tuple = self._identify_queries(trapi_query)
        return identified_queries_tuple

    def _identify_queries(self, query:Query) -> list:
        try:
            message_type = self._determine_message_type(query.message)
            identified_query_tuple = (message_type,query)
        except Exception as ex:
            self.logger.debug(f'Lookup Service could not processes derived query. {str(ex)}. Derived Query graph: {query.message.query_graph.to_dict()}')
        #check if any queryies where setup/processed
        if identified_query_tuple is None:
            raise NoSupportedQueriesFound
        return identified_query_tuple

    def _determine_message_type(self, message: Message):
        if message is None:
            raise UnidentifiedQueryType
        
        query_graph:QueryGraph = message.query_graph

        query_type:QueryType = QueryIdentifier.getQueryType(query_graph=query_graph)

        return query_type

    def _get_meta_knowledge_graph(self) -> MetaKnowledgeGraph:
        """
        Returns the meta knowledge graph for this app
        """
        return MetaKnowledgeGraph.load(
            self.trapi_version,
            None,
            filename=DataHandler.getMetaKnowledgeGraph()
        )

    def get_meta_knowledge_graph(self) -> MetaKnowledgeGraph:
        return self.meta_knowledge_graph

    def _get_curies(self) -> CurieDatabase:
        self.curies_db = CurieDatabase(curies_filename=DataHandler.getAllCuriesMap())

    def get_curies(self) -> CurieDatabase:
        self._get_curies()
        return self.curies_db
    
    def _get_conflation_map(self) -> ConflationMap:
        dir = os.path.dirname(os.path.realpath(__file__))
        return ConflationMap(conflation_map_filename=DataHandler.getConflationMap())

    def get_conflation_map(self) -> ConflationMap:
        return self.conflation_map



