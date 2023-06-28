import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError

class Neo4jConnector:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.driver = None
        return cls._instance

    def __init__(self):
        if self.driver is None:
            
            load_dotenv()  # Load the environment variables from the .env file
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_username = os.getenv("NEO4J_USERNAME")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            self.logger = logging.getLogger(__name__)
            self._connect(neo4j_uri, neo4j_username,neo4j_password)

    def _connect(self,neo4j_uri, neo4j_username,neo4j_password):
        if self.driver is None:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=basic_auth(neo4j_username, neo4j_password))
            self.logger.info("Connected to Neo4j database.")

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.logger.info("Closed connection to Neo4j database.")

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            self.logger.debug("Executing query: %s", query)
            try:
                result = session.run(query, parameters)
                data = result.single()
                return data
            except Neo4jError as e:
                self.logger.error("An error occurred during query execution: %s", str(e))
                raise
            
    def create_node(self, query, parameters):
        try:
            result = self.execute_query(query, parameters)
            return result['node_id']
        except KeyError:
            self.logger.error("Node creation failed. Unexpected response from Neo4j.")
            raise
        except Neo4jError as e:
            self.logger.error("An error occurred during node creation: %s", str(e))
            raise
    
            
    def create_relationship(self, node1_id, node2_id, relationship_type):
        query = f"""
        MATCH (n1), (n2)
        WHERE ID(n1) = $node1_id AND ID(n2) = $node2_id
        MERGE (n1)-[r:{relationship_type}]->(n2)
        ON CREATE SET r.created_at = timestamp()
        RETURN r
        """
        try:
            result = self.execute_query(
                query, parameters={"node1_id": node1_id, "node2_id": node2_id}
            )
            return result["r"]
        except KeyError:
            self.logger.error("Relationship creation failed. Unexpected response from Neo4j.")
            raise
        except Neo4jError as e:
            self.logger.error("An error occurred during relationship creation: %s", str(e))
            raise
    
    def create_index(self, label, property_key):
        with self.driver.session() as session:
            session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{property_key})")

    def create_constraint(self, label, property_key):
        with self.driver.session() as session:
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property_key} IS UNIQUE")