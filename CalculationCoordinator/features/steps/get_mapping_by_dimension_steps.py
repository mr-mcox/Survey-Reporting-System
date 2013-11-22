from behave import *
from CalculationCoordinator import CalculationCoordinator

@given('a CalculationCoordinator integer label mapping')
def step(context):
	context.cc = CalculationCoordinator()
	context.cc.labels_for_cut_dimensions = {'Region':{'Atlanta':'01','SoDak':'02'},'Gender':{'Male':'03','Female':'04'}}

@when('get_integer_string_mapping with "Gender" is called')
def step(context):
	context.result = context.cc.get_integer_string_mapping('Gender')

@then('a dict with two arrays that correspond to the integers and labels for Gender are returned')
def step(context):
	reconstructed_mapping = dict(zip(context.result['labels'],context.result['integer_strings']))
	assert reconstructed_mapping == {'Male':'03','Female':'04'}