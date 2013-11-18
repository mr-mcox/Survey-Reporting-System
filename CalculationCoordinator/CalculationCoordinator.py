import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator
import math
from openpyxl import load_workbook

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

		values_by_column = { column_key : { value : format_string.format(x) for (value, x) in values_dict.items()} for (column_key,values_dict) in values_by_column.items()}

		#Map values to column
		for key, df in self.computations_generated.items():
			for column in df.columns:
				if column != 'aggregation_value':
					value_map = {key : value for (key, value) in values_by_column[column].items()}
					df[column] = df[column].map(value_map)

		#Create mapping to be able to convert back
		mapping = {'values':[],'integers':[]}
		for column, value_dict in values_by_column.items():
			for label, integer in value_dict.items():
				mapping['values'].append(label)
				mapping['integers'].append(integer)
		self.labels_for_cut_dimensions = values_by_column
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

	def export_to_excel(self,filename):
		output_df = self.master_aggregation.set_index(['row_heading','column_heading'])
		output_series = pd.Series(output_df['aggregation_value'],index = output_df.index)
		output_series.unstack().to_excel(filename, sheet_name='Sheet1')


		wb = load_workbook(filename)
		ws = wb.create_sheet()
		ws.title = 'Lookups'
		mapping = self.dimension_integer_mapping
		assert len(mapping['values']) == len(mapping['integers'])
		for i in range(len(mapping['values'])):
			ws.cell(row=i,column=0).value = mapping['values'][i]
			ws.cell(row=i,column=1).value = mapping['integers'][i]

		#Write cut dimensions integer strings
		cut_dimensions = self.labels_for_cut_dimensions.keys()
		for i, key in enumerate(cut_dimensions):
			ws.cell(row=0, column=i+2).value = key
			j = 1
			for label, integer_string in self.labels_for_cut_dimensions[key].items():
				ws.cell(row=j, column=i+2).value = integer_string
				j += 1
		wb.save(filename)