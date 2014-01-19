from behave import *
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from ResultsRetriever import ResultsRetriever
import pandas as pd

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
					Column('question_id', Integer, ForeignKey('questions.id')),
					Column('response', Integer))
	surveys = Table('surveys',metadata,
					Column('id', Integer, primary_key=True),
					Column('survey_code', String))
	questions = Table('questions',metadata,
					Column('id', Integer, primary_key=True),
					Column('survey_id', Integer),
					Column('question_code', String(20)),
					Column('is_confidential', Integer),
					Column('question_type', String(20)),)
	metadata.create_all(engine)

	conn = engine.connect()
	context.engine = engine
	context.db = conn
	context.results_table = results
	context.surveys_table = surveys
	context.questions_table = questions

@given('a results table with this data')
def step(context):
	context.db.execute(context.results_table.insert(),table_for_db(context.table))

@when('retrieve results for survey_id 1 is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_survey(survey_id=1)

@then('there are {number} rows returned')
def step(context,number):
	assert len(context.results['rows'])==int(number)

@given('a survey table with this data')
def step(context):
	context.db.execute(context.surveys_table.insert(),table_for_db(context.table))

@when('retrieve results for survey_code 1314F8W is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_survey(survey_code="1314F8W")

@given('a question table with this data')
def step(context):
	context.db.execute(context.questions_table.insert(),table_for_db(context.table))

@then('one of the columns returned is {column}')
def step(context, column):
	assert column in context.results['column_headings']

@when('retrieve results for multiple surveys with survey_code 1314F8W and 1314MYS is run')
def step(context):
	context.results = ResultsRetriever(db_connection=context.db).retrieve_results_for_survey(survey_code=["1314F8W","1314MYS"])