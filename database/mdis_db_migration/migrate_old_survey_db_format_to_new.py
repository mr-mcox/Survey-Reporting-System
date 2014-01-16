import pandas as pd
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select, create_engine, ForeignKeyConstraint
from sqlalchemy.engine import reflection
import numpy as np
from alembic.migration import MigrationContext
from alembic.operations import Operations
import pdb


#Connect to local DB
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
engine_1 = create_engine('mysql+oursql://mcox:fa1c0n@localhost/mdis_survey_database')
conn_1 = engine_1.connect()

#Connecting to new db
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

connect_info_file = open('db_connect_string.txt')
connect_info = connect_info_file.readline()
connect_info_file.close()
engine_2 = create_engine(connect_info)
conn_2 = engine_2.connect()

#Remove foreign key constraints
# insp = reflection.Inspector.from_engine(engine_2)
# foreign_keys_on_results_table = insp.get_foreign_keys('results')
# ctx = MigrationContext.configure(conn_2)
# alembic_op = Operations(ctx)
# for fk in foreign_keys_on_results_table:
# 	alembic_op.drop_constraint(fk['name'],'results')

#Import from local DB
nr_results = conn_1.execute(select([numerical_responses],numerical_responses.c.survey.in_(['1314MYS'])))
ssq_results = conn_1.execute(select([survey_specific_questions],survey_specific_questions.c.survey.in_(['1314MYS'])))

responses = pd.DataFrame(nr_results.fetchall())
responses.columns = nr_results.keys()

question_table = pd.DataFrame(ssq_results.fetchall())
question_table.columns = ssq_results.keys()

#Read data
# responses = pd.read_csv('numerical_responses.csv')
# question_table = pd.read_csv('survey_specific_questions.csv')

#Create survey table data
survey_codes = question_table.survey.unique().tolist()
survey_map = dict(zip(survey_codes,range(len(survey_codes))))
survey_ids = [survey_map[survey_name] for survey_name in survey_codes]

surveys_for_db = pd.DataFrame({'id':survey_ids,'survey_code':survey_codes})

#Create question table data
questions_list = question_table.survey_specific_qid.unique().tolist()
question_map = dict(zip(questions_list,range(len(questions_list))))

question_table['question_id'] = question_table.survey_specific_qid.map(question_map) + 1
question_table['survey_id'] = question_table.survey.map(survey_map) + 1
question_table = question_table.rename(columns={'master_qid':'question_code','question_id':'id','confidential':'is_confidential'})
questions_for_db = pd.DataFrame(question_table,columns=['id','survey_id','question_code','is_confidential','question_type'])

#Change questions
# pdb.set_trace()
questions_for_db.ix[questions_for_db.question_type == '7pt_Net_1=SA','question_type'] = '7pt_1=SA'
questions_for_db.ix[questions_for_db.question_type == '7pt_NCS_1=SA','question_type'] = '7pt_1=SA'
questions_for_db.ix[questions_for_db.question_type == '7pt_NCS_7=SA','question_type'] = '7pt_7=SA'

#Map survey id and question id onto survey responses
responses['question_id'] = responses.survey_specific_qid.map(question_map)
responses['survey_id'] = responses.survey.map(survey_map)
responses = responses.rename(columns={'cm_pid':'respondent_id'})

#Create results table
results_for_db = pd.DataFrame(responses,columns=['respondent_id','survey_id','question_id','response'])

#Clear new tables
conn_2.execute(results.delete())
conn_2.execute(surveys.delete())
conn_2.execute(questions.delete())

#Insert in new db
def df_to_dict_array(df):
	columns = df.columns
	list_of_rows = list()
	for row in df.itertuples(index=False):
		list_of_rows.append(dict(zip(columns,convert_types_for_db(row))))
	return list_of_rows

def convert_types_for_db(values):
	new_values = list()
	for value in values:
		new_value = value
		if type(value) != str:
			new_value = np.asscalar(value)
		if type(new_value) == str:
			try:
				new_value = float(new_value)
			except:
				pass
		if type(new_value) != str:
			if int(new_value) == new_value:
				new_value = int(new_value)
		new_values.append(new_value)
	return new_values

print("Inserting new results")
try:
	conn_2.execute(surveys.insert(),df_to_dict_array(surveys_for_db))
except:
	pdb.set_trace()

question_rows = df_to_dict_array(questions_for_db)
for i, row in enumerate(question_rows):
	# print("Adding row " + str(row))
	conn_2.execute(questions.insert(),row)
# try:
# 	conn_2.execute(questions.insert(),df_to_dict_array(questions_for_db))
# except:
# 	pdb.set_trace()

conn_2.execute(results.insert(),df_to_dict_array(results_for_db))
# result_rows = df_to_dict_array(results_for_db)
# num_rows = len(result_rows)

# for i, row in enumerate(result_rows):
# 	conn_2.execute(results.insert(),row)
# 	print("\rInserting result " + str(i) + " of " + str(num_rows), end = " " )

#Add foreign keys back
# for fk in foreign_keys_on_results_table:
# 	alembic_op.create_foreign_key(fk['name'],'results',fk['referred_table'],fk['constrained_columns'],fk['referred_columns'])

