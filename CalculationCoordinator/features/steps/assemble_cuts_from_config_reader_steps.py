from behave import *
from unittest import mock
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from CalculationCoordinator import CalculationCoordinator

@given('a config reader that returns ["region","gender"] and ["region",None]')
def step(context):
	config_reader = ConfigurationReader.ConfigurationReader()
	config_reader.cuts_to_be_created = mock.MagicMock(return_value = [["region","gender"], ["region",None]])
	context.cc = CalculationCoordinator(config = config_reader)
	context.config_reader = config_reader

@given('the config reader has 2 levels by default')
def step(context):
	context.config_reader.default_number_of_levels = 2

@when('master_aggregation is accessed')
def step(context):
	pass

@then('master_aggregation row_headers has six rows')
def step(context):
	pass
	# assert len(context.cc.master_aggregation['row_heading'].unique()) == 6