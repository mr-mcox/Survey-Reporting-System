import pandas as pd
import logging
import numpy as np
import pdb
from scipy.stats import poisson, skellam

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):		
		responses = pd.DataFrame(kwargs.pop('responses',dict())).convert_objects(convert_numeric=True)
		assert not responses.empty
		if 'net_formatted_value' not in responses.columns or responses['net_formatted_value'].notnull().sum() == 0:
			responses['net_formatted_value'] = None
			if 'question_type' in responses.columns:
				#Map NFVs
				map_7pt_SA_to_net = {8:None,7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
				responses.ix[responses.question_type == '7pt_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_1=SA','response'].map(map_7pt_SA_to_net)
				map_10pt_SA_to_net = {10:-1,9:-1,8:-1,7:-1,6:-1,5:-1,4:0,3:0,2:1,1:1}
				responses.ix[responses.question_type == '10pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_1=SA','response'].map(map_10pt_SA_to_net)
				map_7pt_7_SA_to_net = {7:1,6:1,5:0,4:-1,3:-1,2:-1,1:-1}
				responses.ix[responses.question_type == '7pt_7=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_7=SA','response'].map(map_7pt_7_SA_to_net)
				map_11pt_NPS_1_SA_to_net = {11:-1,10:-1,9:-1,8:-1,7:-1,6:-1,5:-1,4:0,3:0,2:1,1:1}
				responses.ix[responses.question_type == '11pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '11pt_NPS_1=SA','response'].map(map_11pt_NPS_1_SA_to_net)
				map_10pt_NPS_10_SA_to_net = {10:1,9:1,8:0,7:0,6:-1,5:-1,4:-1,3:-1,2:-1,1:-1}
				responses.ix[responses.question_type == '10pt_NPS_10=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_10=SA','response'].map(map_10pt_NPS_10_SA_to_net)
				
				#Map responses
				responses.ix[(responses.question_type == '7pt_1=SA') & (responses.response > 7 ),'response'] = np.nan
				responses.ix[(responses.question_type == '7pt_1=SA'),'response'] = 8 - responses.ix[(responses.question_type == '7pt_1=SA'),'response']
				responses.ix[(responses.question_type == '10pt_NPS_1=SA') & (responses.response > 10 ),'response'] = np.nan
				responses.ix[(responses.question_type == '10pt_NPS_1=SA'),'response'] = 11 - responses.ix[(responses.question_type == '10pt_NPS_1=SA'),'response']
				responses.ix[(responses.question_type == '11pt_NPS_1=SA') & (responses.response > 11 ),'response'] = np.nan
				responses.ix[(responses.question_type == '11pt_NPS_1=SA'),'response'] = 12 - responses.ix[(responses.question_type == '11pt_NPS_1=SA'),'response'] -1
				responses.ix[(responses.question_type == '7pt_7=SA') & (responses.response > 7 ),'response'] = np.nan
				responses.ix[(responses.question_type == '10pt_NPS_10=SA') & (responses.response > 10 ),'response'] = np.nan

			else:
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

		#Add sample size if it's not one of the cuts already
		if 'is_confidential' in self.responses.columns and 'sample_size' not in result_types:
			result_types.append('sample_size')

		if type(cut_demographic) == list:
			for cut in cut_demographic:
				if cut != []:
					assert cut in self.demographic_data.columns, "Expected " + cut + " to be a header in demographics, but it isn't there"
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
				aggregation_calulation = nfv_copy.ix[nfv_copy.net_formatted_value.notnull(),:].groupby(cut_groupings).aggregate(len).rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()

			aggregation_calulation['result_type'] = result_type
			aggregation_calulations_list.append(aggregation_calulation)


		all_results = pd.concat(aggregation_calulations_list)
		#Determine which questions have fewer than 5 respondents and are confidential
		if 'is_confidential' in all_results.columns:
			all_results = all_results.set_index(cut_groupings)
			nfv = nfv.set_index(cut_groupings)
			less_than_5_sample_size_index = all_results.ix[(all_results.result_type=='sample_size') & (all_results.aggregation_value < 5)].index
			confidential_questions = nfv.ix[nfv.is_confidential==1].index
			# all_results.ix[all_results.index.isin(less_than_5_sample_size_index) & all_results.index.isin(confidential_questions) & (all_results.result_type != 'sample_size'),'aggregation_value'] = np.nan
			all_results.ix[all_results.index.isin(less_than_5_sample_size_index) & all_results.index.isin(confidential_questions) & (all_results.result_type != 'sample_size'),'aggregation_value'] = np.nan
			all_results = all_results.reset_index()

		#Return just required columns
		return_columns = cut_groupings + ['aggregation_value','result_type']
		return pd.DataFrame(all_results,columns=return_columns)


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

		if len(cuts) == 0:
			blank_df = pd.DataFrame({'question_code':self.responses.question_code.unique().tolist()})
			blank_df['aggregation_value'] = ''
			blank_df['result_type'] = 'significance_value'
			return blank_df
		
		cuts, comparison_cuts, base_results, comparison_results = self.aggregations_for_net_significance(cuts=cuts)
		base_results = base_results.set_index(cuts + ['question_code','result_type'])
		base_results = pd.Series(base_results['aggregation_value'],index = base_results.index).unstack()
		comparison_results = comparison_results.set_index(comparison_cuts  + ['question_code','result_type'])
		comparison_results = pd.Series(comparison_results['aggregation_value'],index = comparison_results.index).unstack()
		comparison_results = comparison_results.rename(columns={'sample_size':'comp_sample_size',
																'strong_count':'comp_strong_count',
																'weak_count':'comp_weak_count'})
		self.counts_for_significance = base_results.reset_index().set_index(comparison_cuts + ['question_code']).join(comparison_results).reset_index().set_index(cuts + ['question_code'])
		return self.bootstrap_result_from_frequency_table(self.counts_for_significance)

	def bootstrap_result_from_frequency_table(self,freq_table,**kwargs):
		assert type(freq_table) == pd.DataFrame
		df = freq_table
		bootstrap_samples = 5000
		assert {'sample_size','strong_count','weak_count','comp_sample_size','comp_strong_count','comp_weak_count'} <= set(df.columns)
		df['aggregation_value'] = ''
		df['result_type'] = 'significance_value'
		for index_item in df.index:
			if df.ix[index_item,'sample_size'] < 5:
				df.ix[index_item,'aggregation_value'] = 'S'
				continue
			pop_1_sample_size = df.ix[index_item,'comp_sample_size'] - df.ix[index_item,'sample_size']

			if pop_1_sample_size == 0:#Meaning that subset is identical to the comparison
				continue
			pop_1_strong_count = df.ix[index_item,'comp_strong_count'] - df.ix[index_item,'strong_count']
			pop_1_weak_count = df.ix[index_item,'comp_weak_count'] - df.ix[index_item,'weak_count']

			pop_2_sample_size = df.ix[index_item,'sample_size']
			pop_2_strong_count = df.ix[index_item,'strong_count']
			pop_2_weak_count = df.ix[index_item,'weak_count']

			sum_of_count_distributions = poisson.ppf(0.75,pop_2_strong_count)+poisson.ppf(0.75,pop_2_weak_count)
			if sum_of_count_distributions < pop_2_sample_size * 1.1:#Reasonable cutoff based on simulations
				#Skellam modeled significance
				h0_net_count_interval = skellam.interval(0.95,(pop_1_strong_count / pop_1_sample_size) * pop_2_sample_size, (pop_1_weak_count / pop_1_sample_size) * pop_2_sample_size)
				actual_net_count_interval = pop_2_strong_count - pop_2_weak_count
				if actual_net_count_interval < h0_net_count_interval[0]:
					df.ix[index_item,'aggregation_value'] = 'L'
				elif actual_net_count_interval > h0_net_count_interval[1]:
					df.ix[index_item,'aggregation_value'] = 'H'
			else:

				#Create arrays of strong counts
				pop_1_rand_strong_counts = []

				if pop_1_strong_count == pop_1_sample_size or pop_1_strong_count == 0:
					pop_1_rand_strong_counts = [pop_1_strong_count for i in range(bootstrap_samples)]
				else:
					pop_1_rand_strong_counts = np.random.binomial(pop_1_sample_size,pop_1_strong_count/pop_1_sample_size,bootstrap_samples)

				pop_2_rand_strong_counts = []

				if pop_2_strong_count == pop_2_sample_size or pop_2_strong_count == 0:
					pop_2_rand_strong_counts = [pop_2_strong_count for i in range(bootstrap_samples)]
				else:
					pop_2_rand_strong_counts = np.random.binomial(pop_2_sample_size,pop_2_strong_count/pop_2_sample_size,bootstrap_samples)

				#Generate leftover weak percents
				pop_1_leftover_weak_p = 0
				if pop_1_sample_size > pop_1_strong_count:
					pop_1_leftover_weak_p = pop_1_weak_count / ( pop_1_sample_size - pop_1_strong_count )

				pop_2_leftover_weak_p = 0
				if pop_2_sample_size > pop_2_strong_count:
					pop_2_leftover_weak_p = pop_2_weak_count / ( pop_2_sample_size - pop_2_strong_count )

				#Generate weak and net values for each population
				pop_1_rand_weak_counts = []

				for pop_1_rand_strong in pop_1_rand_strong_counts:
					if pop_1_leftover_weak_p == 0 or pop_1_leftover_weak_p == 1 or pop_1_sample_size == pop_1_rand_strong:
						pop_1_rand_weak_counts.append(pop_1_sample_size - pop_1_rand_strong)
					else:
						pop_1_rand_weak_counts.append(np.random.binomial(pop_1_sample_size - pop_1_rand_strong,pop_1_leftover_weak_p,1))

				pop_2_rand_weak_counts = []

				for pop_2_rand_strong in pop_2_rand_strong_counts:
					if pop_2_leftover_weak_p == 0 or pop_2_leftover_weak_p == 1 or pop_2_sample_size == pop_2_rand_strong:
						pop_2_rand_weak_counts.append(pop_2_sample_size - pop_2_rand_strong)
					else:
						pop_2_rand_weak_counts.append(np.random.binomial(pop_2_sample_size - pop_2_rand_strong,pop_2_leftover_weak_p,1))

				#Assemble nets
				bs = pd.DataFrame({
					'pop_1_strong':pop_1_rand_strong_counts,
					'pop_1_weak':pop_1_rand_weak_counts,
					'pop_2_strong':pop_2_rand_strong_counts,
					'pop_2_weak':pop_2_rand_weak_counts})

				bs['pop_1_net'] = (bs.pop_1_strong - bs.pop_1_weak) / pop_1_sample_size
				bs['pop_2_net'] = (bs.pop_2_strong - bs.pop_2_weak) / pop_2_sample_size

				#Determine greater percents
				bs['pop_2_greater'] = 0
				bs.ix[bs.pop_1_net < bs.pop_2_net,'pop_2_greater'] = 1
				pop_2_greater_percent = bs.pop_2_greater.mean()

				if pop_2_greater_percent > 0.975:
					df.ix[index_item,'aggregation_value'] = 'H'
				if pop_2_greater_percent < 0.025:
					df.ix[index_item,'aggregation_value'] = 'L'

		return pd.DataFrame(df,columns =['aggregation_value','result_type'])