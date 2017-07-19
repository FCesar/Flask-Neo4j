import unittest
import json
from flask import Flask,jsonify,make_response,request
from neo4j.v1 import Transaction
from example import app, TestDao, Test

class TestFlaskNeo4j(unittest.TestCase):
	def setUp(self):
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
		self.response = self.app.get('/count')
		self.assertEqual(int(self.response.data), 1)
		self.assertTrue(isinstance(int(self.response.data), int))
		self.assertIn('application/json', self.response.content_type)

	def test_f(self):
		self.response = self.app.delete('/1')
		self.assertEqual(200, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

	def test_g(self):
		self.response = self.app.get('/1')
		self.assertEqual(404, self.response.status_code)
		self.assertIn('application/json', self.response.content_type)

if __name__ == '__main__':
	unittest.main()