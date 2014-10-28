import pandas as pd
from sqlalchemy import create_engine

connect_string = 'mysql+oursql://mcox:fa1c0n@localhost/mdis_survey_database'
engine = create_engine(connect_string)
conn = engine.connect()

df = pd.io.sql.read_sql('numerical_responses',engine)

surveys = ['0809EYS',
			'0809MYS',
			'0910EYS',
			'0910MYS',
			'1011EYS',
			'1011MYS',
			'1011R0',
			'1112EYS',
			'1112F8W',
			'1112MYS',
			'1213EYS',
			'1213F8W',
			'1213Ind',
			'1213MYS',
			'1314EYS',
			'1314F8W',
			'1314MYS',
			'1415F8W',
			'1415Ind',
			'2009Inst.EIS',
			'2010Inst.EIS',
			'2011Inst-EIS',
			'2012Inst-EIS',
			'2012Inst-MIS',
			'2013Ind',
			'2013Inst-EIS',
			'2013MIS',
			'2014Inst-EIS',
			'2014Inst-MIS',]

archived_surveys = [
'1213Ind',
'1314MYS',
'2012Inst-MIS',
]

df2 = pd.io.sql.read_sql('numerical_responses_archive',engine)

pd.concat([df.ix[df.survey.isin(surveys)],df2.ix[df2.survey.isin(archived_surveys)]]).to_csv('responses.csv',index=False)