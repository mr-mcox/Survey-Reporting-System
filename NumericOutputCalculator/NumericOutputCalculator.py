import pandas as pd

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):		
		responses = pd.DataFrame(kwargs.pop('responses',dict()))
		assert not responses.empty

		if 'net_formatted_value' not in responses.columns:
			map_7pt_SA_to_net = {8:None,7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
			responses['net_formatted_value'] = responses.response.map(map_7pt_SA_to_net)
		self.responses = responses
		self.demographic_data = kwargs.pop('demographic_data',pd.DataFrame())

	def compute_aggregation(self,**kwargs):
		cut_demographic = kwargs.pop('cut_demographic', None)
		result_type = kwargs.pop('result_type',None)
		assert result_type != None

		nfv = self.responses.copy()
		if not self.demographic_data.empty:
			nfv = nfv.join(self.demographic_data.loc[:,cut_demographic], how = 'outer')

		cut_groupings = ['question_id']
		if cut_demographic != None:
			if type(cut_demographic) == list:
				cut_groupings = cut_groupings + cut_demographic
			else:
				cut_groupings.append(cut_demographic)

		if result_type == 'net':
			return nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'strong':
			nfv.ix[nfv.net_formatted_value.notnull() & (nfv.net_formatted_value != 1),'net_formatted_value'] = 0
			return nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'weak':
			nfv.ix[nfv.net_formatted_value.notnull() & (nfv.net_formatted_value != -1),'net_formatted_value'] = 0
			nfv.net_formatted_value = nfv.net_formatted_value * -1
			return nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'raw_average':
			return self.responses.groupby(cut_groupings).mean().rename(columns={'response':'aggregation_value'}).reset_index()


	def compute_net_results(self,**kwargs):
		return self.compute_aggregation(result_type='net',**kwargs)

	def compute_strong_results(self,**kwargs):
		return self.compute_aggregation(result_type='strong',**kwargs)
		
	def compute_weak_results(self,**kwargs):
		return self.compute_aggregation(result_type='weak',**kwargs)

	def compute_average_results(self,**kwargs):
		return self.compute_aggregation(result_type='raw_average',**kwargs)
