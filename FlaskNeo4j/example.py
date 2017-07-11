import json
from flask import Flask,jsonify,make_response,request, abort
from neo4j.v1 import Transaction
from .flask_neo4j import Neo4j
from .dao import Dao
from .node import Node

class Test(Node):
	name = ""

class TestDao(Dao):
	def __init__(self,transaction:Transaction):
		super().__init__(transaction)
		self.node = Test

app = Flask(__name__)
app.debug = False



neo4j = Neo4j(app=app,host="bolt://localhost:7687/",user="neo4j",password="neo4jneo4j")

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
		abort(404)
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

@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(505)
def not_foundddd(error):
    return jsonify(message=str(error)), error.code

if __name__ == '__main__':
	app.run()