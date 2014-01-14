import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
import math
from openpyxl import load_workbook, cell
import copy
import logging
import os
import gc

class CalculationCoordinator(object):
	"""docstring for CalculationCoordinator"""
	def __init__(self, **kwargs):
		self.results = kwargs.pop('results',None)
		self.demographic_data = kwargs.pop('demographic_data',None)
		if self.demographic_data is not None:
			self.demographic_data = self.demographic_data.set_index('respondent_id').applymap(str).fillna("Missing").reset_index()
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

		calculations = calculator.compute_aggregation(result_type=self.result_types,cut_demographic=cuts,**kwargs)

		if self.ensure_combination_for_every_set_of_demographics and len(cuts) > 0:
			logging.debug("Cuts passing to modify " + str(cuts))
			calculations = self.modify_for_combinations_of_demographics(df=calculations,cuts=cuts)

		aggregation_key = tuple(cuts)

		self.computations_generated[aggregation_key] = calculations
		return calculations

	def compute_significance(self,**kwargs):
		calculator = NumericOutputCalculator.NumericOutputCalculator(responses=self.results,demographic_data=self.demographic_data)
		assert type(self.result_types) == list
		orig_cuts = kwargs.pop('cut_demographic',None)
		if type(orig_cuts) != list:
			orig_cuts = [orig_cuts]
		cuts = [cut for cut in orig_cuts if cut != None]

		calculations = calculator.bootstrap_net_significance(cuts=cuts,**kwargs).reset_index()

		if self.ensure_combination_for_every_set_of_demographics and len(cuts) > 0:
			logging.debug("Cuts passing to modify " + str(cuts))
			calculations = self.modify_for_combinations_of_demographics(df=calculations,cuts=cuts)

		aggregation_key = tuple(cuts)

		# self.computations_generated[aggregation_key] = calculations
		return calculations

	def modify_for_combinations_of_demographics(self, df, cuts):
		df = df.reset_index()
		# logging.debug("Starting df is " + str(df.head()))
		# logging.debug("Starting df row is " + str(df.reset_index().ix[0,:]))
		first_result_type = df.ix[0,'result_type']
		# logging.debug("First result type is " + df.ix[0,'result_type'])
		first_question_code = df.ix[0,'question_code']
		if hasattr(self,'default_question'):
			first_question_code = self.default_question
		if hasattr(self,'default_result_type'):
			first_result_type = self.default_result_type

		#Initialize with first list
		assert len(cuts) > 0
		# logging.debug("Cuts are " + str(cuts))
		assert cuts[0] in self.demographic_data, cuts[0] + " not found in demographic_data"
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

		#Convert list to tuples
		master_list_of_demographics = {tuple(value_set) for value_set in master_list_of_demographics}

		#Remove all rows where dynamic dimension pairs don't exist
		if self.config is not None:
				all_dimensions = {dimension.title: dimension for dimension in self.config.all_dimensions()}
				position_of_cut = {cut: i for i, cut in enumerate(cuts)}
				for cur_cut in position_of_cut.keys():
					if cur_cut in all_dimensions and all_dimensions[cur_cut].dimension_type == 'dynamic' and all_dimensions[cur_cut].dynamic_parent_dimension in cuts:
						parent_dimension = all_dimensions[cur_cut].dynamic_parent_dimension
						position_of_parent = position_of_cut[parent_dimension]
						position_of_child = position_of_cut[cur_cut]
						df_for_dynamic = df.copy().set_index([parent_dimension,cur_cut])
						value_sets_to_remove = set()
						for value_set in master_list_of_demographics:
							dimension_combo_to_check_for = (value_set[position_of_parent],value_set[position_of_child])
							if df_for_dynamic.index.isin(dimension_combo_to_check_for).sum() == 0:
								value_sets_to_remove.add(value_set)
						for value_set in value_sets_to_remove:
							master_list_of_demographics.remove(value_set)

		#Add new rows where necessary
		df_with_cut_index = df.copy().set_index(cuts)
		for value_set in master_list_of_demographics:
			if df_with_cut_index.index.isin([tuple(value_set)]).sum()== 0:
				dict_for_df = dict()
				dict_for_df['result_type'] = [first_result_type]
				# logging.debug("First question code is " + first_question_code )
				dict_for_df['question_code'] = [first_question_code]
				new_row = pd.DataFrame(dict_for_df)
				# logging.debug("New row before adding cuts:\n" + str(new_row))
				for i in range(len(cuts)):
					new_row[cuts[i]] = value_set[i]
				logging.debug("New row after adding cuts:\n" + str(new_row))

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
				# logging.debug("Mapping values for column " + column + "\n" + str(value_map))
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
		assert dimension in self.labels_for_cut_dimensions, "Dimension " + dimension + " not present"
		mapping_as_dict = self.labels_for_cut_dimensions[dimension]
		sorted_labels = sorted(mapping_as_dict.keys())
		return {'integer_strings':[mapping_as_dict[label] for label in sorted_labels],'labels':sorted_labels}

	def create_row_column_headers(self, df, cuts):
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
		# logging.debug("All cuts are " + str(self.config.cuts_to_be_created()))
		#Set default question as not doing that seems to cause issues
		if 'show_questions' in self.config.config:
			self.default_question = self.config.config['show_questions'][0]
		if 'result_types' in self.config.config:
			self.result_types = self.config.config['result_types']
			self.default_result_type = self.result_types[0]
		cut_sets = self.config.cuts_to_be_created()
		for i, cut_set in enumerate(cut_sets):
			# logging.debug("Cut set is " + str(cut_set))
			df = pd.DataFrame()
			if 'composite_questions' in self.config.config:
				df = self.compute_aggregation(cut_demographic=cut_set,composite_questions=self.config.config['composite_questions'])
			else:
				df = self.compute_aggregation(cut_demographic=cut_set)

			#Remove samples sizes for questions that don't need them
			assert 'question_code' in df.columns
			logging.debug("question_code dtype is " + str(df.question_code.dtype))
			logging.debug("question_codes are " + str(df.question_code))
			questions_to_show_sample_size = df.question_code.unique().tolist()
			if 'show_sample_size_for_questions' in self.config.config:
				questions_to_show_sample_size = self.config.config['show_sample_size_for_questions']
			df = df.ix[(df.result_type != 'sample_size') | df.question_code.isin(questions_to_show_sample_size),:]

			#Remove questions that aren't specified
			questions_to_show = df.question_code.unique().tolist()
			if 'show_questions' in self.config.config:
				questions_to_show = self.config.config['show_questions']
			df = df.ix[df.question_code.isin(questions_to_show),:]
			df = self.replace_dimensions_with_integers(df)
			df = self.create_row_column_headers(df,cuts=cut_set)
			all_aggregations.append(pd.DataFrame(df,columns=['row_heading','column_heading','aggregation_value']))
			gc.collect()
			print("\rCompleted {0:.0f} % of basic computations".format(i/len(cut_sets)*100),end=" ")
		return_table = pd.concat(all_aggregations)
		return_table.row_heading = return_table.row_heading.map(self.adjust_zero_padding_of_heading)
		return_table.column_heading = return_table.column_heading.map(self.adjust_zero_padding_of_heading)
		assert len(return_table.row_heading.apply(len).unique()) == 1, "Not all row headings have the same length\n" + str(return_table.row_heading.unique())
		assert len(return_table.column_heading.apply(len).unique()) == 1, "Not all column headings have the same length\n" + str(return_table.column_heading.unique())
		return return_table.drop_duplicates()

	def compute_significance_from_config(self):
		assert self.config != None
		all_aggregations = list()
		#Set default question as not doing that seems to cause issues
		if 'show_questions' in self.config.config:
			self.default_question = self.config.config['show_questions'][0]
		self.default_result_type = 'significance_value'

		no_stat_significance_computation = False
		if 'no_stat_significance_computation' in self.config.config:
			 no_stat_significance_computation = True

		cut_sets = self.config.cuts_to_be_created()
		for i, cut_set in enumerate(cut_sets):
			df = pd.DataFrame()
			if 'composite_questions' in self.config.config:
				df = self.compute_significance(cut_demographic=cut_set,composite_questions=self.config.config['composite_questions'],no_stat_significance_computation=no_stat_significance_computation)
			else:
				df = self.compute_significance(cut_demographic=cut_set, no_stat_significance_computation=no_stat_significance_computation)			
			#Remove samples sizes for questions that don't need them
			assert 'question_code' in df.columns
			# logging.debug("question_code dtype is " + str(df.question_code.dtype))
			# logging.debug("question_codes are " + str(df.question_code))

			#Remove questions that aren't specified
			questions_to_show = df.question_code.unique().tolist()
			if 'show_questions' in self.config.config:
				questions_to_show = self.config.config['show_questions']
			df = df.ix[df.question_code.isin(questions_to_show),:]
			df = self.replace_dimensions_with_integers(df)
			df = self.create_row_column_headers(df,cuts=cut_set)
			all_aggregations.append(pd.DataFrame(df,columns=['row_heading','column_heading','aggregation_value']))
			gc.collect()
			print("\rCompleted {0:.0f} % of significance computations".format(i/len(cut_sets)*100),end=" ")
		return_table = pd.concat(all_aggregations)
		return_table.row_heading = return_table.row_heading.map(self.adjust_zero_padding_of_heading)
		return_table.column_heading = return_table.column_heading.map(self.adjust_zero_padding_of_heading)
		assert len(return_table.row_heading.apply(len).unique()) == 1, "Not all row headings have the same length\n" + str(return_table.row_heading.unique())
		assert len(return_table.column_heading.apply(len).unique()) == 1, "Not all column headings have the same length\n" + str(return_table.column_heading.unique())
		return return_table.drop_duplicates()

	def export_to_excel(self):
		# assert type(self.config) == ConfigurationReader.ConfigurationReader
		assert 'excel_template_file' in self.config.config
		self.ensure_combination_for_every_set_of_demographics = True
		filename = self.config.config['excel_template_file']

		#Output display values
		output_df = self.compute_cuts_from_config().set_index(['row_heading','column_heading'])
		# logging.debug("Snapshot of master table " + str(output_df.head()))
		if not output_df.index.is_unique:
			df = output_df.reset_index()
			duplicate_index_df = df.ix[df.duplicated(cols=['row_heading','column_heading']),:].set_index(['row_heading','column_heading'])
			logging.warning("Duplicate headers found including: " + str(output_df[output_df.index.isin(duplicate_index_df.index)].head()))
		output_df = output_df.reset_index().drop_duplicates(cols=['row_heading','column_heading'],take_last=False).set_index(['row_heading','column_heading'])
		output_series = pd.Series(output_df['aggregation_value'],index = output_df.index)
		output_series.unstack().to_excel('display_values.xlsx', sheet_name='DisplayValues')

		self.copy_sheet_to_workbook('display_values.xlsx','DisplayValues',filename)
		os.remove('display_values.xlsx')

		#Output significance values
		output_df = self.compute_significance_from_config().set_index(['row_heading','column_heading'])
		# logging.debug("Snapshot of master table " + str(output_df.head()))
		if not output_df.index.is_unique:
			df = output_df.reset_index()
			duplicate_index_df = df.ix[df.duplicated(cols=['row_heading','column_heading']),:].set_index(['row_heading','column_heading'])
			logging.warning("Duplicate headers found including: " + str(output_df[output_df.index.isin(duplicate_index_df.index)].head()))
		output_df = output_df.reset_index().drop_duplicates(cols=['row_heading','column_heading'],take_last=False).set_index(['row_heading','column_heading'])
		output_series = pd.Series(output_df['aggregation_value'],index = output_df.index)
		output_series.unstack().to_excel('significance_values.xlsx', sheet_name='SignificanceValues')

		self.copy_sheet_to_workbook('significance_values.xlsx','SignificanceValues',filename)
		os.remove('significance_values.xlsx')

		wb = load_workbook(filename)

		#Remove existing named ranges
		for range_name in wb.get_named_ranges():
			wb.remove_named_range(range_name)

		#Add ranges for display_values tab
		dv_ws = wb.get_sheet_by_name('DisplayValues')
		range_width = dv_ws.get_highest_column() -1
		range_height = dv_ws.get_highest_row() - 1
		wb.create_named_range('disp_value_col_head',dv_ws,self.rc_to_range(row=0,col=1,width=range_width,height=1))
		wb.create_named_range('disp_value_row_head',dv_ws,self.rc_to_range(row=1,col=0,width=1,height=range_height))
		wb.create_named_range('disp_value_values',dv_ws,self.rc_to_range(row=1,col=1,width=range_width,height=range_height))

		#Add ranges for significance_values tab
		dv_ws = wb.get_sheet_by_name('SignificanceValues')
		range_width = dv_ws.get_highest_column() -1
		range_height = dv_ws.get_highest_row() - 1
		wb.create_named_range('sig_value_col_head',dv_ws,self.rc_to_range(row=0,col=1,width=range_width,height=1))
		wb.create_named_range('sig_value_row_head',dv_ws,self.rc_to_range(row=1,col=0,width=1,height=range_height))
		wb.create_named_range('sig_value_values',dv_ws,self.rc_to_range(row=1,col=1,width=range_width,height=range_height))

		if 'Lookups' in wb.get_sheet_names():
			ws_to_del = wb.get_sheet_by_name('Lookups')
			wb.remove_sheet(ws_to_del)

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

		#Add dimension menus
		next_column_to_use = ws.get_highest_column()
		#TODO: Perhaps having a function call directly from config would be better than these structures?
		all_dimensions = {dimension.title: dimension for dimension in self.config.all_dimensions()}
		dimension_titles = [dimension.title for dimension in self.config.all_dimensions()]
		all_together_label_for_title = {dimension.title: dimension.all_together_label for dimension in self.config.all_dimensions()}
		dynamic_parent_dimension = {dimension.title: dimension.dynamic_parent_dimension for dimension in self.config.all_dimensions() if dimension.dimension_type=='dynamic'}
		dimension_titles.append('question_code')
		dimension_titles.append('result_type')
		for dimension_title in dimension_titles:
			mapping = {'labels':[],'integer_strings':[]}
			if dimension_title in all_dimensions and all_dimensions[dimension_title].is_composite:
				for component_dimension_title in all_dimensions[dimension_title].composite_dimensions:
					new_mapping = self.get_integer_string_mapping(component_dimension_title)
					mapping['labels'] = mapping['labels'] + new_mapping['labels']
					mapping['integer_strings'] = mapping['integer_strings'] + new_mapping['integer_strings']
			else:
				mapping = self.get_integer_string_mapping(dimension_title)

			ws.cell(row=0, column = next_column_to_use).value = dimension_title
			row_offset = 1
			if dimension_title in dynamic_parent_dimension:
				if dimension_title in all_together_label_for_title and all_together_label_for_title[dimension_title] is not None:
					ws.cell(row=row_offset, column = next_column_to_use).value = all_together_label_for_title[dimension_title]
					ws.cell(row=row_offset, column = next_column_to_use + 1 ).value = self.zero_integer_string
					row_offset = 2
				assert self.demographic_data is not None
				parent_dimension = dynamic_parent_dimension[dimension_title]
				assert parent_dimension in self.demographic_data.columns
				assert dimension_title in self.demographic_data.columns
				dimension_mapping = pd.DataFrame(self.demographic_data,columns=[parent_dimension,dimension_title]).drop_duplicates().sort(columns=[parent_dimension,dimension_title])
				integer_mapping = dict(zip(mapping['labels'],mapping['integer_strings']))
				i = 0
				for index, row_items in dimension_mapping.iterrows():
					ws.cell(row=i+row_offset, column = next_column_to_use).value = row_items[dimension_title]
					ws.cell(row=i+row_offset, column = next_column_to_use+1).value = integer_mapping[row_items[dimension_title]]
					ws.cell(row=i+row_offset, column = next_column_to_use+2).value = row_items[parent_dimension]
					i += 1
				next_column_to_use += 3
			else:
				if dimension_title in all_together_label_for_title and all_together_label_for_title[dimension_title] is not None:
					ws.cell(row=row_offset, column = next_column_to_use).value = all_together_label_for_title[dimension_title]
					ws.cell(row=row_offset, column = next_column_to_use + 1 ).value = self.zero_integer_string
					row_offset = 2
				for i in range(len(mapping['integer_strings'])):
					ws.cell(row=i+row_offset, column = next_column_to_use).value = mapping['labels'][i]
					ws.cell(row=i+row_offset, column = next_column_to_use+1).value = str(mapping['integer_strings'][i])
				next_column_to_use += 2

		#Add ranges for dimension menus
		col_for_default_menu = range_width
		range_width = ws.get_highest_column() -1
		wb.create_named_range('default_menu',ws,self.rc_to_range(row=1,col=col_for_default_menu,width=1,height=100))
		wb.create_named_range('default_mapping',ws,self.rc_to_range(row=1,col=col_for_default_menu,width=2,height=100))
		wb.create_named_range('default_menu_start',ws,self.rc_to_range(row=1,col=col_for_default_menu))
		wb.create_named_range('cuts_head',ws,self.rc_to_range(row=0,col=col_for_default_menu + 1,
																width=range_width-col_for_default_menu,height=1))

		#Add zero string value
		next_column_to_use = ws.get_highest_column()
		ws.cell(row=0,column=next_column_to_use).value = self.zero_integer_string
		wb.create_named_range('zero_string',ws,self.rc_to_range(row=0,col=next_column_to_use))

		wb.save(filename)

	def adjust_zero_padding_of_heading(self, input_heading):
		values = input_heading.split(";")
		value_strings = [self.format_string.format(int(value)) for value in values]
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

	def copy_sheet_to_workbook(self,src_wb_name,src_ws_name,dest_wb_name):
		src_wb = load_workbook(src_wb_name)
		assert src_ws_name in src_wb.get_sheet_names()
		src_ws = src_wb.get_sheet_by_name(src_ws_name)

		dest_wb = load_workbook(dest_wb_name)

		if src_ws_name in dest_wb.get_sheet_names():
			ws_to_del = dest_wb.get_sheet_by_name(src_ws_name)
			dest_wb.remove_sheet(ws_to_del)

		dest_ws = dest_wb.create_sheet()
		dest_ws.title = src_ws_name

		for i in range(src_ws.get_highest_column()):
			for j in range(src_ws.get_highest_row()):
				dest_ws.cell(row=j,column=i).value = src_ws.cell(row=j,column=i).value

		dest_wb.save(dest_wb_name)