from pytest_bdd import scenario, given, when, then
import re
import pandas as pd
import numpy as np
import re
import os
from openpyxl import load_workbook
from openpyxl import Workbook
from unittest import mock
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader

@scenario('convert_demograph_text_to_number.feature', 'When multiple cuts are run, they are stored by tuple')
def test_store_cuts_by_tuple():
    pass

@given(re.compile('net formatted values\n(?P<text_table>.+)', re.DOTALL))
def coordinator_with_net_formatted_values(text_table):
	coordinator = CalculationCoordinator.CalculationCoordinator()
	coordinator.results = pd.DataFrame(import_table_data(text_table))
	return coordinator

@given(re.compile('demographic data passed to coordinator\n(?P<text_table>.+)', re.DOTALL))
def demographic_data(text_table, coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.demographic_data = pd.DataFrame(import_table_data(text_table))

@when('compute net with cut_demographic = region is run')
def compute_net_with_region(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.compute_aggregation(cut_demographic='region')

@when('compute net with cut_demographic = region and gender is run')
def compute_net_with_region_and_gender(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.result_types =['net']
	coordinator_with_net_formatted_values.compute_aggregation(cut_demographic=['region','gender'])

@then('computations_generated has a length of 2')
def computation_generated_length_2(coordinator_with_net_formatted_values):
	assert len(coordinator_with_net_formatted_values.computations_generated.keys()) == 2

@then('the display_value including region for question_code 1 and region "Atlanta" is 0.5')
def check_Atlanta_result_for_question_code_1(coordinator_with_net_formatted_values):
	results = coordinator_with_net_formatted_values.get_aggregation(cuts='region')
	assert results.set_index(['question_code','region']).loc[(1,'Atlanta'),'aggregation_value'] == 0.5

@scenario('convert_demograph_text_to_number.feature', 'Identify all demographic columns across multiple cuts')
def test_identify_demographic_columns_across_multiple_cuts():
    pass

@given('a generic coordinator')
def generic_coordinator():
	return CalculationCoordinator.CalculationCoordinator()

@given('computations generated with a cut by gender')
def computation_cut_by_gender():
	return pd.DataFrame({'question_code':[0,1,1],'gender':['Male','Female',"Male"]})

@given('computations generated with a cut by region')
def computation_cut_by_region():
	return pd.DataFrame({'question_code':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]})

@when('replace_dimensions_with_integers for both computations is run')
def replace_dimensions_with_integers_for_computations(generic_coordinator, computation_cut_by_gender, computation_cut_by_region):
	results = [generic_coordinator.replace_dimensions_with_integers(computation_cut_by_gender), generic_coordinator.replace_dimensions_with_integers(computation_cut_by_region)]

@then('columns of computations_generated are strings with filled numbers')
def check_columns_are_string_filled_numbers(generic_coordinator, computation_cut_by_gender, computation_cut_by_region):
	results = [generic_coordinator.replace_dimensions_with_integers(computation_cut_by_gender), generic_coordinator.replace_dimensions_with_integers(computation_cut_by_region)]
	for df in results:
		for column in df.columns:
			if column != 'aggregation_value':
				for value in df[column].unique():
					assert type(value) == str
					assert re.search('^\d+$',value) != None
	values = list()
	for df in results:
		for column in df.columns:
			print(df)
			if column != 'aggregation_value':
				values = values + df[column].unique().tolist()
	values = set(values)
	print(values)
	assert len(values) == 6


@when('replace_dimensions_with_integers is run')
def run_replace_dimensions_with_integers(generic_coordinator):
	generic_coordinator.replace_dimensions_with_integers()

@then('same number of unique values in dimension columns exists before and after')
def do_nothing():
	pass

@scenario('convert_demograph_text_to_number.feature', 'After changing all dimensions to numbers, we have a mapping that we can re-assemble the cuts with')
def test_map_numbers_back_to_strings():
    pass

@scenario('convert_demograph_text_to_number.feature', "Mapping is sorted by integer string so that excel doesn't need to re-sort")
def test_mapping_sort():
    pass

@then('there is a mapping of the values back to numbers')
def check_mapping_back_to_numbers(generic_coordinator, computation_cut_by_gender, computation_cut_by_region):
	mapping = generic_coordinator.dimension_integer_mapping
	assert {'Male','Atlanta'} <= set(mapping['values'])

@then('the mapping is in order by integer strings')
def check_mapping_in_order(generic_coordinator):
	integers = generic_coordinator.dimension_integer_mapping['integers']
	assert integers == sorted(integers)

@then('the values column corresponds with the appropriate integer strings')
def check_values_column_corresponds_to_integers(generic_coordinator):
	values_by_column = generic_coordinator.labels_for_cut_dimensions
	dim = generic_coordinator.dimension_integer_mapping
	integers = dim['integers']
	for column, value_dict in values_by_column.items():
		for label, integer in value_dict.items():
			for i, string in enumerate(integers):
				if string == integer:
					assert dim['values'][i] == label

@scenario('convert_demograph_text_to_number.feature', "CalcCoordinator computes multiple result types at the same time")
def test_multiple_result_types_simultaneously():
    pass

@given('CalcCoordinator result types of net, strong and weak')
def result_types_of_net_strong_weak(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.result_types = ['net','strong','weak']

@then('result_type of results includes net, strong and weak')
def check_result_type_includes_net_strong_weak(coordinator_with_net_formatted_values):
	results = coordinator_with_net_formatted_values.get_aggregation(cuts='region')
	assert set(results.result_type.unique()) == {'net','strong','weak'}

@scenario('convert_demograph_text_to_number.feature', "CalcCoordinator accepts a list with blanks for cuts")
def test_accepts_list_with_blanks_for_cuts():
    pass

@when('compute aggregation with cut_demographic = [gender,None,region] is run')
def compute_aggreatoin_with_cut_demographic_cut_by_gender_region(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.compute_aggregation(cut_demographic=['gender',None,'region'])

@then('the display_value including region for question_code 1 and region "Atlanta" and gender "Female" is 0.5')
def check_display_value_for_Atlanta_and_Female(coordinator_with_net_formatted_values):
	results = coordinator_with_net_formatted_values.get_aggregation(cuts=['gender','region'])
	assert results.set_index(['question_code','region','gender']).loc[(1,'Atlanta','Female'),'aggregation_value'] == 0.5

@scenario('convert_demograph_text_to_number.feature', "Assemble row and column headings for a simple case")
def test_assemble_row_column_headings():
    pass

@given(re.compile('data frame of compuations\n(?P<text_table>.+)', re.DOTALL))
def data_frame_of_computations(text_table):
	return pd.DataFrame(import_table_data(text_table))

@when('create_row_column_headers is run with cuts = [gender, region]')
def create_row_column_headers_run_with_cuts():
	pass
	# context.result  = context.coordinator.create_row_column_headers(context.df, ['gender','region'])

@then(re.compile('result of create_row_column_headers with cuts = \[gender, None\] has column "(?P<column>.+)" with value "(?P<value>.+)"'),converters=dict(column=str,value=str))
def result_of_create_row_column_headers(data_frame_of_computations,generic_coordinator,column,value):
	assert value in generic_coordinator.create_row_column_headers(data_frame_of_computations, ['gender','region'])[column].unique().tolist()

@scenario('convert_demograph_text_to_number.feature', "Row and column header strings should be padded with the appropriate number of zeros even if the format has changed")
def test_padding_change_with_proper_number_of_zeros():
    pass

@scenario('convert_demograph_text_to_number.feature', "Row and column header strings should be padded with the appropriate number of zeros even if the format has changed - with separators")
def test_padding_change_with_proper_number_of_zeros_with_separators():
    pass

@when('integer_string_length is set to 3')
def set_integer_string_length_to_3(generic_coordinator):
	generic_coordinator.format_string = "{0:0" + str(3) + "d}"

@scenario('output_dimension_value_combinations.feature', 'When a combination of values would not be shown for a cut because no values exist, add that combination in as to not screw up excel')
def test_add_combination_of_values():
	pass

@when('ensure_combination_for_every_set_of_demographics is True')
def ensure_combination_for_every_set_of_demographics_is_true(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.ensure_combination_for_every_set_of_demographics = True

@then('compute net with cut_demographic = region and gender is run results in row with SoDak and Female')
def check_row_with_SoDak_and_Female(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.result_types =['net']
	res = coordinator_with_net_formatted_values.compute_aggregation(cut_demographic=['region','gender']).set_index(['region','gender'])
	assert res.index.isin([('SoDak','Female')]).sum() > 0

@scenario('output_dimension_value_combinations.feature', "When a combination of values would not be shown for a cut because no values exist, and the dimension type is 'dynamic', don't include that cut")
def test_do_not_include_dynamic ():
	pass

@given('the gender ethnicity is "dynamic" with "dynamic_parent_dimension" of "region"')
def gender_ethnicty_is_dynamic(coordinator_with_net_formatted_values):
	dimension_with_dynamic_type = ConfigurationReader.Dimension(title="gender")
	dimension_with_dynamic_type.dimension_type = "dynamic"
	dimension_with_dynamic_type.dynamic_parent_dimension = "region"
	coordinator_with_net_formatted_values.config = ConfigurationReader.ConfigurationReader()
	coordinator_with_net_formatted_values.config.all_dimensions = mock.MagicMock(return_value = [
																		ConfigurationReader.Dimension(title="region"),
																		ConfigurationReader.Dimension(title="corps"),
																		dimension_with_dynamic_type,
																		])

@then('compute net with cut_demographic = region and gender is run results in no rows with SoDak and Female')
def check_no_row_with_SoDak_and_Female(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.result_types =['net']
	res = coordinator_with_net_formatted_values.compute_aggregation(cut_demographic=['region','gender']).set_index(['region','gender'])
	assert res.index.isin([('SoDak','Female')]).sum() == 0

@scenario('output_dimension_value_combinations.feature', "When a combination of values would not be shown for a cut because no values exist, and the dimension type is 'dynamic' but parent dimension isn't in the cut, there should be a row")
def test_include_some_dimensions_for_dynamic():
	pass

@then('compute net with cut_demographic = region and gender is run results in a row with 2013 and Female')
def check_for_2013_and_female(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.result_types =['net']
	res = coordinator_with_net_formatted_values.compute_aggregation(cut_demographic=['corps','gender']).set_index(['corps','gender'])
	assert res.index.isin([(2013.0,'Female')]).sum() > 0

@when('adjust_zero_padding_of_heading is run with row_heading of "{heading}"')
def step(context,heading):
	context.result = context.coordinator.adjust_zero_padding_of_heading(heading)

@then(re.compile('result of adjust_zero_padding_of_heading with input "(?P<heading>.+)" is "(?P<expected_value>.+)"'),converters=dict(heading=str,expected_value=str))
def step(generic_coordinator,heading,expected_value):
	assert generic_coordinator.adjust_zero_padding_of_heading(heading) == expected_value

@scenario('output_dimension_value_combinations.feature', "When there is a row in the demographics file but no row in the results and the dimension is dynamic, don't include the row")
def test_row_in_demographics_but_not_results():
	pass

def import_table_data(text_table):
    lines = re.split("\n",text_table)
    headings = table_line_to_array(lines.pop(0))
    rows = []
    for line in lines:
        row = dict()
        line_items = table_line_to_array(line)
        assert len(line_items) == len(headings)
        for i, item in enumerate(line_items):
            if item == "":
                item = None
            try:
                item = float(item)
            except(TypeError, ValueError):
                pass
            row[headings[i]] = item
        rows.append(row)
    return rows

def table_line_to_array(line):
    line = re.findall("\|(.*)\|", line)[0]
    items = re.split("\|",line)
    return [item.strip() for item in items]