from behave import *
from ConfigurationReader import ConfigurationReader

@given('basic static cuts')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
							'Grade': {'dimensions':['Grade','Region','Corps']},
							'Region':{'dimensions':['Region','Corps','Something']}
							},
							'dimensions':
							{'Grade':{'all_together_label':"Lack of Ethnicity"},
							'Region':{'all_together_label':"Lack of Ethnicity"},
							'Corps':{'all_together_label':"Lack of Ethnicity"}}}
	context.reader.cuts

@when('cuts_for_excel_menu is run')
def step(context):
	context.result = context.reader.cuts_for_excel_menu()

@then('each cut is represented as an item in a list, starting with title, "static" and all dimension titles')
def step(context):
	expected_results = [['Grade', 'static', 'Grade', 'Region', 'Corps'], ['Region', 'static', 'Region', 'Corps','Something']]
	print(context.result)
	assert len(context.result) == 2
	for res in expected_results:
		match = False
		for res2 in context.result:
			if res == res2:
				match = True
		assert match == True

@given('basic static cuts with one historical cut')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
							'Grade': {'dimensions':['Grade','Region','Corps']},
							'Region':{'dimensions':['Region','Corps','Something'],'cut_menus':['historical']}
							},
							'dimensions':
							{'Grade':{'all_together_label':"Lack of Ethnicity"},
							'Region':{'all_together_label':"Lack of Ethnicity"},
							'Corps':{'all_together_label':"Lack of Ethnicity"}}}
	context.reader.cuts

@when('cuts_for_excel_menu is run with menu historical')
def step(context):
	context.result = context.reader.cuts_for_excel_menu(menu='historical')

@then('only historical cut is output')
def step(context):
	expected_results = [['Region', 'static', 'Region', 'Corps',"Something"]]
	assert len(context.result) == 1
	for res in expected_results:
		match = False
		for res2 in context.result:
			if res == res2:
				match = True
		assert match == True