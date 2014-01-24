import pandas as pd
import logging
import numpy as np
import pdb
from scipy.stats import poisson, skellam
import copy
import gc

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):		
		responses = pd.DataFrame(kwargs.pop('responses',dict())).convert_objects(convert_numeric=True)
		assert not responses.empty
		if 'net_formatted_value' not in responses.columns or responses['net_formatted_value'].notnull().sum() == 0:
			responses['net_formatted_value'] = np.nan
			if 'question_type' in responses.columns:
				#Map NFVs
				map_7pt_SA_to_net = {7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
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
		self._results_with_dimensions = pd.DataFrame()
		# self.question_types_to_compute_significance_for = {'7pt_1=SA','10pt_NPS_1=SA','7pt_7=SA','11pt_NPS_1=SA','10pt_NPS_10=SA'}

	def results_with_dimensions():
		doc = "The results_with_dimensions property."
		def fget(self):
			if self.demographic_data.empty:
				return self.responses
			else:
				if self._results_with_dimensions.empty:
					assert 'respondent_id' in self.responses, "Expected respondent_id column in responses"
					assert 'respondent_id' in self.demographic_data, "Expected respondent_id column in demographic_data"
					if 'survey_code' in self.demographic_data.columns and 'survey_code' in self.responses.columns:
						self._results_with_dimensions = self.responses.set_index(['respondent_id','survey_code']).join(self.demographic_data.set_index(['respondent_id','survey_code']), how = 'outer').reset_index()
					else:
						self._results_with_dimensions = self.responses.set_index('respondent_id').join(self.demographic_data.set_index('respondent_id'), how = 'outer').reset_index()
				return self._results_with_dimensions
		def fset(self, value):
			self._results_with_dimensions = value
		def fdel(self):
			del self._results_with_dimensions
		return locals()
	results_with_dimensions = property(**results_with_dimensions())

	# @profile
	def compute_aggregation(self,**kwargs):
		cut_demographic = kwargs.pop('cut_demographic', None)
		result_type = kwargs.pop('result_type',None)
		composite_questions = kwargs.pop('composite_questions',None)
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

		cut_groupings = ['question_code']
		cut_demographic_list = []
		if cut_demographic != None:
			assert type(cut_demographic) == str or type(cut_demographic) == list
			if type(cut_demographic) == str:
				cut_demographic_list = [cut_demographic]
			else:
				cut_demographic_list = cut_demographic
			cut_groupings = cut_groupings + cut_demographic_list

		columns_to_keep = copy.deepcopy(cut_groupings)
		# nfv = self.results_with_dimensions.copy()
		results_columns = self.results_with_dimensions.columns
		if 'net_formatted_value' in results_columns:
			columns_to_keep.append('net_formatted_value')
		if 'response' in results_columns:
			columns_to_keep.append('response')
		if 'is_confidential' in results_columns:
			columns_to_keep.append('is_confidential')
		if 'question_type' in results_columns:
			columns_to_keep.append('question_type')
		nfv = self.results_with_dimensions.loc[:,columns_to_keep]
		# logging.debug("Results with dimensions for cut_demographic " + str(cut_demographic) + " are\n" + str(nfv.head()))

		aggregation_calulations_list = list()
		for result_type in result_types:
			nfv_copy = nfv.copy()
			# logging.debug("Computing aggregation for result type "+ result_type + " and cuts "+ str(cut_groupings))
			# logging.debug("Responses columns are " + str(nfv))
			assert result_type in {'net','strong','weak','raw_average','sample_size','strong_count','weak_count'}, "No calculation defined for result_type " + result_type
			aggregation_calulation = pd.DataFrame()
			if result_type == 'net':
				aggregation_calulation = nfv_copy.groupby(cut_groupings).mean().rename(columns={'net_formatted_value':'aggregation_value'}).reset_index()
				# logging.debug("Net results are\n" + str(aggregation_calulation.head()))
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
			aggregation_calulation = self.add_composite_question_calculation(composite_questions,aggregation_calulation,cut_demographic_list)
			aggregation_calulation['result_type'] = result_type
			aggregation_calulations_list.append(aggregation_calulation)

		#Add categorical responses
		categorical_calculation = pd.DataFrame()
		if 'question_type' in nfv.columns:
			question_types = nfv.question_type.unique()
			if 'Categorical_response' in question_types or 'Ordered_response' in question_types:
				categorical_calculation = nfv.ix[nfv.question_type.isin(['Categorical_response','Ordered_response'])].groupby(cut_groupings + ['response']).aggregate(len).reset_index().rename(columns={'question_type':'aggregation_value','response':'result_type'})
				categorical_calculation_samp_size = categorical_calculation.groupby(cut_groupings).sum().rename(columns={'aggregation_value':'sample_size'})['sample_size']
				categorical_calculation = categorical_calculation.set_index(cut_groupings).join(categorical_calculation_samp_size).reset_index()
				categorical_calculation.aggregation_value = categorical_calculation.aggregation_value / categorical_calculation.sample_size
				categorical_calculation.result_type = categorical_calculation.result_type.astype(int).astype(str)

		all_results = pd.concat(aggregation_calulations_list + [categorical_calculation])
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
		# logging.debug("Data returned is\n" + str(pd.DataFrame(all_results,columns=return_columns).head()))
		gc.collect()
		return pd.DataFrame(all_results,columns=return_columns)

	def add_composite_question_calculation(self,composite_questions,aggregation_calulation,cut_demographic_list):
		# logging.debug("Adding composite questions for " + str(composite_questions))
		if composite_questions is not None:
			for question, components in composite_questions.items():
				composite_computation = pd.DataFrame()
				if len(cut_demographic_list) == 0:
					assert 'aggregation_value' in aggregation_calulation.columns, "Missing aggregation_value " + str(aggregation_calulation)
					composite_output = aggregation_calulation.ix[aggregation_calulation.question_code.isin(components)].mean()['aggregation_value']
					aggregation_calulation = pd.concat([aggregation_calulation,pd.DataFrame({'question_code':[question],'aggregation_value':[composite_output]})])
				else:
					composite_computation = aggregation_calulation.ix[aggregation_calulation.question_code.isin(components)].groupby(cut_demographic_list).mean().reset_index()
					composite_computation['question_code'] = question
					aggregation_calulation = pd.concat([aggregation_calulation,composite_computation])
		return aggregation_calulation


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
		if cuts[0] == 'survey_code':
			comparison_cuts = ['survey_code'] + cuts[2:]

		base_results = self.compute_aggregation(cut_demographic=cuts,result_type=["sample_size","strong_count","weak_count"],**kwargs)
		comparison_results = self.compute_aggregation(cut_demographic=comparison_cuts,result_type=["sample_size","strong_count","weak_count"],**kwargs)
		return (cuts, comparison_cuts,base_results,comparison_results)


	# @profile
	def bootstrap_net_significance(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		no_stat_significance_computation = kwargs.pop('no_stat_significance_computation',False)

		if len(cuts) == 0:
			blank_df = pd.DataFrame({'question_code':self.responses.question_code.unique().tolist()})
			blank_df['aggregation_value'] = ''
			blank_df['result_type'] = 'significance_value'
			return blank_df

		cuts, comparison_cuts, base_results, comparison_results = self.aggregations_for_net_significance(cuts=cuts,**kwargs)

		if no_stat_significance_computation:
			df_with_no_results = self.compute_aggregation(cut_demographic=cuts,result_type='sample_size',**kwargs)
			df_with_no_results['result_type'] = 'significance_value'
			df_with_no_results['aggregation_value'] = ''
			df_with_no_results.set_index(cuts+['question_code'])
			return df_with_no_results
		base_results = base_results.ix[base_results['result_type'].isin(["sample_size","strong_count","weak_count"])]
		base_results = base_results.set_index(cuts + ['question_code','result_type'])
		base_results = pd.Series(base_results['aggregation_value'],index = base_results.index).unstack()
		comparison_results = comparison_results.ix[comparison_results['result_type'].isin(["sample_size","strong_count","weak_count"])]
		comparison_results = comparison_results.set_index(comparison_cuts  + ['question_code','result_type'])
		comparison_results = pd.Series(comparison_results['aggregation_value'],index = comparison_results.index).unstack()
		comparison_results = comparison_results.rename(columns={'sample_size':'comp_sample_size',
																'strong_count':'comp_strong_count',
																'weak_count':'comp_weak_count'})
		# logging.debug('Base results are\n' + str(base_results.head()))
		# logging.debug('comparison_results are\n' + str(comparison_results.head()))
		self.counts_for_significance = base_results.reset_index().set_index(comparison_cuts + ['question_code']).join(comparison_results).reset_index().set_index(cuts + ['question_code'])
		return self.bootstrap_result_from_frequency_table(self.counts_for_significance)

	# @profile
	def bootstrap_result_from_frequency_table(self,freq_table,**kwargs):
		assert type(freq_table) == pd.DataFrame
		df = freq_table
		bootstrap_samples = 5000
		#Testing results for NCS
		# df_test = df.copy()
		# df_test = df_test.reset_index()
		# logging.debug("Sample of results for NCS freq_table\n" + str(df_test.ix[df_test['question_code']=='NCS',:].head()))
		# logging.debug("Sample of results for CSI1 freq_table\n" + str(df_test.ix[df_test['question_code']=='CSI1',:].head()))
		#End testing results
		assert {'sample_size','strong_count','weak_count','comp_sample_size','comp_strong_count','comp_weak_count'} <= set(df.columns)
		df['aggregation_value'] = ''
		df['result_type'] = 'significance_value'
		df.ix[df.sample_size < 5,'aggregation_value'] = 'S'
		df['pop_1_sample_size'] = df.comp_sample_size - df.sample_size
		df['pop_1_strong_count'] = df.comp_strong_count - df.strong_count
		df['pop_1_weak_count'] = df.comp_weak_count - df.weak_count
		df['pop_2_sample_size'] = df.sample_size
		df['pop_2_strong_count'] = df.strong_count
		df['pop_2_weak_count'] = df.weak_count
		df.ix[df.pop_1_sample_size == 0,'aggregation_value'] = 'N'#Meaning that subset is identical to the comparison

		df_no_agg_value = df.ix[df.aggregation_value == '',:]
		dist_1 = pd.DataFrame(poisson.ppf(0.75,df_no_agg_value.pop_2_strong_count), index = df_no_agg_value.index)
		dist_2 = pd.DataFrame(poisson.ppf(0.75,df_no_agg_value.pop_2_weak_count), index = df_no_agg_value.index)
		# print("df is\n"+ str(df))
		# print(df_no_agg_value.pop_2_strong_count)
		# print(dist_1)
		# print(dist_2)
		df_no_agg_value['use_skellam'] = 0
		df_small = pd.DataFrame(df.ix[df.sample_size < 5,:],columns=['aggregation_value','result_type'])
		if len(dist_1.index) > 0:
			df_no_agg_value['sum_of_count_distributions'] =  dist_1 + dist_2
			df_no_agg_value.ix[df_no_agg_value.sum_of_count_distributions < (df_no_agg_value.pop_2_sample_size * 1.1),'use_skellam'] = 1
		else:
			return df_small

		df_skellam = df_no_agg_value.ix[df_no_agg_value.use_skellam==1]
		if len(df_skellam.index) > 0:
			df_skellam['mu1'] = (df_skellam.pop_1_strong_count / df_skellam.pop_1_sample_size) * df_skellam.pop_2_sample_size
			df_skellam['mu2'] = (df_skellam.pop_1_weak_count / df_skellam.pop_1_sample_size) * df_skellam.pop_2_sample_size
			df_skellam['obs'] = df_skellam.pop_2_strong_count - df_skellam.pop_2_weak_count
			df_skellam['p'] = pd.DataFrame(skellam.cdf(df_skellam.obs, df_skellam.mu1, df_skellam.mu2), index=df_skellam.index)
			df_skellam.ix[df_skellam.p > 0.975,'aggregation_value'] = 'H'
			df_skellam.ix[df_skellam.p < 0.025,'aggregation_value'] = 'L'

		df_bootstrap = df_no_agg_value.ix[df_no_agg_value.use_skellam==0]
		for index_item in df_bootstrap.index:
			pop_1_sample_size = df_bootstrap.ix[index_item,'pop_1_sample_size']

			pop_1_strong_count = df_bootstrap.ix[index_item,'pop_1_strong_count']
			pop_1_weak_count = df_bootstrap.ix[index_item,'pop_1_weak_count']

			pop_2_sample_size = df_bootstrap.ix[index_item,'sample_size']
			pop_2_strong_count = df_bootstrap.ix[index_item,'strong_count']
			pop_2_weak_count = df_bootstrap.ix[index_item,'weak_count']

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
				df_bootstrap.ix[index_item,'aggregation_value'] = 'H'
			if pop_2_greater_percent < 0.025:
				df_bootstrap.ix[index_item,'aggregation_value'] = 'L'
		# logging.debug("df_small is\n" + str(df.ix[df.sample_size < 5,:]))
		df_small = pd.DataFrame(df.ix[df.sample_size < 5,:],columns=['aggregation_value','result_type'])
		df_skellam = pd.DataFrame(df_skellam,columns=['aggregation_value','result_type'])
		df_bootstrap = pd.DataFrame(df_bootstrap,columns=['aggregation_value','result_type'])
		return pd.concat([df_small,df_skellam,df_bootstrap])