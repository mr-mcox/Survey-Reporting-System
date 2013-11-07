import pandas as pd

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):
		
		net_results = kwargs.pop('net_formatted_values', None)
		net_results = pd.DataFrame(net_results)
		self.net_results = net_results

	def compute_net_results(self):
		return self.net_results.groupby('question_id').mean().reset_index()

	def compute_strong_results(self):
		data = self.net_results.copy()
		data.ix[data.value.notnull() & (data.value != 1),'value'] = 0
		return data.groupby('question_id').mean().reset_index()
	
	def compute_weak_results(self):
		data = self.net_results.copy()
		data.ix[data.value.notnull() & (data.value != -1),'value'] = 0
		data.value = data.value * -1
		return data.groupby('question_id').mean().reset_index()
