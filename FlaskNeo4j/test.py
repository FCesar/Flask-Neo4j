import unittest
import json
from flask import Flask,jsonify,make_response,request
from neo4j.v1 import Transaction
from .flask_neo4j import FlaskNeo4j
from .dao import Dao
from .node import Node

class Test(Node):
	name = ""

class TestDao(Dao):
	def __init__(self,transaction:Transaction):
		super().__init__(transaction)
		self.node = Test
		t:Test = Test(json.loads('{"name":"XPTO"}'))

		t.id = self.count()+1

		self.insert(t)

class TestFlaskNeo4j(unittest.TestCase):
	def setUp(self):
		self.neo4j = FlaskNeo4j(host="bolt://localhost:7687/",user="neo4j",password="neo4jneo4j")
		self.dao = TestDao(self.neo4j.transaction())

	def tearDown(self):
		self.dao.delete()

	def test_a(self):
		t:Test = Test({"id":"1"})
		result = self.dao.find(t)
		self.assertEqual(t.id, result[0].id)
		self.assertEqual("XPTO", result[0].name)

	
		


if __name__ == '__main__':
	unittest.main()