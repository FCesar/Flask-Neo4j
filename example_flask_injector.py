from flask import Flask, Config,jsonify
from flask.views import View,MethodView
from flask_injector import FlaskInjector,request
from injector import inject,Module,provider,singleton,Injector
from neo4j.v1 import GraphDatabase, basic_auth, Session, Transaction
from FlaskNeo4j.flask_neo4j import Neo4j
from FlaskNeo4j.dao import Dao
from FlaskNeo4j.node import Node
import json

class Test(Node):
	name = ""

class TestDao(Dao):
	def __init__(self,transaction:Transaction):
		super().__init__(transaction)
		self.node = Test
		t:Test = Test(json.loads('{"name":"XPTO"}'))

		t.id = self.count()+1

		self.insert(t)

	def __del__(self):
		self.delete()

class Neo4jModule(Module):
	@provider
	@singleton
	def provide_ext(self, app: Flask) -> Neo4j:
		return Neo4j(app=app,host="bolt://localhost:7687/",user="neo4j",password="neo4jneo4j")

class Neo4jTransactionModule(Module):
	@provider
	@request
	def provide_ext(self, neo4j: Neo4j) -> Transaction:
		return neo4j.transaction()

# Class-based view with injected constructor
class TesteView(MethodView):
	@inject
	def __init__(self, t:Transaction):
		self.t:Transaction = t

	def get(self):
		dao:Dao = TestDao(self.t)

		r = dao.find()
		
		list = [ob.json() for ob in r]

		return jsonify(list), 200

if __name__ == '__main__':
	app = Flask(__name__)
	app.debug = True

	@app.route("/test")
	def test(t:Transaction):
		dao:Dao = TestDao(t)

		r = dao.find()
		
		list = [ob.json() for ob in r]

		return jsonify(list), 200

	app.add_url_rule('/TestView', view_func=TesteView.as_view('TesteView'),methods=['GET'])

	FlaskInjector(app=app, modules=[Neo4jModule,Neo4jTransactionModule])

	app.run()