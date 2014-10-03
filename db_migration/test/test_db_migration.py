from SurveyReportingSystem.db_migration.migrate import migrate
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, engine, select
import pytest
import pandas as pd

@pytest.fixture
def db_ready_to_migrate():
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

	return {'conn':conn,'schema':schema}

def test_basic_migration(db_ready_to_migrate):
	schema = db_ready_to_migrate['schema']
	results = schema['results']
	surveys = schema['surveys']
	questions = schema['questions']

	migrate(db_ready_to_migrate['conn'],db_ready_to_migrate['conn'],'1415F8W')
	sq = (select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W']))).alias('sq')
	select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions).join(select([surveys],use_labels=True).where(surveys.c.survey_code.in_(['1415F8W'])).alias('sq')))
	db_results = db_ready_to_migrate['conn'].execute(select_results)

	df = pd.DataFrame.from_records(db_results.fetchall(),columns=db_results.keys())
	assert df.set_index('question_code').get_value('CSI2','response') == 2