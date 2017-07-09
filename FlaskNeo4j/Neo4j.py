from neo4j.v1 import GraphDatabase, basic_auth, Session, Transaction
from flask import current_app, request, Flask, jsonify,make_response

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class Neo4j(object):

	def __init__(self,host:str,user:str,password:str,app:Flask=None) -> None:
		self._host:str = host
		self._user:str = user
		self._password:str = password

		self._session:Session = None
		self._driver = None
		self._transaction:Transaction = None

		if self._driver is None:
			self.__connect()

		if app is not None:
			self.init_app(app)

	def init_app(self,app):
		self.app = app

		self.app.before_request_funcs.setdefault(None, []).append(self.open)

		self.app.after_request_funcs.setdefault(None, []).append(self.close)

		if hasattr(self.app, 'teardown_appcontext'):
			self.app.teardown_appcontext_funcs.append(self.error)
		else:
			self.app.teardown_request_funcs.append(self.error)

	def transaction(self):
		if self._session is None:
			self.open()

		if not self._session.has_transaction():
			self._transaction = self._session.begin_transaction()
			# print("Open Transaction")

		return self._transaction

	def open(self):
		self._session = self.driver.session()
		# print("Open Session")
		self.transaction()

	def close(self,response):
		if not self._transaction.closed():
			self._transaction.commit()
			# print("Commit Transaction")

		self.__close()

		return response

	def error(self,exception):
		if not self._transaction.closed():
			self._transaction.rollback()
			# print("Rollback Transaction")

		self.__close()

	def __close(self):
		if not self._session.closed():
			self._session.close()
			# print("Close Session")

	def __connect(self):
		# print("Open Connection")
		self.driver = GraphDatabase.driver(self._host, auth=basic_auth(self._user,self._password))
		