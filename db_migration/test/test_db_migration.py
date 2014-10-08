from SurveyReportingSystem.db_migration.migrate import Migrator
from sqlalchemy import Table, Column, Integer, String, MetaData, select, create_engine
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
							Column('question_type',String),
							Column('survey_specific_question',String(2000)),
							)
	question = Table('cm_question',metadata,
		Column('question_id', Integer, primary_key=True, autoincrement=False),
		Column('question_title', String(2000)),
		Column('question_code', String(20)),
		)
	question_category = Table('cm_question_category',metadata,
		Column('question_category_id', Integer, primary_key=True, autoincrement=False),
		Column('question_category', String(20)),
		)
	response = Table('cm_response',metadata,
		Column('person_id', Integer, primary_key=True, autoincrement=False),
		Column('survey_question_id', Integer, primary_key=True, autoincrement=False),
		Column('response', Integer),
		Column('converted_net_value', Integer),
		)
	survey = Table('cm_survey',metadata,
		Column('survey_id', Integer, primary_key=True, autoincrement=False),
		Column('survey_code', String(20)),
		Column('survey_title', String(2000)),
		)
	survey_question = Table('cm_survey_question',metadata,
		Column('survey_question_id', Integer, primary_key=True, autoincrement=False),
		Column('survey_id', Integer),
		Column('is_confidential', Integer),
		Column('question_type', String(20)),
		Column('question_title_override', String(2000)),
		Column('question_id', Integer),
		Column('question_category_id', Integer),
		)

	metadata.create_all(engine)

	schema = {
			'numerical_responses':numerical_responses,
			'survey_specific_questions':survey_specific_questions,
			'question':question,
			'question_category':question_category,
			'response':response,
			'survey':survey,
			'survey_question':survey_question,
		}
	conn = engine.connect()

	return {'conn':conn,'schema':schema}

@pytest.fixture
def migrator_with_ssq_for_survey(empty_db):
	conn = empty_db['conn']
	survey_specific_questions = empty_db['schema']['survey_specific_questions']
	ssq_cols = ['survey_specific_qid', 'survey']
	ssq_rows = [('2014Inst-EIS-CSI1','2014Inst-EIS'),
				('1415F8W-CSI1','1415F8W'),
				('1415F8W-CSI2','1415F8W')]
	for row in ssq_rows:
		conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
	return Migrator(conn)

def test_extract_survey_code_from_survey_specific_questions(migrator_with_ssq_for_survey):
	m = migrator_with_ssq_for_survey
	assert len(m.survey_df.index)==2

def test_assign_survey_id_and_map(migrator_with_ssq_for_survey):
	m = migrator_with_ssq_for_survey
	for i in m.survey_df.index:
		assert m.survey_df.loc[i,'survey_id'] == m.survey_id_survey_code_map[m.survey_df.loc[i,'survey_code']]

def test_assign_question_text(migrator_with_ssq_for_survey):
	m = migrator_with_ssq_for_survey
	assert m.survey_df.set_index('survey_code').get_value('1415F8W','survey_title') =='2014-15 First 8 Weeks CM Survey'

@pytest.fixture
def empty_migrator(empty_db):
	conn = empty_db['conn']
	return Migrator(conn)

def test_basic_question_category_df(empty_migrator):
	m = empty_migrator
	expected_df = pd.DataFrame({'question_category_id':[1,2],'question_category':['CALI','CSI']})
	pd.util.testing.assert_frame_equal(m.question_category_df, expected_df)

def test_question_category_question_code_map(empty_migrator):
	m = empty_migrator
	expected_dict = {
		'CSI2' : 'CSI',
		'CSI1' : 'CSI',
		'CSI8' : 'CSI',
		'CSI10' : 'CSI',
		'CSI12' : 'CSI',
		'CSI4' : 'CSI',
		'CSI5' : 'CSI',
		'CSI6' : 'CSI',
		'Culture1' : 'CSI',
		'CSI3' : 'CSI',
		'CSI7' : 'CSI',
		'CLI1' : 'CALI',
		'CLI2' : 'CALI',
		'CLI3' : 'CALI',
		'CLI4' : 'CALI',
		'CLI5' : 'CALI',
		'CLI6' : 'CALI',
		'CLI7' : 'CALI',
		'CLI8' : 'CALI',
	}
	df = m.question_category_df.set_index('question_category')
	for key, value in expected_dict.items():
		assert m.question_category_question_code_map[key] == df.get_value(value,'question_category_id')

@pytest.fixture
def migrator_with_ssq_for_survey_question(empty_db):
	conn = empty_db['conn']
	survey_specific_questions = empty_db['schema']['survey_specific_questions']
	ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
	ssq_rows = [
				('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
				('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
				('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
				]
	for row in ssq_rows:
		conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
	return Migrator(conn)

def test_basic_fields_in_survey_question(migrator_with_ssq_for_survey_question):
	m = migrator_with_ssq_for_survey_question
	expected_records = [
				('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
				('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
				('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
				]
	expected_columns = ['survey_specific_qid','master_qid','survey','is_confidential','question_type','survey_specific_question']
	expected_df = pd.DataFrame.from_records(expected_records,columns=expected_columns)
	pd.util.testing.assert_frame_equal(pd.DataFrame(m.survey_question_df,columns=expected_columns), expected_df)

def test_question_code_survey_column(migrator_with_ssq_for_survey_question):
	m = migrator_with_ssq_for_survey_question
	for i in m.survey_question_df.index:
		assert m.survey_question_df.get_value(i,'survey_question_code') == m.survey_question_df.get_value(i,'survey') + m.survey_question_df.get_value(i,'master_qid')

def test_survey_question_code_survey_question_id_map(migrator_with_ssq_for_survey_question):
	m = migrator_with_ssq_for_survey_question
	for i in m.survey_question_df.index:
		assert m.survey_question_df.loc[i,'survey_question_id'] == m.survey_question_code_survey_question_id_map[m.survey_question_df.loc[i,'survey_question_code']]