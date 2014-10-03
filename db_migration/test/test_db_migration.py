from SurveyReportingSystem.db_migration.migrate import migrate
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, engine, select
import pytest
import pandas as pd

@pytest.fixture
def empty_db():
	engine = create_engine('sqlite:///:memory:')
	metadata = MetaData()
	numerical_responses = Table('numerical_responses',metadata,
						Column('cm_pid', Integer),
						Column('survey', String),
						Column('survey_specific_qid', String),
						Column('response', Integer))

	survey_specific_questions = Table('survey_specific_questions',metadata,
							Column('survey_specific_qid',String),
							Column('master_qid',String),
							Column('survey',String),
							Column('confidential',Integer),
							Column('question_type',String)
							)
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

	schema = {
		'numerical_responses':numerical_responses,
		'survey_specific_questions':survey_specific_questions,
		'results':results,
		'surveys':surveys,
		'questions':questions,
	}

	conn = engine.connect()

	return {'conn':conn,'schema':schema}

@pytest.fixture
def db_ready_to_migrate(empty_db):
	conn = empty_db['conn']
	numerical_responses = empty_db['schema']['numerical_responses']
	survey_specific_questions = empty_db['schema']['survey_specific_questions']
	nr_cols = ['cm_pid','survey','survey_specific_qid','response']
	ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type']

	nr_rows = [
		(1,'1415F8W','1415F8W-CSI1',1),
		(1,'1415F8W','1415F8W-CSI2',2),
		(1,'1415F8W','1415F8W-CSI3',3),
	]

	ssq_rows = [
		('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI3','CSI3','1415F8W',1,'7pt_1=SA'),
	]
	for row in nr_rows:
		conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
	for row in ssq_rows:
		conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
	return empty_db

@pytest.fixture
def db_with_incomplete_CSI(empty_db):
	conn = empty_db['conn']
	numerical_responses = empty_db['schema']['numerical_responses']
	survey_specific_questions = empty_db['schema']['survey_specific_questions']
	nr_cols = ['cm_pid','survey','survey_specific_qid','response']
	ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type']

	nr_rows = [
		(1,'1415F8W','1415F8W-CSI1',1),
		(1,'1415F8W','1415F8W-CSI2',2),
		(1,'1415F8W','1415F8W-CSI3',3),
		(1,'1415F8W','1415F8W-CSI4',3),
		(1,'1415F8W','1415F8W-CSI5',3),
		(1,'1415F8W','1415F8W-CSI6',3),
		(1,'1415F8W','1415F8W-CSI7',3),
		(1,'1415F8W','1415F8W-CSI8',3),
		(1,'1415F8W','1415F8W-CSI10',3),
		(1,'1415F8W','1415F8W-CSI12',3),
		(1,'1415F8W','1415F8W-Culture1',3),
		(2,'1415F8W','1415F8W-CSI1',1),
		(2,'1415F8W','1415F8W-CSI2',2),
		(2,'1415F8W','1415F8W-CSI3',3),
		(2,'1415F8W','1415F8W-CSI4',3),
		(2,'1415F8W','1415F8W-CSI5',3),
		(2,'1415F8W','1415F8W-CSI6',3),
		(2,'1415F8W','1415F8W-CSI7',3),
		(2,'1415F8W','1415F8W-CSI8',3),
		(2,'1415F8W','1415F8W-CSI10',3),
		(2,'1415F8W','1415F8W-CSI12',3),
	]

	ssq_rows = [
		('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI3','CSI3','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI4','CSI4','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI5','CSI5','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI6','CSI6','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI7','CSI7','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI8','CSI8','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI10','CSI10','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CSI12','CSI12','1415F8W',1,'7pt_1=SA'),
		('1415F8W-Culture1','Culture1','1415F8W',1,'7pt_1=SA'),
	]
	for row in nr_rows:
		conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
	for row in ssq_rows:
		conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
	return empty_db

