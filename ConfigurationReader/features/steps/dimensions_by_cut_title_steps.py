from behave import *
from ConfigurationReader import ConfigurationReader, Dimension

@given('a configuration reader object with a set of cuts organized into dimensions')
def step(context):
	context.cr = ConfigurationReader()
	context.cr.config = {'cuts':{
							'Ethnicity': {'dimensions':['ethnicity','region','corps']},
							'Region':{'dimensions':['region','corps']}
							},
						'computations':['net']}

@when('columns_for_row_header is called')
def step(context):
	context.result = context.cr.columns_for_row_header()

@then('a list of dicts with result_type, columns_used is returned')
def step(context):
	res = context.result
	assert type(res) == list
	assert len(res) == 12
	example_one = ['ethnicity','region','corps']
	example_two = [None,'region','corps']
	example_three = ['region','corps',None]
	found_one = False
	found_two = False
	found_three = False
	for output in res:
		assert output['result_type'] == 'net'
		if output['columns_used'] == example_one:
			found_one = True
		if output['columns_used'] == example_two:
			found_two = True
		if output['columns_used'] == example_three:
			found_three = True
	assert found_one
	assert found_two
	assert found_three