import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
import math
from openpyxl import load_workbook, cell

class CalculationCoordinator(object):
	"""docstring for CalculationCoordinator"""
	def __init__(self, **kwargs):
		self.results = kwargs.pop('results',None)
		self.demographic_data = kwargs.pop('demographic_data',None)
		self.computations_generated = dict()
		self.result_types = kwargs.pop('result_types',['net'])
		self.labels_for_cut_dimensions = dict()
		self.integers_for_cut_dimensions = dict()
		self.max_integer_used_for_integer_string = 1 

	def get_aggregation(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		
		if type(cuts) != list:
			cuts = [cuts]
		aggregation_key = tuple(cuts)

		assert aggregation_key in self.computations_generated
		return self.computations_generated[aggregation_key]

	def compute_aggregation(self,**kwargs):
		calculator = NumericOutputCalculator.NumericOutputCalculator(responses=self.results,demographic_data=self.demographic_data)
		assert type(self.result_types) == list
		orig_cuts = kwargs.pop('cut_demographic',None)
		if type(orig_cuts) != list:
			orig_cuts = [orig_cuts]
		cuts = [cut for cut in orig_cuts if cut != None]

		calcs = list()
		for result_type in self.result_types:
			calcs.append(calculator.compute_aggregation(result_type=result_type,cut_demographic=cuts,**kwargs))
		calculations = pd.concat(calcs)

		aggregation_key = tuple(cuts)

		self.computations_generated[aggregation_key] = calculations

	def replace_dimensions_with_integers(self, df = None):

		values_by_column = self.integers_for_cut_dimensions
		#Collect all values by column
		for column in df.columns:
			if column != 'aggregation_value':
				if column not in values_by_column:
					values_by_column[column] = dict()
				for value in df[column].unique():
					if value not in values_by_column[column]:
						values_by_column[column][value] = self.max_integer_used_for_integer_string
						self.max_integer_used_for_integer_string += 1

		format_string = "{0:0" + str(math.floor(self.max_integer_used_for_integer_string/10)) + "d}"

		integer_strings_by_column = { column_key : { value : format_string.format(x) for (value, x) in values_dict.items()} for (column_key,values_dict) in values_by_column.items()}

		#Map values to column
		for column in df.columns:
			if column != 'aggregation_value':
				value_map = {key : value for (key, value) in integer_strings_by_column[column].items()}
				df[column] = df[column].map(value_map)

		#Create mapping to be able to convert back
		mapping = dict()
		for column, value_dict in integer_strings_by_column.items():
			for label, integer in value_dict.items():
				mapping[integer] = label
		self.labels_for_cut_dimensions = integer_strings_by_column
		self.integers_for_cut_dimensions = values_by_column
		self.dimension_integer_mapping = {
			'integers': sorted(mapping.keys()),
			'values': [mapping[key] for key in sorted(mapping.keys())] 
		}
		assert format_string.format(0) not in self.dimension_integer_mapping['integers']

		return df

	def get_integer_string_mapping(self, dimension):
		assert dimension in self.labels_for_cut_dimensions
		mapping_as_dict = self.labels_for_cut_dimensions[dimension]
		sorted_labels = sorted(mapping_as_dict.keys())
		return {'integer_strings':[mapping_as_dict[label] for label in sorted_labels],'labels':sorted_labels}

	def create_row_column_headers(self):
		for key, df in self.computations_generated.items():
			remaining_column = list(set(df.columns) - {'question_code','aggregation_value','result_type'})[0]
			df['row_heading'] = df[remaining_column]
			df['column_heading'] = df.apply(lambda x: '%s;%s' % (x['question_code'],x['result_type']),axis=1)

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
		assert type(self.config) == ConfigurationReader.ConfigurationReader
		output_df = self.master_aggregation.set_index(['row_heading','column_heading'])
		output_series = pd.Series(output_df['aggregation_value'],index = output_df.index)
		output_series.unstack().to_excel(filename, sheet_name='Sheet1')

		wb = load_workbook(filename)
		ws = wb.create_sheet()
		ws.title = 'Lookups'
		cuts_menus = self.config.cuts_for_excel_menu()
		max_menu_length = max([len(menu) for menu in cuts_menus])
		for menu_i, cut_menu in enumerate(cuts_menus):
			for col_i, item in enumerate(cut_menu):
				ws.cell(row=menu_i, column = col_i).value = item

		next_column_to_use = ws.get_highest_column()
		for dimension in self.config.all_dimensions():
			dimension_title = dimension.title
			mapping = self.get_integer_string_mapping(dimension_title)

			ws.cell(row=0, column = next_column_to_use).value = dimension_title
			for i in range(len(mapping['integer_strings'])):
				ws.cell(row=i+1, column = next_column_to_use).value = mapping['labels'][i]
				ws.cell(row=i+1, column = next_column_to_use+1).value = str(mapping['integer_strings'][i])
			next_column_to_use += 2
		# mapping = self.dimension_integer_mapping
		# assert len(mapping['values']) == len(mapping['integers'])
		# for i in range(len(mapping['values'])):
		# 	ws.cell(row=i,column=0).value = mapping['integers'][i]
		# 	ws.cell(row=i,column=1).value = mapping['values'][i]
		# 	ws.cell(row=i,column=2).value = mapping['integers'][i]

		# #Write cut dimensions integer strings
		# cut_dimensions = self.labels_for_cut_dimensions.keys()
		# for i, key in enumerate(cut_dimensions):
		# 	ws.cell(row=0, column=i+3).value = key
		# 	j = 1
		# 	for label, integer_string in self.labels_for_cut_dimensions[key].items():
		# 		ws.cell(row=j, column=i+3).value = integer_string
		# 		j += 1
		wb.save(filename)

	def rc_to_range(self,row,col,**kwargs):
		height = kwargs.pop('height',None)
		width = kwargs.pop('width',None)
		if height == None:
			return cell.get_column_letter(col + 1) + str(row+1)
		else:
			assert width != None
			start_cell =  cell.get_column_letter(col + 1) + str(row+1)
			end_cell = cell.get_column_letter(col + width) + str(row+height)
			return start_cell + ":" + end_cell