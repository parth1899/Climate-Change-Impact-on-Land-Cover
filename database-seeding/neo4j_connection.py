from neo4j import GraphDatabase
from config import Config

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(Config.NEO4J_URI, auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD))
    
    def close(self):
        if self.driver is not None:
            self.driver.close()
    
    def query(self, query: str, parameters: dict = None, db: str = "neo4j"):
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return result.data()
