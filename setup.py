from setuptools import setup

setup(
	name='FlaskNeo4j',
	version='1.0.0',
	description='Easy integration between Flask and Neo4j',
	url='http://github.com/FCesar/FlaskNeo4j',
	author='FCesar',
	author_email='fcgpsjob@gmail.com',
	license='MIT',
	packages=['FlaskNeo4j'],
	install_requires=[
		'Flask','neo4j-driver>=1.3.0'
	],
	zip_safe=False
)	