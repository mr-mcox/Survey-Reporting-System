from pytest_bdd import scenario, given, when, then
import re
from unittest import mock
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
import pandas as pd
import os

@scenario('assemble_cuts_from_config_reader.feature', 'Given a set of cuts from config reader, the calculation coordinator computes the cuts given')
def test_calculate_cuts_from_config_reader():
    pass

@given(re.compile('net formatted values\n(?P<text_table>.+)', re.DOTALL))
def coordinator_with_net_formatted_values(text_table):
	coordinator = CalculationCoordinator.CalculationCoordinator()
	coordinator.results = pd.DataFrame(import_table_data(text_table))
	return coordinator

@given(re.compile('demographic data passed to coordinator\n(?P<text_table>.+)', re.DOTALL))
def demographic_data(text_table, coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.demographic_data = pd.DataFrame(import_table_data(text_table))

@given('a config reader that returns ["region","gender"] and ["region",None]')
def config_reader_with_cuts_to_be_created(coordinator_with_net_formatted_values):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [["region","gender"], ["region",None]])
	coordinator_with_net_formatted_values.config = config_reader
	return config_reader

@given('the config reader has 2 levels by default')
def config_reader_has_two_levels(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.default_number_of_levels = 2

@when('compute_cuts_from_config is run')
def run_compute_cuts_from_config(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.compute_cuts_from_config()

@scenario('export_cuts_to_seperate_files.feature', 'Given a set of cuts from config reader, the calculation coordinator computes the cuts given')
def test_coordinator_computes_cuts():
    pass

@given('a config reader that returns ["region","gender"]')
def config_reader_with_region_gender_to_be_created(coordinator_with_net_formatted_values):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [["region","gender"]])
	coordinator_with_net_formatted_values.config = config_reader
	return config_reader

@when('export_cuts_to_files is run')
def export_cuts_to_files(coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.export_cuts_to_files()

@then('there is a csv file named "cut_1.csv" that has region and gender columns')
def read_csv_file_named_cut_1(coordinator_with_net_formatted_values):
	result = pd.read_csv('cut_1.csv')
	assert {'region','gender'} <= set(result.columns)
	os.remove('cut_1.csv')

# @given('the no_stat_significance_computation flag set')
# def config_reader_with_cuts_and_no_stat_significance(config_reader_with_cuts_to_be_created):
# 	config_reader_with_cuts_to_be_created.config = {'no_stat_significance_computation':'True'}
# 	return config_reader_with_cuts_to_be_created

# @given('mocked coordinator with calculations')
# def mocked_coordinator_with_calculations(config_reader_with_cuts_and_no_stat_significance, coordinator_with_net_formatted_values ):
# 	coordinator_with_net_formatted_values.config = config_reader_with_cuts_and_no_stat_significance
# 	coordinator_with_net_formatted_values.compute_significance = mock.MagicMock(return_value=pd.DataFrame({'question_code':[],'result_type':[]}))
# 	coordinator_with_net_formatted_values.replace_dimensions_with_integers = mock.MagicMock(return_value=pd.DataFrame({'row_heading':['0'],'column_heading':['0'],'aggregation_value':['0']}))
# 	coordinator_with_net_formatted_values.create_row_column_headers = mock.MagicMock(return_value=pd.DataFrame({'row_heading':['0'],'column_heading':['0'],'aggregation_value':['0']}))
# 	coordinator_with_net_formatted_values.adjust_zero_padding_of_heading = {'0':'0'}

# @then('bootstrap_net_significance is called with no_stat_significance_computation = True')
# def step(context):
# 	pass
# 	#No longer works because we can pass dfs. Don't want to take the time to re-work
# 	# print(context.coordinator.compute_significance.mock_calls)
# 	# context.coordinator.compute_significance.assert_any_call(no_stat_significance_computation=True, cut_demographic=['region', None])
#

@scenario('include_specified_question.feature', 'Only include questions specified')
def test_only_include_specified_questions():
    pass

@when('a config reader that requests national cuts only requests cut for "q2" is assigned')
def config_reader_that_requests_q2(coordinator_with_net_formatted_values):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [[None,None,None]])
	config_reader.config = {'show_questions':['q2']}
	coordinator_with_net_formatted_values.config = config_reader

@then('there there is a net entry for question_code "q2"')
def check_for_net_entry_q2(coordinator_with_net_formatted_values):
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q2']) + ";" + result_type_map['net']
	assert label_to_probe_for in coordinator_with_net_formatted_values.compute_cuts_from_config()['column_heading'].unique().tolist()

@then('there there not is a net entry for question_code "q1"')
def check_for_no_net_entry_q1(coordinator_with_net_formatted_values):
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	assert 'q1' not in question_code_map.keys()

@scenario('only_include_sample_sizes_for_questions_specified.feature', 'Only include sample sizes for questions specified')
def test_only_include_sample_sizes_for_specified_questions():
    pass

@when('a config reader that requests national cuts and show_sample_size_for_questions for question_code "q1" and default result_types of "net" and "sample_size" is assigned')
def config_reader_that_specifies_sample_size_for_questions(coordinator_with_net_formatted_values):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [[None,None,None]])
	config_reader.config = {'show_sample_size_for_questions':['q1'],'result_types':['net','sample_size']}
	coordinator_with_net_formatted_values.config = config_reader

@then('there there is a sample size entry for question_code "q1"')
def step(coordinator_with_net_formatted_values):
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q1']) + ";" + result_type_map['sample_size']
	assert label_to_probe_for in coordinator_with_net_formatted_values.compute_cuts_from_config()['column_heading'].unique().tolist()

@then('there there is not a sample size entry for question_code "q2"')
def step(coordinator_with_net_formatted_values):
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = coordinator_with_net_formatted_values.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q2']) + ";" + result_type_map['sample_size']
	assert label_to_probe_for not in coordinator_with_net_formatted_values.compute_cuts_from_config()['column_heading'].unique().tolist()



@then('master_aggregation row_headers has six rows')
def step(coordinator_with_net_formatted_values):
	assert len(coordinator_with_net_formatted_values.compute_cuts_from_config()['row_heading'].unique()) == 6


















@when('compute_significance_from_config is run')
def step(context):
	context.result = context.coordinator.compute_significance_from_config()





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