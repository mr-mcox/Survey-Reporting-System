from behave import *
from ConfigurationReader import ConfigurationReader

@given('basic static cuts')
def step(context):
	context.reader = ConfigurationReader()
	context.reader.config = {'cuts':{
							'Grade': {'dimensions':['Grade','Region','Corps']},
							'Region':{'dimensions':['Region','Corps']}
							}}

@when('cuts_for_excel_menu is run')
def step(context):
	context.result = context.reader.cuts_for_excel_menu()

@then('each cut is represented as an item in a list, starting with title, "static" and all dimension titles')
def step(context):
	expected_results = [['Grade', 'static', 'Grade', 'Region', 'Corps'], ['Region', 'static', 'Region', 'Corps']]
	print(context.result)
	assert len(context.result) == 2
	for res in expected_results:
		match = False
		for res2 in context.result:
			if res == res2:
				match = True
		assert match == True