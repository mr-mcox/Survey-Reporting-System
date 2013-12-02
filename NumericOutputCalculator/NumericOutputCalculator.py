import pandas as pd
import logging
# import pdb

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):		
		responses = pd.DataFrame(kwargs.pop('responses',dict())).convert_objects(convert_numeric=True)
		assert not responses.empty

		# logging.debug('values before re-formatting:\n' + str(responses.head()))

		if 'net_formatted_value' not in responses.columns or responses['net_formatted_value'].notnull().sum() == 0:
			map_7pt_SA_to_net = {8:None,7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
			responses['net_formatted_value'] = responses.response.map(map_7pt_SA_to_net)
		assert responses.net_formatted_value.notnull().sum() > 0
		self.responses = responses
		self.demographic_data = kwargs.pop('demographic_data',pd.DataFrame())

	def compute_aggregation(self,**kwargs):
		cut_demographic = kwargs.pop('cut_demographic', None)
		result_type = kwargs.pop('result_type',None)
		assert result_type != None

		# logging.debug("NumOutput cut_demographic is " + str(cut_demographic))
		if type(cut_demographic) == list:
			for cut in cut_demographic:
				if cut != []:
					assert cut in self.demographic_data.columns
		elif cut_demographic != None:
			assert cut_demographic in self.demographic_data.columns

		nfv = self.responses.copy()
		if not self.demographic_data.empty:
			if cut_demographic != []:
				assert 'respondent_id' in nfv, "Expected respondent_id column in responses"
				assert 'respondent_id' in self.demographic_data, "Expected respondent_id column in demographic_data"
				# logging.debug("data sets to join " + str(nfv) + " and demographics " + str(self.demographic_data))			
				nfv = nfv.set_index('respondent_id').join(self.demographic_data.set_index('respondent_id').loc[:,cut_demographic], how = 'outer')

		cut_groupings = ['question_code']
		if cut_demographic != None:
			assert type(cut_demographic) == str or type(cut_demographic) == list
			if type(cut_demographic) == list:
				cut_groupings = cut_groupings + cut_demographic
			else:
				cut_groupings.append(cut_demographic)

		aggregation_calulation = pd.DataFrame()
		if result_type == 'net':
			aggregation_calulation = nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'strong':
			nfv.ix[nfv.net_formatted_value.notnull() & (nfv.net_formatted_value != 1),'net_formatted_value'] = 0
			aggregation_calulation = nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'weak':
			nfv.ix[nfv.net_formatted_value.notnull() & (nfv.net_formatted_value != -1),'net_formatted_value'] = 0
			nfv.net_formatted_value = nfv.net_formatted_value * -1
			aggregation_calulation = nfv.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
		if result_type == 'raw_average':
			aggregation_calulation = self.responses.groupby(cut_groupings).mean().rename(columns={'response':'aggregation_value'}).reset_index()

		aggregation_calulation['result_type'] = result_type
		return_columns = cut_groupings + ['aggregation_value','result_type']
		# logging.debug('results for ' + str(return_columns) + ': ' + str(pd.DataFrame(aggregation_calulation,columns=return_columns)))
		return pd.DataFrame(aggregation_calulation,columns=return_columns)


	def compute_net_results(self,**kwargs):
		return self.compute_aggregation(result_type='net',**kwargs)

	def compute_strong_results(self,**kwargs):
		return self.compute_aggregation(result_type='strong',**kwargs)
		
	def compute_weak_results(self,**kwargs):
		return self.compute_aggregation(result_type='weak',**kwargs)

	def compute_average_results(self,**kwargs):
		return self.compute_aggregation(result_type='raw_average',**kwargs)
