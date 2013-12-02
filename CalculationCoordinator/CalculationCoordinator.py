import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
import math
from openpyxl import load_workbook, cell
import copy
import logging

class CalculationCoordinator(object):
	"""docstring for CalculationCoordinator"""
	def __init__(self, **kwargs):
		self.results = kwargs.pop('results',None)
		self.demographic_data = kwargs.pop('demographic_data',None)
		self.config = kwargs.pop('config',None)
		self.computations_generated = dict()
		self.result_types = kwargs.pop('result_types',['net'])
		self.labels_for_cut_dimensions = dict()
		self.integers_for_cut_dimensions = dict()
		self.max_integer_used_for_integer_string = 1
		self.zero_integer_string = '0'
		self.ensure_combination_for_every_set_of_demographics = False

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

		if self.ensure_combination_for_every_set_of_demographics:
			calculations = self.modify_for_combinations_of_demographics(df=calculations,cuts=cuts)

		aggregation_key = tuple(cuts)

		self.computations_generated[aggregation_key] = calculations
		return calculations

	def modify_for_combinations_of_demographics(self, df, cuts):

		first_result_type = df.ix[0,'result_type']
		first_question_code = df.ix[0,'question_code']

		#Initialize with first list
		assert cuts[0] in self.demographic_data
		master_list_of_demographics = [ [item] for item in self.demographic_data[cuts[0]].unique().tolist()]

		#Create list of combinations to look for
		for i in range(len(cuts) - 1):
			cur_cut = cuts[i+1]
			assert cur_cut in self.demographic_data
			cur_cut_values = self.demographic_data[cur_cut].unique().tolist()
			value_set_for_cut = list()
			for value in cur_cut_values:
				list_to_add_onto = copy.deepcopy(master_list_of_demographics)
				for item in list_to_add_onto:
					item.append(value)
				value_set_for_cut += list_to_add_onto
			master_list_of_demographics = value_set_for_cut

		#Add new rows where necessary
		df_with_cut_index = df.copy().set_index(cuts)
		for value_set in master_list_of_demographics:
			if df_with_cut_index.index.isin([tuple(value_set)]).sum()== 0:
				dict_for_df = dict()
				for i in range(len(cuts)):
					dict_for_df[cuts[i]] = [value_set[i]]
				dict_for_df['result_type'] = [first_result_type]
				dict_for_df['question_code'] = [first_question_code]
				new_row = pd.DataFrame(dict_for_df)

				df = pd.concat([df,new_row])
		return df



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

		self.integer_string_length = math.floor(math.log(self.max_integer_used_for_integer_string,10) + 1 )

		self.format_string = "{0:0" + str(self.integer_string_length) + "d}"
		self.zero_integer_string = self.format_string.format(0)

		integer_strings_by_column = { column_key : { value : self.format_string.format(x) for (value, x) in values_dict.items()} for (column_key,values_dict) in values_by_column.items()}

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
		assert self.format_string.format(0) not in self.dimension_integer_mapping['integers']

		return df

	def get_integer_string_mapping(self, dimension):
		assert dimension in self.labels_for_cut_dimensions
		mapping_as_dict = self.labels_for_cut_dimensions[dimension]
		sorted_labels = sorted(mapping_as_dict.keys())
		return {'integer_strings':[mapping_as_dict[label] for label in sorted_labels],'labels':sorted_labels}

	def create_row_column_headers(self, df, cuts):
		# remaining_column = list(set(df.columns) - {'question_code','aggregation_value','result_type'})[0]
		df['row_heading'] = df.apply( lambda row: self.concat_row_items(row,cuts),axis=1)
		df['column_heading'] = df.apply(lambda x: '%s;%s' % (x['question_code'],x['result_type']),axis=1)
		assert df.row_heading.apply(len).min() > 0, "Blank row header created from cuts " + str(cuts) + "\n" + str(df)
		assert df.column_heading.apply(len).min() > 0, "Blank col header created from cuts " + str(cuts) + "\n" + str(df)
		return df

	def concat_row_items(self,row, columns):
		items_in_order = list()
		for column in columns:
			if column == None:
				items_in_order.append(self.zero_integer_string)
			else:
				assert column in row
				items_in_order.append(str(row[column]))
		return ";".join(items_in_order)

	def compute_cuts_from_config(self):
		assert self.config != None
		# assert type(self.config) == ConfigurationReader.ConfigurationReader
		all_aggregations = list()
		logging.debug("All cuts are " + str(self.config.cuts_to_be_created()))
		for cut_set in self.config.cuts_to_be_created():
			# logging.debug("Cut set is " + str(cut_set))
			df = self.compute_aggregation(cut_demographic=cut_set)
			df = self.replace_dimensions_with_integers(df)
			df = self.create_row_column_headers(df,cuts=cut_set)
			all_aggregations.append(pd.DataFrame(df,columns=['row_heading','column_heading','aggregation_value']))
		return_table = pd.concat(all_aggregations)
		return_table.row_heading = return_table.row_heading.map(self.adjust_zero_padding_of_heading)
		return_table.column_heading = return_table.column_heading.map(self.adjust_zero_padding_of_heading)
		assert len(return_table.row_heading.apply(len).unique()) == 1, "Not all row headings have the same length\n" + str(return_table.row_heading.unique())
		assert len(return_table.column_heading.apply(len).unique()) == 1, "Not all column headings have the same length\n" + str(return_table.column_heading.unique())
		return return_table.drop_duplicates()

	def export_to_excel(self,filename):
		# assert type(self.config) == ConfigurationReader.ConfigurationReader
		output_df = self.compute_cuts_from_config().set_index(['row_heading','column_heading'])
		logging.debug("Snapshot of master table " + str(output_df.head()))
		if not output_df.index.is_unique:
			df = output_df.reset_index()
			logging.warning("Duplicate headers found including: " + str(df.ix[df.duplicated(cols=['row_heading','column_heading']),:]))
		output_series = pd.Series(output_df['aggregation_value'],index = output_df.index)
		output_series.unstack().to_excel(filename, sheet_name='DisplayValues')

		wb = load_workbook(filename)

		#Add ranges for display_values tab
		dv_ws = wb.get_sheet_by_name('DisplayValues')
		range_width = dv_ws.get_highest_column() -1
		range_height = dv_ws.get_highest_row() - 1
		wb.create_named_range('disp_value_col_head',dv_ws,self.rc_to_range(row=0,col=1,width=range_width,height=1))
		wb.create_named_range('disp_value_row_head',dv_ws,self.rc_to_range(row=1,col=0,width=1,height=range_height))
		wb.create_named_range('dis_value_values',dv_ws,self.rc_to_range(row=1,col=1,width=range_width,height=range_height))

		ws = wb.create_sheet()
		ws.title = 'Lookups'
		cuts_menus = self.config.cuts_for_excel_menu()
		max_menu_length = max([len(menu) for menu in cuts_menus])
		for menu_i, cut_menu in enumerate(cuts_menus):
			for col_i, item in enumerate(cut_menu):
				ws.cell(row=menu_i, column = col_i).value = item


		#Added ranges for cut menu
		range_width = ws.get_highest_column() - 1
		range_height = ws.get_highest_row() -1 
		wb.create_named_range('cuts',ws,self.rc_to_range(row=0,col=0,width=1,height=range_height + 1))
		wb.create_named_range('cuts_config',ws,self.rc_to_range(row=0,col=0,width=range_width + 1,height=range_height + 1))

		next_column_to_use = ws.get_highest_column()
		dimension_titles = [dimension.title for dimension in self.config.all_dimensions()]
		dimension_titles.append('question_code')
		dimension_titles.append('result_type')
		for dimension_title in dimension_titles:
			mapping = self.get_integer_string_mapping(dimension_title)

			ws.cell(row=0, column = next_column_to_use).value = dimension_title
			for i in range(len(mapping['integer_strings'])):
				ws.cell(row=i+1, column = next_column_to_use).value = mapping['labels'][i]
				ws.cell(row=i+1, column = next_column_to_use+1).value = str(mapping['integer_strings'][i])
			next_column_to_use += 2

		#Add ranges for dimension menus
		col_for_default_menu = range_width
		range_width = ws.get_highest_column() -1
		wb.create_named_range('default_menu',ws,self.rc_to_range(row=1,col=col_for_default_menu,width=1,height=100))
		wb.create_named_range('cuts_head',ws,self.rc_to_range(row=0,col=col_for_default_menu + 1,
																width=range_width-col_for_default_menu,height=1))

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

	def adjust_zero_padding_of_heading(self, input_heading):
		values = input_heading.split(";")
		try:
			value_strings = [self.format_string.format(int(value)) for value in values]
		except:
			print(values)
		return ";".join(value_strings)

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