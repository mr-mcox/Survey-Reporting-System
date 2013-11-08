from behave import *
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from ResultsRetriever import ResultsRetriever

def table_for_db(table):
	db_formatted_table = [dict([(header,int(row[header])) for header in table.headings]) for row in table]
	return db_formatted_table

@given('a results table with this data')
def step(context):
	engine = create_engine('sqlite:///:memory:')
	metadata = MetaData()
	results = Table('results',metadata,
					Column('respondent_id', Integer),
					Column('survey_id', Integer),
					Column('question_id', Integer),
					Column('response', Integer))
	metadata.create_all(engine)

	conn = engine.connect()
	conn.execute(results.insert(),table_for_db(context.table))
	context.db = conn

@when('retrieve results for survey_id 1 is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_one_survey(survey_id=1)
	#conn.execute("SELECT * FROM results WHERE survey_id = 1").fetchall()

@then('there are 8 rows returned')
def step(context):
	print(context.results)
	assert len(context.results)==8