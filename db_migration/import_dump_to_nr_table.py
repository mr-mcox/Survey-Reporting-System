import pandas as pd
from sqlalchemy import Table, Column, Integer, String, MetaData, select, create_engine
import sys
import numpy as np
import logging

logging.basicConfig(filename='migration.log',level=logging.INFO)

connect_info_file = open(sys.argv[2])
connect_info = connect_info_file.readline().strip()
engine = create_engine(connect_info)
conn = engine.connect()
df = pd.read_csv(sys.argv[1])

#Some basic conversion of types needs to occur for the database library to be ok with it
def convert_types_for_db(values):
    new_values = list()
    for value in values:
        new_value = value
        if type(value) != str and type(value) != int and new_value is not None:
            new_value = np.asscalar(value)
        if type(new_value) == str:
            try:
                new_value = float(new_value)
            except:
                pass
        if type(new_value) != str  and new_value is not None:
            if np.isnan(new_value):
                new_value = None
            elif int(new_value) == new_value:
                new_value = int(new_value)
        new_values.append(new_value)
    return new_values

#Insert in new db
def df_to_dict_array(df):
    columns = df.columns
    list_of_rows = list()
    for row in df.itertuples(index=False):
        list_of_rows.append(dict(zip(columns,convert_types_for_db(row))))
    return list_of_rows


metadata = MetaData()
#Tables
numerical_responses = Table('numerical_responses',metadata,
                        Column('cm_pid', Integer),
                        Column('survey', String),
                        Column('survey_specific_qid', String),
                        Column('response', Integer))



# df.to_sql('numerical_responses',engine,if_exists='append',index=False)
for survey in df.survey.unique().tolist():
    logging.info("Importing survey " + survey)
    conn.execute(numerical_responses.delete().where(numerical_responses.c.survey == survey))
    conn.execute(numerical_responses.insert(),df_to_dict_array(df.ix[df.survey==survey]))