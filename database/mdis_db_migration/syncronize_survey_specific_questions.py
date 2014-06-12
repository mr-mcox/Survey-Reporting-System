from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select, create_engine, ForeignKeyConstraint, func
import pandas as pd
import numpy as np
import sys

#Some basic conversion of types needs to occur for the database library to be ok with it
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
			if np.isnan(new_value):
				new_value = None
			elif int(new_value) == new_value:
				new_value = int(new_value)
		new_values.append(new_value)
	return new_values

def df_to_dict_array(df):
	columns = df.columns
	list_of_rows = list()
	for row in df.itertuples(index=False):
		list_of_rows.append(dict(zip(columns,convert_types_for_db(row))))
	return list_of_rows

#Set up database connections
local_connect_info_file = open('local_db_connect_string.txt')
local_connect_info = local_connect_info_file.readline()

local_engine = create_engine(local_connect_info)
l_conn = local_engine.connect()

remote_connect_info_file = open('remote_db_connect_string.txt')
remote_connect_info = remote_connect_info_file.readline()

remote_engine = create_engine(remote_connect_info)
r_conn = remote_engine.connect()

#Define schema
metadata = MetaData()
survey_specific_questions = Table('survey_specific_questions',metadata,
							Column('survey_specific_qid',String),
							Column('master_qid',String),
							Column('survey',String),
							Column('confidential',Integer),
							Column('question_type',String)
							)


survey_codes = sys.argv[1:]

for code in survey_codes:
	#Remove old questions on the remote database
	r_conn.execute(survey_specific_questions.delete().where(survey_specific_questions.c.survey==code))

ssq_results = l_conn.execute(select([survey_specific_questions],survey_specific_questions.c.survey.in_(survey_codes)))

question_table = pd.DataFrame(ssq_results.fetchall())
question_table.columns = ssq_results.keys()

r_conn.execute(survey_specific_questions.insert(),df_to_dict_array(question_table))
