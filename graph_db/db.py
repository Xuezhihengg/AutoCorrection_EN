import os
import dotenv
import atexit
from typing import List, Optional, TypedDict
from neo4j import GraphDatabase, Neo4jDriver
from neo4j.exceptions import Neo4jError

dotenv.load_dotenv()
neo4j_url = os.getenv("NEO4J_URI")
neo4j_database = os.getenv("NEO4J_DATABASE")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")


class Neo4jQuery:
    """
    用于与知识图交互的Neo4j客户端
    """

    def __init__(self):
        self.driver: Optional[Neo4jDriver] = None
        self.connect()

    def connect(self):
        """建立与neo4j数据库的连接"""
        try:
            self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_username, neo4j_password))
        except Neo4jError as e:
            print(f"Error connecting to Neo4j: {e}")

    def close(self):
        """关闭neo4j连接"""
        if self.driver:
            self.driver.close()

    def execute_query(self, query: str, parameters: dict = {}) -> List:
        """使用给定参数执行neo4j查询"""
        if not self.driver:
            print("No active Neo4j connection.")
            return []

        with self.driver.session(database=neo4j_database) as session:
            try:
                result = session.run(query, **parameters)
                return result.data()
            except Neo4jError as e:
                print(f"Query execution failed: {e}")
                return []

    def get_top_gc(self) -> List[str]:
        """检索所有顶级语法概念节点"""
        query = """
        MATCH (n:GrammarConcept)
        WHERE n.type = 'top'
        RETURN n.id AS id
        """
        results = self.execute_query(query)
        return [record["id"] for record in results]

    def get_neighbours(self, node_id: str) -> List[str]:
        """通过id检索给定节点的所有相邻节点"""
        query = """
        MATCH (r {id: $node_id})
        MATCH (r)-[r_type]-(n)
        WHERE type(r_type) = 'BELONGS_TO' OR (type(r_type) = 'HAS_SUBCLASS' AND startNode(r_type) = r)
        RETURN n.id AS id
        """
        results = self.execute_query(query, {'node_id': node_id})
        return [record["id"] for record in results]

    def get_labels(self, node_id: str) -> List[str]:
        """通过id检索给定节点的标签"""
        query = """
        MATCH (n {id: $node_id})
        RETURN labels(n) AS node_labels
        """
        results = self.execute_query(query, {'node_id': node_id})
        if results:
            return results[0]["node_labels"]
        return []

    def get_description(self, node_id: str) -> str:
        """通过id检索给定节点的描述"""
        query = """
        MATCH (n {id: $node_id})
        RETURN n.description AS description
        """
        results = self.execute_query(query, {'node_id': node_id})

        return results[0]["description"]

    def get_examples(self, node_id: str) -> List[str]:
        """通过id检索给定Rule节点的所邻接Example节点的细节"""
        query = """
        MATCH (n {id: $node_id})-[:HAS_EXAMPLE]->(r)
        RETURN r.example AS example
        """
        results = self.execute_query(query, {'node_id': node_id})

        if results:
            return [result["example"] for result in results]
        return []


neo4j_query = Neo4jQuery()


def get_top_gc() -> List[str]:
    """
    获取所有顶级语法概念节点
    :return: 所有语法概念节点的列表
    """
    return neo4j_query.get_top_gc()


def get_neighbours(node_id: str) -> List[str]:
    """
    获取特定节点的邻居
    :param node_id: 特定节点的ID
    :return: 节点的邻居列表
    """
    return neo4j_query.get_neighbours(node_id)


def get_labels(node_id: str) -> List[str]:
    """
    获取特定节点的标签
    :param node_id: 特定节点的ID
    :return: 节点的标签
    """
    return neo4j_query.get_labels(node_id)


class NodeDetail(TypedDict):
    description: str
    examples: List[str]


def get_detail(node_id: str) -> NodeDetail:
    """
    获取指定id节点（该节点应为Rule类型）的细节信息，包括其描述和例子
    :param node_id: 指定节点的id
    :return: NodeDetail对象，包含“description”键与“examples”键
    """
    assert "Rule" in neo4j_query.get_labels(node_id), "get_detail方法的作用对象应为Rule类型节点"
    description = neo4j_query.get_description(node_id)
    examples = neo4j_query.get_examples(node_id)
    return {"description": description, "examples": examples}


__all__ = [
    "get_top_gc", "get_neighbours", "get_labels", "get_detail", "NodeDetail"
]

atexit.register(neo4j_query.close)
