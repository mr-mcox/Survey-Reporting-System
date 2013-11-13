from behave import *
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from ResultsRetriever import ResultsRetriever

def table_for_db(table):
	db_formatted_table = list()
	for row in table:
		row_dict = dict()
		for header in table.headings:
			value = row[header]
			try:
				value = int(value)
			except:
				pass
			row_dict[header] = value
		db_formatted_table.append(row_dict)
	return db_formatted_table

@given('set up database schema')
def step(context):
	engine = create_engine('sqlite:///:memory:')
	metadata = MetaData()
	results = Table('results',metadata,
					Column('respondent_id', Integer),
					Column('survey_id', Integer, ForeignKey('surveys.id')),
					Column('question_id', Integer),
					Column('response', Integer))
	surveys = Table('surveys',metadata,
					Column('id', Integer, primary_key=True),
					Column('survey_code', String))
	metadata.create_all(engine)

	conn = engine.connect()
	context.engine = engine
	context.db = conn
	context.results_table = results
	context.surveys_table = surveys

@given('a results table with this data')
def step(context):
	context.db.execute(context.results_table.insert(),table_for_db(context.table))

@when('retrieve results for survey_id 1 is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_one_survey(survey_id=1)

@then('there are 8 rows returned')
def step(context):
	assert len(context.results['rows'])==8

@given('a survey table with this data')
def step(context):
	context.db.execute(context.surveys_table.insert(),table_for_db(context.table))

@when('retrieve results for survey_code 1314F8W is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_one_survey(survey_code="1314F8W")