import pandas as pd
import logging
# import pdb

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):		
		responses = pd.DataFrame(kwargs.pop('responses',dict())).convert_objects(convert_numeric=True)
		assert not responses.empty
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
		result_types = list()
		if type(result_type) == list:
			result_types = result_type
		else:
			result_types = [result_type]

		if type(cut_demographic) == list:
			for cut in cut_demographic:
				if cut != []:
					assert cut in self.demographic_data.columns
		elif cut_demographic != None:
			assert cut_demographic in self.demographic_data.columns

		nfv = self.responses.copy()
		raw_fv = self.responses.copy()
		if not self.demographic_data.empty:
			if cut_demographic != []:
				assert 'respondent_id' in nfv, "Expected respondent_id column in responses"
				assert 'respondent_id' in self.demographic_data, "Expected respondent_id column in demographic_data"
				nfv = nfv.set_index('respondent_id').join(self.demographic_data.set_index('respondent_id').loc[:,cut_demographic], how = 'outer')

		cut_groupings = ['question_code']
		if cut_demographic != None:
			assert type(cut_demographic) == str or type(cut_demographic) == list
			if type(cut_demographic) == list:
				cut_groupings = cut_groupings + cut_demographic
			else:
				cut_groupings.append(cut_demographic)

		aggregation_calulations_list = list()
		for result_type in result_types:
			nfv_copy = nfv.copy()
			logging.debug("Computing aggregation for result type "+ result_type + " and cuts "+ str(cut_groupings))
			# logging.debug("Responses columns are " + str(nfv))
			assert result_type in {'net','strong','weak','raw_average','sample_size','strong_count','weak_count'}, "No calculation defined for result_type " + result_type
			aggregation_calulation = pd.DataFrame()
			if result_type == 'net':
				aggregation_calulation = nfv_copy.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
			if result_type == 'strong':
				nfv_copy.ix[nfv_copy.net_formatted_value.notnull() & (nfv_copy.net_formatted_value != 1),'net_formatted_value'] = 0
				aggregation_calulation = nfv_copy.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
			if result_type == 'strong_count':
				nfv_copy.ix[nfv_copy.net_formatted_value.notnull() & (nfv_copy.net_formatted_value != 1),'net_formatted_value'] = 0
				aggregation_calulation = nfv_copy.groupby(cut_groupings).sum().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
			if result_type == 'weak':
				nfv_copy.ix[nfv_copy.net_formatted_value.notnull() & (nfv_copy.net_formatted_value != -1),'net_formatted_value'] = 0
				nfv_copy.net_formatted_value = nfv_copy.net_formatted_value * -1
				aggregation_calulation = nfv_copy.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
			if result_type == 'weak_count':
				nfv_copy.ix[nfv_copy.net_formatted_value.notnull() & (nfv_copy.net_formatted_value != -1),'net_formatted_value'] = 0
				nfv_copy.net_formatted_value = nfv_copy.net_formatted_value * -1
				aggregation_calulation = nfv_copy.groupby(cut_groupings).sum().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
			if result_type == 'raw_average':
				assert 'response' in nfv_copy.columns
				aggregation_calulation = nfv_copy.groupby(cut_groupings).mean().rename(columns={'response':'aggregation_value'}).reset_index()
			if result_type == 'sample_size':
				assert 'response' in nfv_copy.columns
				aggregation_calulation = nfv_copy.ix[nfv_copy.response.notnull(),:].groupby(cut_groupings).aggregate(len).rename(columns={'response':'aggregation_value'}).reset_index()

			aggregation_calulation['result_type'] = result_type
			aggregation_calulations_list.append(aggregation_calulation)
		return_columns = cut_groupings + ['aggregation_value','result_type']
		return pd.DataFrame(pd.concat(aggregation_calulations_list),columns=return_columns)


	def compute_net_results(self,**kwargs):
		return self.compute_aggregation(result_type='net',**kwargs)

	def compute_strong_results(self,**kwargs):
		return self.compute_aggregation(result_type='strong',**kwargs)
		
	def compute_weak_results(self,**kwargs):
		return self.compute_aggregation(result_type='weak',**kwargs)

	def compute_average_results(self,**kwargs):
		return self.compute_aggregation(result_type='raw_average',**kwargs)

	def compute_sample_size_results(self,**kwargs):
		return self.compute_aggregation(result_type='sample_size',**kwargs)

	def aggregations_for_net_significance(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		assert cuts is not None
		assert type(cuts) == list
		assert len(cuts) >= 1, "Cannot make statistical significance comparison with no dimensions"
		comparison_cuts = cuts[1:]

		base_results = self.compute_aggregation(cut_demographic=cuts,result_type=["sample_size","strong_count","weak_count"])
		comparison_results = self.compute_aggregation(cut_demographic=comparison_cuts,result_type=["sample_size","strong_count","weak_count"])
		return (cuts, comparison_cuts,base_results,comparison_results)


	def bootstrap_net_significance(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		
		cuts, comparison_cuts, base_results, comparison_results = self.aggregations_for_net_significance(cuts=cuts)
		base_results = base_results.set_index(cuts + ['question_code','result_type'])
		base_results = pd.Series(base_results['aggregation_value'],index = base_results.index).unstack()
		comparison_results = comparison_results.set_index(comparison_cuts  + ['question_code','result_type'])
		comparison_results = pd.Series(comparison_results['aggregation_value'],index = comparison_results.index).unstack()
		print(comparison_results)
		comparison_results = comparison_results.rename(columns={'sample_size':'comp_sample_size',
																'strong_count':'comp_strong_count',
																'weak_count':'comp_weak_count'})
		self.counts_for_significance = base_results.reset_index().set_index(comparison_cuts + ['question_code']).join(comparison_results).reset_index().set_index(cuts + ['question_code'])