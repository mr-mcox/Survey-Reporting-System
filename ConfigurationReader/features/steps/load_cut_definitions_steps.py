from behave import *
from ConfigurationReader import ConfigurationReader, Cut, Dimension


@given('input yaml that has one one dimension')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'dimensions':['ethnicity']},
	{'dimensions':['region']}
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

@given('input yaml that has three dimensions')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'dimensions':['ethnicity','region','corps']}
	]}

@then('it returns every combination of each of the dimensions being used or not used')
def step(context):
	cuts_in_the_yaml = [{},{'ethnicity'},{'region'},{'corps'},{'ethnicity','region'},{'ethnicity','corps'},{'region','corps'},{'ethnicity','corps','region'}]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match

@given('basic set of cut and dimensions in config file')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'title': 'Region',
	'dimensions':['region','corps']},
	{'title': 'ROSVP',
	'dimensions':['rosvp','region','corps']},
	]}

@when('cuts from the config are accessed')
def step(context):
	context.cuts = context.reader.cuts

@then('the number of cut objects equal to the number of cuts in the config are returned')
def step(context):
	assert len(context.cuts) == 2
	for cut in context.cuts:
		assert type(cut) == Cut

@given('a cut object with config information')
def step(context):
	context.cut_config_data = {'title': 'Region',
								'dimensions':['region','corps']}

@when('the cut object is created')
def step(context):
	context.cut = Cut(config_data=context.cut_config_data)

@then('it has dimension objects that correspond to the dimensions in the config object')
def step(context):
	assert len(context.cut.dimensions) == 2
	for dimension in context.cut.dimensions:
		assert type(dimension) == Dimension