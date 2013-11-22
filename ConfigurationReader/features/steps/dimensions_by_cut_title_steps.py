from behave import *
from ConfigurationReader import ConfigurationReader, Dimension

@given('a configuration reader object with a set of cuts organized into dimensions')
def step(context):
	context.cr = ConfigurationReader()
	context.cr.config = {'cuts':{
							'Ethnicity': {'dimensions':['ethnicity','region','corps']},
							'Region':{'dimensions':['region','corps']}
							}}

@when('dimensions_by_cuts is called')
def step(context):
	context.result = context.cr.dimensions_by_cuts()

@then('a dict of all cuts with Dimension objects is returned')
def step(context):
	res = context.result
	assert type(res) == dict
	assert 'Ethnicity' in res
	assert 'Region' in res
	assert type(res['Ethnicity']) == list
	assert type(res['Ethnicity'][0]) == Dimension
	assert [dimension.title for dimension in res['Ethnicity']] == ['ethnicity','region','corps']