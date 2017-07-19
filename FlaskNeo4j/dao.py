from neo4j.v1 import Transaction

from .node import Node
from .edge import Edge

class Dao(object):
	node:Node = None

	edge:Edge = []

	def __init__(self,transaction:Transaction):
		self.transaction=transaction

	def __query(self,cypher_query=""):
		if not cypher_query:
			return None

		r = []
		print(cypher_query)
		for record in self.transaction.run(cypher_query):
			r.append(record)

		return r

	def __nodeName(self):
		return self.node.__name__

	def __edgeName(self,edge:Edge):
		if edge in self.edge:
			return self.edge[self.edge.index(edge)]

	def __convert(self,node:Node, insert = True):
		list = []

		if node is None:
			return ""

		for key,value in node.__dict__.items():
			if insert :
				list.append("%s:'%s'" % (key ,value))
			else:
				list.append("n.%s='%s'" % (key, value))
		
		return ",".join(list)

	def count(self):

		query = "MATCH (n:"+self.__nodeName()+") WHERE 1=1 RETURN count(n)"

		result = self.__query(query)

		if not result is None:
			result =  result[0]["count(n)"]
		else:
			result = 0
		
		return result


	def find(self, node:Node = None, where = "1=1"):
		result = []
		
		query = "MATCH (n:%s {%s}) WHERE %s RETURN n" % (self.__nodeName(),self.__convert(node),where)

		for r in self.__query(query):
			if not r is None:
				result.append(self.node(r["n"].properties))
		
		return result 

	def insert(self, node:Node):
		result = []
		
		query = "CREATE (n:"+self.__nodeName()+" {"+ self.__convert(node)+"}) RETURN n"

		for r in self.__query(query):
			if not r is None:
				result.append(self.node(r["n"].properties))

		return result[0] 

	def update(self, node:Node):
		result = []
		
		query = "MATCH (n:"+self.__nodeName()+") WHERE n.id = '"+node.id+"' SET "+self.__convert(node,False)+" RETURN n"

		for r in self.__query(query):
			if not r is None:
				result.append(self.node(r["n"].properties))
		
		return result[0]

	def delete(self, id:str = None, where = "1=1"):
		condition = "n.id = '%s'" % (str(id)) if id != None else where

		result = []
		
		query = "MATCH (n:"+self.__nodeName()+") WHERE "+condition+" DELETE n"
		
		for r in self.__query(query):
			if not r is None:
				result.append(r["n"].properties)
		else:
			return result
		
		return result[0]

	def insertEdge(self, nodeA:Node, nodeB:Node, edge:Edge, whereA = "1=1", whereB = "1=1"):
		result = []

		query = "MATCH (a:%s),(b:%s) WHERE %s AND %s CREATE (a)-[e:%s]->(b) RETURN e" % (type(nodeA).__name__,type(nodeB).__name__,whereA,whereB,type(edge).__name__) 

		for r in self.__query(query):
			if not r is None:
				result.append(self.__edgeName(type(edge))(r["e"].properties))
		
		return result[0]
		