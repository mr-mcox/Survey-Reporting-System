from behave import *
from ConfigurationReader import ConfigurationReader, Cut, Dimension
from unittest import mock


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
		assert cuts_match, "Cuts don't match and are " + str(context.cuts)

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

@then('the dimension has a not included label of "{value}"')
def step(context,value):
	assert context.result.all_together_label == value

@then('the dimension has a not included label of None')
def step(context):
	print(context.result.all_together_label)
	assert context.result.all_together_label is None

@then('the dimension has dimension_type of "{dimension_type}"')
def step(context,dimension_type):
	assert context.result.dimension_type == dimension_type


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

@given('basic set of cut and dimensions in config file with a not included label for ethnicity of "Lack of Ethnicity"')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['Ethnicity']},
	'Region':{'dimensions':['Region']}
	},
	'dimensions':
	{'Ethnicity':{'all_together_label':"Lack of Ethnicity"}}
	}

@given('a set of cuts and dimensions with the Ethnicity dimensions having a "display_all_together_label" value of "No"')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['Ethnicity']},
	'Region':{'dimensions':['Region']}
	},
	'dimensions':
	{'Ethnicity':{'display_all_together_label': "No"}}
	}

@given('basic set of cut and dimensions in config file with a dynamic_parent_dimension for Ethnicity dimension of "Region"')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['Ethnicity']},
	'Region':{'dimensions':['Region']}
	},
	'dimensions':
	{'Ethnicity':{'dynamic_parent_dimension':"Region"}}
	}

@then('the dimension is_composite flag is False')
def step(context):
	assert context.result.is_composite == False


@given('basic set of cut and dimensions in config file with composite dimension for Ethnicity')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity': {'dimensions':['Ethnicity']},
	'Region':{'dimensions':['Region']}
	},
	'dimensions':
	{'Ethnicity':{'composite_dimensions':["Ethnicity","LIB"]},
	'LIB':{}}
	}

@then('the dimension is_composite flag is True')
def step(context):
	assert context.result.is_composite == True

@given('input yaml that has a composite dimension of "Ethnicity_POC" that includes "ethnicity" and "poc" components')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
	'Ethnicity_POC': {'dimensions':['ethnicity_poc','region','corps']},
	},
	'dimensions':{'ethnicity_poc':{'composite_dimensions':['ethnicity','poc']}}
	}

@then('it returns cuts with ethnicity and poc')
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
						['poc','region','corps'],
						['poc',None,'corps'],
						['poc','region',None],
						['poc',None,None],
						]
	for yaml_cut in cuts_in_the_yaml:
		cuts_match = False
		for cut in context.cuts:
			if cut == yaml_cut:
				cuts_match = True
		assert cuts_match
