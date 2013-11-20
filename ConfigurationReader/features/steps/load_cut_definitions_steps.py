from behave import *
from ConfigurationReader import ConfigurationReader, Cut, Level, Dimension


@given('input yaml that has one one dimension')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'levels':['ethnicity']},
	{'levels':['region']}
	]}

@when('cuts_to_be_created is called')
def step(context):
	context.cuts = context.reader.cuts_to_be_created()

@then('it returns the cuts in the yaml and an empty cut')
def step(context):
	cuts_in_the_yaml = [{},{'ethnicity'},{'region'}]
	print(cuts_in_the_yaml)
	print(context)
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match

@given('input yaml that has three levels')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'levels':['ethnicity','region','corps']}
	]}

@then('it returns every combination of each of the levels being used or not used')
def step(context):
	cuts_in_the_yaml = [{},{'ethnicity'},{'region'},{'corps'},{'ethnicity','region'},{'ethnicity','corps'},{'region','corps'},{'ethnicity','corps','region'}]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match

@given('basic set of cut, levels and dimensions in config file')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'title': 'Region',
	'levels':['region','corps']},
	{'title': 'ROSVP',
	'levels':['rosvp','region','corps']},
	]}

@when('cuts from the config are accessed')
def step(context):
	context.cuts = context.reader.cuts

@then('the number of cut objects equal to the number of cuts in the config are returned')
def step(context):
	assert len(context.cuts) == 2
	for cut in context.cuts:
		assert type(cut) == Cut