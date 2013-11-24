from behave import *
from ConfigurationReader import ConfigurationReader, Cut, Dimension


@given('input yaml that has one one dimension')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['ethnicity']},
	'Region':{'dimensions':['region']}
	}
	}
	context.reader.default_number_of_levels = 1

@when('cuts_to_be_created is called')
def step(context):
	context.cuts = context.reader.cuts_to_be_created()

@then('it returns the cuts in the yaml and an empty cut')
def step(context):
	cuts_in_the_yaml = [[None],['ethnicity'],['region']]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match

@given('input yaml that has three dimensions')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['ethnicity','region','corps']},
	}
	}

@then('it returns every combination of each of the dimensions being used or not used')
def step(context):
	cuts_in_the_yaml = [
						['ethnicity','region','corps'],
						[None,'region','corps'],
						['ethnicity',None,'corps'],
						['ethnicity','region',None],
						[None,None,'corps'],
						[None,'region',None],
						['ethnicity',None,None],
						[None,None,None],
						]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match

@given('basic set of cut and dimensions in config file')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['ethnicity']},
	'Region':{'dimensions':['region']}
	}
	}

@when('cuts from the config are accessed')
def step(context):
	context.cuts = context.reader.cuts

@then('the number of cut objects equal to the number of cuts in the config are returned')
def step(context):
	assert len(list(context.cuts.keys())) == 2
	for cut_title, cut in context.cuts.items():
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

@given('a dimension list with a dimension named "Ethnicity"')
def step(context):
	context.reader = ConfigurationReader()
	context.reader._all_dimensions = {'Ethnicity':Dimension(title='Ethnicity')}

@when('a new dimension is created that has the title "{title}"')
def step(context,title):
	context.result = context.reader.create_dimension(title)

@then('the new dimension is the same as the original')
def step(context):
	assert context.result == context.reader._all_dimensions['Ethnicity']

@then('the cuts have titles that they were given in the config')
def step(context):
	created_titles = set([str(cut.title) for key, cut in context.cuts.items()])
	orig_titles = set(list(context.reader.config['cuts'].keys()))
	assert created_titles == orig_titles

@then('that dimension has a title of "Ethnicity"')
def step(context):
	context.result.title == "Ethnicity"

@then('all_dimensions has dimensions titled "Ethnicity" and "Grade"')
def step(context):
	dimension_titles = [dimension.title for dimension in context.reader.all_dimensions()]
	assert set(dimension_titles) == {'Ethnicity','Grade'}

@then('the dimension has a not included label of "Ethnicity Not Used"')
def step(context):
	assert context.result.not_included_label == "Ethnicity Not Used"

@given('that that config has 3 levels by default')
def step(context):
	context.reader.default_number_of_levels = 3

@then('it returns the cuts in the yaml and an empty cut with two blanks at the end of the list')
def step(context):
	cuts_in_the_yaml = [[None,None,None],['ethnicity',None,None],['region',None,None]]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match