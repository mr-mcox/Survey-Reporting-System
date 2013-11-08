from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select

class ResultsRetriever(object):
	"""docstring for ResultsRetriever"""
	def __init__(self, **kwargs):
		self.db_connection = kwargs.pop('db_connection',None)

	def retrieve_results_for_one_survey(self,**kwargs):
		survey_id = kwargs.pop('survey_id',None)
		metadata = MetaData()
		results = Table('results',metadata,
				Column('respondent_id', Integer),
				Column('survey_id', Integer),
				Column('question_id', Integer),
				Column('response', Integer))
		select_results = select([results]).where(results.c.survey_id == survey_id)

		return 	self.db_connection.execute(select_results).fetchall()

