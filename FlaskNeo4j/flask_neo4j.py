import os
import sys
from neo4j.v1 import GraphDatabase, basic_auth, Session, Transaction
from flask import current_app, request, Flask, jsonify,make_response, Response
from flask._compat import reraise, string_types, text_type, integer_types
from pprint import pprint
import json
from werkzeug import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException, InternalServerError, \
     MethodNotAllowed, BadRequest, default_exceptions, NotFound

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class Neo4j(object):
	"""
	Neo4j.

	:param host: Host os conection
	:param user: User os conection
	:param password: Password os conection
	:param app: Flask application
    """
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

	def init_app(self,app:Flask) -> None:
		"""
		Method init_app.
		"""
		self.app = app

		self.handler = {}

		for e in self.app.error_handler_spec:
			for f in self.app.error_handler_spec[e]:
				self.handler[f] = self.app.error_handler_spec[e][f][default_exceptions[f]]
				self.app.error_handler_spec[e][f][default_exceptions[f]] = self.__error

		for e in default_exceptions:
			if e not in self.app.error_handler_spec[None]:
				exc_class, code = self.app._get_exc_class_and_code(e)

				handlers = self.app.error_handler_spec.setdefault(None, {}).setdefault(code, {})
				handlers[exc_class] = self.__error

		self.app.before_request_funcs.setdefault(None, []).append(self.open)

		self.app.after_request_funcs.setdefault(None, []).append(self.close)

		if hasattr(self.app, 'teardown_appcontext'):
			self.app.teardown_appcontext_funcs.append(self.__error)
		else:
			self.app.teardown_request_funcs.append(self.__error)

	
	def transaction(self) -> Transaction:
		"""
		Method transaction.
		"""
		if self._session is None:
			self.open()

		if not self._session.has_transaction():
			self._transaction = self._session.begin_transaction()
			# print("Open Transaction")

		return self._transaction

	def open(self) -> None:
		"""
		Method open.
		"""
		self._session = self.driver.session()
		# print("Open Session")
		self.transaction()

	def close(self,response:Response) -> Response:
		"""
		Method close.
		"""
		if not self._transaction.closed():
			self._transaction.commit()
			# print("Commit Transaction")

		self.__close()

		return response

	def __error(self,exception:Exception) -> None:
		"""
		Method __error.
		"""
		if not self._transaction.closed():
			self._transaction.rollback()
			# print("Rollback Transaction")

		self.__close()

		if not exception is None and exception.code in self.handler :
			return self.handler[exception.code](exception)
		else:
			return exception

	def __close(self) -> None:
		"""
		Method __close.
		"""
		if not self._session.closed():
			self._session.close()
			# print("Close Session")

	def __connect(self) -> None:
		"""
		Method __connect.
		"""
		# print("Open Connection")
		self.driver = GraphDatabase.driver(self._host, auth=basic_auth(self._user,self._password))
		