@pytest.fixture
def db_with_incomplete_CALI(empty_db):
	conn = empty_db['conn']
	numerical_responses = empty_db['schema']['numerical_responses']
	survey_specific_questions = empty_db['schema']['survey_specific_questions']
	nr_cols = ['cm_pid','survey','survey_specific_qid','response']
	ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type']

	nr_rows = [
		(1,'1415F8W','1415F8W-CLI1',1),
		(1,'1415F8W','1415F8W-CLI2',2),
		(1,'1415F8W','1415F8W-CLI3',3),
		(1,'1415F8W','1415F8W-CLI4',3),
		(1,'1415F8W','1415F8W-CLI5',3),
		(1,'1415F8W','1415F8W-CLI6',3),
		(1,'1415F8W','1415F8W-CLI7',3),
		(1,'1415F8W','1415F8W-CLI8',3),
		(2,'1415F8W','1415F8W-CLI1',1),
		(2,'1415F8W','1415F8W-CLI2',2),
		(2,'1415F8W','1415F8W-CLI3',3),
		(2,'1415F8W','1415F8W-CLI4',3),
		(2,'1415F8W','1415F8W-CLI5',3),
		(2,'1415F8W','1415F8W-CLI6',3),
		(2,'1415F8W','1415F8W-CLI7',3),
	]

	ssq_rows = [
		('1415F8W-CLI1','CLI1','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI2','CLI2','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI3','CLI3','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI4','CLI4','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI5','CLI5','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI6','CLI6','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI7','CLI7','1415F8W',1,'7pt_1=SA'),
		('1415F8W-CLI8','CLI8','1415F8W',1,'7pt_1=SA'),
	]
	for row in nr_rows:
		conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
	for row in ssq_rows:
		conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
	return empty_db

def test_basic_migration(db_ready_to_migrate):
	schema = db_ready_to_migrate['schema']
	results = schema['results']
	surveys = schema['surveys']
	questions = schema['questions']

	migrate(db_ready_to_migrate['conn'],db_ready_to_migrate['conn'],['1415F8W'])
	sq = (select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W']))).alias('sq')
	select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions).join(select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W'])).alias('sq')))
	db_results = db_ready_to_migrate['conn'].execute(select_results)

	df = pd.DataFrame.from_records(db_results.fetchall(),columns=db_results.keys())
	assert df.set_index('question_code').get_value('CSI2','response') == 2

def test_removing_responses_incomplete_CSI(db_with_incomplete_CSI):
	schema = db_with_incomplete_CSI['schema']
	results = schema['results']
	surveys = schema['surveys']
	questions = schema['questions']

	migrate(db_with_incomplete_CSI['conn'],db_with_incomplete_CSI['conn'],['1415F8W'],clean_CSI=True)
	sq = (select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W']))).alias('sq')
	select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions).join(select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W'])).alias('sq')))
	db_results = db_with_incomplete_CSI['conn'].execute(select_results)

	df = pd.DataFrame.from_records(db_results.fetchall(),columns=db_results.keys())
	assert len(df.ix[df.respondent_id==2].index) == 0
	assert len(df.ix[df.respondent_id==1].index) == 11

def test_removing_responses_incomplete_CALI(db_with_incomplete_CALI):
	schema = db_with_incomplete_CALI['schema']
	results = schema['results']
	surveys = schema['surveys']
	questions = schema['questions']

	migrate(db_with_incomplete_CALI['conn'],db_with_incomplete_CALI['conn'],['1415F8W'],clean_CALI=True)
	sq = (select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W']))).alias('sq')
	select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions).join(select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W'])).alias('sq')))
	db_results = db_with_incomplete_CALI['conn'].execute(select_results)

	df = pd.DataFrame.from_records(db_results.fetchall(),columns=db_results.keys())
	assert len(df.ix[df.respondent_id==2].index) == 0
	assert len(df.ix[df.respondent_id==1].index) == 8