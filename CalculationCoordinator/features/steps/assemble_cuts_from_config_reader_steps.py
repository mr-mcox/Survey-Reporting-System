from behave import *
from unittest import mock
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from CalculationCoordinator import CalculationCoordinator

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