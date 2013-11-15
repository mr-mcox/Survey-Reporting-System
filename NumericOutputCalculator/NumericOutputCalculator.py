import pandas as pd

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):
		
		net_formatted_values = kwargs.pop('net_formatted_values', None)
		raw_values = kwargs.pop('raw_values', None)
		if net_formatted_values == None:
			map_7pt_SA_to_net = {8:None,7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
			net_formatted_values = pd.DataFrame(raw_values)
			net_formatted_values['value'] = net_formatted_values.response.map(map_7pt_SA_to_net)
		net_formatted_values = pd.DataFrame(net_formatted_values)
		self.net_formatted_values = net_formatted_values
		self.raw_values = pd.DataFrame(raw_values)
		self.demographic_data = kwargs.pop('demographic_data',pd.DataFrame())

	def compute_net_results(self,**kwargs):
		cut_demographic = kwargs.pop('cut_demographic', None)
		nfv = self.net_formatted_values
		if not self.demographic_data.empty:
			nfv = nfv.join(self.demographic_data.loc[:,cut_demographic], how = 'outer')

		cut_groupings = ['question_id']
		if cut_demographic != None:
			if type(cut_demographic) == list:
				cut_groupings = cut_groupings + cut_demographic
			else:
				cut_groupings.append(cut_demographic)
		return nfv.groupby(cut_groupings).mean().reset_index()

	def compute_strong_results(self):
		data = self.net_formatted_values.copy()
		data.ix[data.value.notnull() & (data.value != 1),'value'] = 0
		return data.groupby('question_id').mean().reset_index()
	
	def compute_weak_results(self):
		data = self.net_formatted_values.copy()
		data.ix[data.value.notnull() & (data.value != -1),'value'] = 0
		data.value = data.value * -1
		return data.groupby('question_id').mean().reset_index()

	def compute_average_results(self):
		return self.raw_values.groupby('question_id').mean().reset_index()
