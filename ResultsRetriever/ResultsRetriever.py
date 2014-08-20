from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select
import logging

class ResultsRetriever(object):
	"""docstring for ResultsRetriever"""
	def __init__(self, **kwargs):
		self.db_connection = kwargs.pop('db_connection',None)

	def retrieve_results_for_survey(self,**kwargs):
		survey_id = kwargs.pop('survey_id',None)
		survey_code = kwargs.pop('survey_code',None)
		if not type(survey_code) is list:
			survey_code = [survey_code]
		metadata = MetaData()
		results = Table('results',metadata,
					Column('respondent_id', Integer),
					Column('survey_id', Integer, ForeignKey('surveys.id')),
					Column('question_id', Integer, ForeignKey('questions.id')),
					Column('response', Integer))
		surveys = Table('surveys',metadata,
					Column('id', Integer, primary_key=True, autoincrement=False),
					Column('survey_code', String))
		questions = Table('questions',metadata,
					Column('id', Integer, primary_key=True, autoincrement=False),
					Column('survey_id', Integer),
					Column('question_code', String(20)),
					Column('is_confidential', Integer),
					Column('question_type', String(20)),)
		if survey_code != [None]:
			sq = (select([surveys],use_labels=True).where(surveys.c.survey_code.in_(survey_code))).alias('sq')
			if len(survey_code) > 1:
				select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type, questions.c.question_code,sq.c.surveys_survey_code.label('survey_code')]).select_from(results.join(questions).join(sq))
			else:
				select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions).join(select([surveys],use_labels=True).where(surveys.c.survey_code.in_(survey_code)).alias('sq')))
		else:
			select_results = select([results, questions.c.question_code,questions.c.is_confidential,questions.c.question_type]).select_from(results.join(questions)).where(results.c.survey_id == survey_id)

		logging.debug('retrieve_results_for_survey query:\n' + str(select_results))
		results = self.db_connection.execute(select_results)
		return 	{'rows':results.fetchall(),'column_headings':results.keys()}