from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select

class ResultsRetriever(object):
	"""docstring for ResultsRetriever"""
	def __init__(self, **kwargs):
		self.db_connection = kwargs.pop('db_connection',None)

	def retrieve_results_for_one_survey(self,**kwargs):
		survey_id = kwargs.pop('survey_id',None)
		survey_code = kwargs.pop('survey_code',None)
		metadata = MetaData()
		results = Table('results',metadata,
					Column('respondent_id', Integer),
					Column('survey_id', Integer, ForeignKey('surveys.id')),
					Column('question_id', Integer),
					Column('response', Integer))
		surveys = Table('surveys',metadata,
					Column('id', Integer, primary_key=True),
					Column('survey_code', String))
		if survey_code != None:
			select_results = select([results]).select_from(results.join(select([surveys]).where(surveys.c.survey_code == survey_code)))
		else:
			select_results = select([results]).where(results.c.survey_id == survey_id)

		results = self.db_connection.execute(select_results)
		return 	{'rows':results.fetchall(),'column_headings':results.keys()}