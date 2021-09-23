from trapi_model.logger import Logger as TrapiLogger
from trapi_model.message import Message
from trapi_model.query_graph import QueryGraph
from trapi_model.biolink.constants import *
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph
from trapi_model.knowledge_graph import KnowledgeGraph

from chp_utils.curie_database import CurieDatabase
from chp_utils.conflation import ConflationMap

from exceptions import *
from enum import Enum
from .trapi_interface import QueryType
from collections import defaultdict

from models import GeneToPathway, PathwayToGene

class QueryType(Enum):
    PATHWAY_TO_GENE_WILDCARD = 1
    GENE_TO_PATHWAY_WILDCARD = 2

class QueryIdentifier:

    def _isPathwayToGeneWildcardQuery(self, query_graph:QueryGraph)->bool:
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
        edges = query_graph.message.query_graph.edges

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

    def _isGeneToPathwayWildcardQuery(self, query_graph:QueryGraph)->bool:
        """
        Identifies if a query is a gene to pathway query
        """
        #check genes
        pathway_nodes_ids = query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
        gene_nodes_ids = query_graph.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
        
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
          
    def getQueryType(self, query_graph:QueryGraph) -> QueryType:
        if self._isPathwayToGeneWildcardQuery(query_graph):
            query_type:QueryType = QueryType.PATHWAY_TO_GENE_WILDCARD
        elif self._isGeneToPathwayWildcardQuery(query_graph):
            query_type:QueryType = QueryType.GENE_TO_PATHWAY_WILDCARD
        else:
            raise UnidentifiedQueryType
        return query_type

class TrapiInterface:
    def __init__(self,
                 trapi_version='1.1',
                ):
        self.trapi_version = trapi_version

        # Get base handler for processing curies and meta kg requests
        self.curies_db = self._get_curies()
        self.curies = self.curies_db.curies
        self.meta_knowledge_graph = self._get_meta_knowledge_graph()
        self.conflation_map = self._get_conflation_map()

        # Initialize interface level logger
        self.logger = TrapiLogger()

    def query_database(self, model_to_query_dict):
        return_dict = {}
        
        for query_type in model_to_query_dict.keys():
            queries_for_database = model_to_query_dict[query_type]
            database_results = None
            subject_node_curie = None
            for query in queries_for_database:
                if query_type == QueryType.GENE_TO_PATHWAY_WILDCARD:
                    gene_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
                    subject_node_curie = gene_nodes_ids[0]
                    database_results = GeneToPathway.objects.get(gene__exact=subject_node_curie).get_result()
                elif query_type==  QueryType.PATHWAY_TO_GENE_WILDCARD:
                    pathway_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
                    subject_node_curie = pathway_nodes_ids[0]
                    database_results = PathwayToGene.objects.get(pathway__exact=subject_node_curie)
                trapi_response = self._build_results(subject_node_curie, database_results, query_type)
                return_dict.update({query:trapi_response})
        return return_dict    

    def _build_results(subject_curie, object_curies, query_type):
        if query_type == GeneToPathway:
            knowledge_graph = KnowledgeGraph()
            knowledge_graph.add_node(curie=subject_curie, categories="biolink:Gene", name=subject_curie)
            
            pathway_count = 1
            for pathway in object_curies:
                pathway_count = pathway_count + 1
                knowledge_graph.add_node(curie=pathway, categories="biolink:Pathway", name=pathway)
                knowledge_graph.add_edge(k_subject='n0', k_object="n{}".format(pathway_count), predicate="biolink:participates_in")
            return knowledge_graph.to_dict()

        elif query_type == PathwayToGene:
            knowledge_graph = KnowledgeGraph()
            knowledge_graph.add_node(curie=subject_curie, categories="biolink:Pathway", name=subject_curie)
            
            pathway_count = 1
            for gene in object_curies:
                pathway_count = pathway_count + 1
                knowledge_graph.add_node(curie=gene, categories="biolink:Gene", name=gene)
                knowledge_graph.add_edge(k_subject='n0', k_object="n{}".format(pathway_count), predicate="biolink:participates_in")
        
            return knowledge_graph.to_dict()

    # def contert_to_models(self, identified_queries) -> dict:

    #     return_dict = {}

    #     for query_type in identified_queries.keys():
    #         typed_queries = identified_queries[query_type] 
    #         model = None
    #         if query_type == QueryType.PathwayToGene:
    #             model = PathwayToGene()
    #         elif query_type == QueryType.GeneToPathway:
    #             model = GeneToPathway()

    #         if model is not None:
    #             return_dict.update({model:typed_queries})
            
    #     return return_dict

    def identify_queries(self, trapi_queries) -> dict:
        # Setup messages
        self.queries_dict = self._identify_queries(trapi_queries)

    def _identify_queries(self, queries) -> None:
        queries_dict = defaultdict(list)
        for query in queries:
            try:
                message_type = self._determine_message_type(query.message)
                queries_dict[message_type].append(query)
            except Exception as ex:
                self.logger.debug(f'Lookup Service could not processes derived query. {str(ex)}. Derived Query graph: {query.message.query_graph.to_dict()}')
        #check if any queryies where setup/processed
        if len(queries_dict) == 0:
            raise NoSupportedQueriesFound

    def _determine_message_type(self, message: Message):
        if message is None:
            raise UnidentifiedQueryType
        
        query_graph:QueryGraph = message.query_graph

        query_type:QueryType = QueryIdentifier.getQueryType(query_graph)

        return query_type

    def _get_meta_knowledge_graph(self) -> MetaKnowledgeGraph:
        """
        Returns the meta knowledge graph for this app
        """

        return MetaKnowledgeGraph.load(
            self.trapi_version,
            None,
            filename="metakg.json"
        )

    def get_meta_knowledge_graph(self) -> MetaKnowledgeGraph:
        return self.meta_knowledge_graph

    def _get_curies(self) -> CurieDatabase:
        curies_db = CurieDatabase(curies_filename="./data-to-import/all_curies_map.json")
        return curies_db

    def get_curies(self) -> CurieDatabase:
        return self.curies_db
    
    def _get_conflation_map(self) -> ConflationMap:
        return ConflationMap(conflation_map_filename="data-to-import")

    def get_conflation_map(self) -> ConflationMap:
        return self.conflation_map



