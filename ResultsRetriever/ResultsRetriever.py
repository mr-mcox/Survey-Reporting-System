class ResultsRetriever(object):
	"""docstring for ResultsRetriever"""
	def __init__(self, **kwargs):
		self.db_connection = kwargs.pop('db_connection',None)

	def retrieve_results_for_one_survey(self,**kwargs):
		survey_id = kwargs.pop('survey_id',None)
		return 	self.db_connection.execute("SELECT * FROM results WHERE survey_id = 1").fetchall()

