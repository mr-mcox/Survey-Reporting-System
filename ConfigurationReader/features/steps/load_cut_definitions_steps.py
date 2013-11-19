from behave import *
from ConfigurationReader import ConfigurationReader

@given('input yaml that has one one dimension')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':[
	{'cut_fields':['ethnicity']},
	{'cut_fields':['region']}
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
	{'cut_fields':['ethnicity','region','corps']}
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