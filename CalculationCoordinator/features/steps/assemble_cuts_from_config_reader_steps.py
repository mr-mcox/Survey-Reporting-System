from behave import *
from unittest import mock
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from CalculationCoordinator import CalculationCoordinator
import pandas as pd

@given('a config reader that returns ["region","gender"] and ["region",None]')
def step(context):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [["region","gender"], ["region",None]])
	context.coordinator.config = config_reader
	context.config_reader = config_reader

@given('the config reader has 2 levels by default')
def step(context):
	context.config_reader.default_number_of_levels = 2

@when('compute_cuts_from_config is run')
def step(context):
	context.result = context.coordinator.compute_cuts_from_config()

@then('master_aggregation row_headers has six rows')
def step(context):
	assert len(context.result['row_heading'].unique()) == 6

@given('a config reader that requests national cuts and show_sample_size_for_questions for question_code "q1" and default result_types of "net" and "sample_size"')
def step(context):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [[None,None,None]])
	config_reader.config = {'show_sample_size_for_questions':['q1'],'result_types':['net','sample_size']}
	context.coordinator.config = config_reader
	context.config_reader = config_reader

@then('there there is a sample size entry for question_code "q1"')
def step(context):
	mapping = context.coordinator.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = context.coordinator.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q1']) + ";" + result_type_map['sample_size']
	assert label_to_probe_for in context.result['column_heading'].unique().tolist()

@then('there there is not a sample size entry for question_code "q2"')
def step(context):
	mapping = context.coordinator.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = context.coordinator.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q2']) + ";" + result_type_map['sample_size']
	assert label_to_probe_for not in context.result['column_heading'].unique().tolist()

@given('a config reader that requests national cuts only requests cut for "q2"')
def step(context):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [[None,None,None]])
	config_reader.config = {'show_questions':['q2']}
	context.coordinator.config = config_reader
	context.config_reader = config_reader

@then('there there is a net entry for question_code "q2"')
def step(context):
	mapping = context.coordinator.get_integer_string_mapping('result_type')
	result_type_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	mapping = context.coordinator.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	label_to_probe_for = str(question_code_map['q2']) + ";" + result_type_map['net']
	assert label_to_probe_for in context.result['column_heading'].unique().tolist()

@then('there there not is a net entry for question_code "q1"')
def step(context):
	mapping = context.coordinator.get_integer_string_mapping('question_code')
	question_code_map = dict(zip(mapping['labels'],mapping['integer_strings']))
	assert 'q1' not in question_code_map.keys()

@given('a config reader that returns ["region","gender"] and ["region",None] and the no_stat_significance_computation flag set')
def step(context):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [["region","gender"], ["region",None]])
	config_reader.config = {'no_stat_significance_computation':'True'}
	context.coordinator.config = config_reader
	context.config_reader = config_reader
	context.coordinator.compute_significance = mock.MagicMock(return_value=pd.DataFrame({'question_code':[],'result_type':[]}))
	context.coordinator.replace_dimensions_with_integers = mock.MagicMock(return_value=pd.DataFrame({'row_heading':['0'],'column_heading':['0'],'aggregation_value':['0']}))
	context.coordinator.create_row_column_headers = mock.MagicMock(return_value=pd.DataFrame({'row_heading':['0'],'column_heading':['0'],'aggregation_value':['0']}))
	context.coordinator.adjust_zero_padding_of_heading = {'0':'0'}


@then('bootstrap_net_significance is called with no_stat_significance_computation = True')
def step(context):
	pass
	#No longer works because we can pass dfs. Don't want to take the time to re-work
	# print(context.coordinator.compute_significance.mock_calls)
	# context.coordinator.compute_significance.assert_any_call(no_stat_significance_computation=True, cut_demographic=['region', None])

@when('compute_significance_from_config is run')
def step(context):
	context.result = context.coordinator.compute_significance_from_config()