import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator
import math

class CalculationCoordinator(object):
	"""docstring for CalculationCoordinator"""
	def __init__(self, **kwargs):
		self.results = kwargs.pop('results',None)
		self.demographic_data = kwargs.pop('demographic_data',None)
		self.computations_generated = dict()	

	def get_aggregation(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		result_type = kwargs.pop('result_type',None)
		
		if type(cuts) != list:
			cuts = [cuts]
		aggregation_key = tuple(cuts + [result_type])

		assert aggregation_key in self.computations_generated
		return self.computations_generated[aggregation_key]

	def compute_aggregation(self,**kwargs):
		calculator = NumericOutputCalculator.NumericOutputCalculator(responses=self.results,demographic_data=self.demographic_data)
		calculations = calculator.compute_aggregation(**kwargs)

		cuts = kwargs.pop('cut_demographic',None)
		result_type = kwargs.pop('result_type',None)

		if type(cuts) != list:
			cuts = [cuts]
		aggregation_key = tuple(cuts + [result_type])

		self.computations_generated[aggregation_key] = calculations

	def replace_dimensions_with_integers(self):
		current_index = 0

		values_by_column = dict()
		#Collect all values by column
		for key, df in self.computations_generated.items():
			for column in df.columns:
				if column != 'aggregation_value':
					if column not in values_by_column:
						values_by_column[column] = dict()
					for value in df[column].unique():
						if value not in values_by_column[column]:
							values_by_column[column][value] = current_index
							current_index += 1

		format_string = "{0:0" + str(math.floor(current_index/10)) + "d}"

		#Map values to column
		for key, df in self.computations_generated.items():
			for column in df.columns:
				if column != 'aggregation_value':
					value_map = {key : format_string.format(value) for (key, value) in values_by_column[column].items()}
					df[column] = df[column].map(value_map)

		#Create mapping to be able to convert back
		mapping = {'values':[],'integers':[]}
		for column, value_dict in values_by_column.items():
			for label, integer in value_dict.items():
				mapping['values'].append(label)
				mapping['integers'].append(integer)
		self.dimension_integer_mapping = mapping

	def create_row_column_headers(self):
		for key, df in self.computations_generated.items():
			remaining_column = list(set(df.columns) - {'question_code','aggregation_value','result_type'})[0]
			df['row_heading'] = df[remaining_column]
			df['column_heading'] = df.apply(lambda x: '%s.%s' % (x['question_code'],x['result_type']),axis=1)

	def master_aggregation():
		doc = "The master_aggregation property."
		def fget(self):
			dfs = list()
			for key, df in self.computations_generated.items():
				dfs.append(pd.DataFrame(df,columns=['row_heading','column_heading','aggregation_value']))
			return pd.concat(dfs)
		def fset(self, value):
			self._master_aggregation = value
		def fdel(self):
			del self._master_aggregation
		return locals()
	master_aggregation = property(**master_aggregation())