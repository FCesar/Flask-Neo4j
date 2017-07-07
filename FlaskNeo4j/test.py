import unittest
import json
from Neo4j import Neo4j
from flask import Flask,jsonify,make_response,request
from neo4j.v1 import Transaction
from Neo4j import Neo4j
from Dao import Dao
from Node import Node

class Test(Node):
	name = ""

class TestDao(Dao):
	def __init__(self,transaction:Transaction):
		super().__init__(transaction)
		self.node = Test

class TestFlaskNeo4j(unittest.TestCase):
	def setUp(self):
		app = Flask(__name__)

		neo4j = Neo4j(app=app,host="http://localhost:7474/db/data/",user="neo4j",password="neo4j")

		@app.route('/',methods=['GET'])
		def get():
			dao:Dao = TestDao(neo4j.transaction())

			r = dao.find()
			
			list = [ob.__dict__ for ob in r]

			return jsonify(list), 200

		@app.route('/<int:id>',methods=['GET'])
		def getId(id:int=None):
			dao:Dao = TestDao(neo4j.transaction())

			r = dao.find(id)

			if len(r) == 0:
				return jsonify(r), 200
			else:
				return jsonify(r[0].json()), 200
			

		@app.route('/',methods=['POST'])
		def post():
			dao:Dao = TestDao(neo4j.transaction())

			t:Test = Test(json.loads(request.data))

			t.id = dao.count()+1

			r = dao.insert(t)

			return jsonify(r.json()), 201

		@app.route('/',methods=['PUT'])
		def put():
			dao:Dao = TestDao(neo4j.transaction())

			r = dao.update(Test(json.loads(request.data)))

			return jsonify(r.json()), 200

		@app.route('/<int:id>',methods=['DELETE'])
		def delete(id:int=None):
			dao:Dao = TestDao(neo4j.transaction())

			r = dao.delete(id)

			return jsonify(r), 200

		@app.route('/count',methods=['GET'])
		def count():
			dao:Dao = TestDao(neo4j.transaction())

			r = dao.count()

			return jsonify(r), 200

		self.app = app.test_client()
		
	
	def test_a(self):
		self.response = self.app.post('/',data='{"name":"XPTO"}')
		self.assertTrue(isinstance(TestDao(self.response.data),TestDao))
		self.assertEqual(201, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_b(self):
		self.response = self.app.get('/')
		self.assertEqual(200, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_c(self):
		self.response = self.app.get('/1')
		self.assertTrue(isinstance(TestDao(self.response.data),TestDao))
		self.assertEqual(200, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_d(self):
		self.response = self.app.put('/',data='{"id":"1", "name":"XPTO4"}')
		self.assertTrue(isinstance(TestDao(self.response.data),TestDao))
		self.assertEqual(200, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_e(self):
		self.response = self.app.delete('/1')
		self.assertEqual(200, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_f(self):
		self.response = self.app.get('/count')
		self.assertEqual(int(self.response.data), 0)
		self.assertTrue(isinstance(int(self.response.data), int))
		self.assertIn('application/json', self.response.content_type)

	
		

	


if __name__ == '__main__':
	unittest.main()