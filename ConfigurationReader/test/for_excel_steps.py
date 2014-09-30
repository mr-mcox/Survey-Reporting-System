from pytest_bdd import scenario, given, when, then
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader

@scenario('for_excel_export.feature', 'Basic output for static cuts')
def test_cut_menu_options_provides_list_of_menus():
    pass

@scenario('for_excel_export.feature', 'Output cuts for a given menu')
def test_output_cuts_for_given_menu():
    pass

def reader_with_basic_static_cuts():
@given('basic static cuts')
	reader = ConfigurationReader.ConfigurationReader()
	reader.config = {'cuts':{
							'Grade': {'dimensions':['Grade','Region','Corps']},
							'Region':{'dimensions':['Region','Corps','Something']}
							},
							'dimensions':
							{'Grade':{'all_together_label':"Lack of Ethnicity"},
							'Region':{'all_together_label':"Lack of Ethnicity"},
							'Corps':{'all_together_label':"Lack of Ethnicity"}}}
	reader.cuts
	return reader

@when('cuts_for_excel_menu is run')
def run_cuts_for_excel_menu(reader_with_basic_static_cuts):
	pass

@then('each cut is represented as an item in a list, starting with title, "static" and all dimension titles')
def static_cut_list(reader_with_basic_static_cuts):

	result = reader_with_basic_static_cuts.cuts_for_excel_menu()
	expected_responses = [['Grade', 'static', 'Grade', 'Region', 'Corps'], ['Region', 'static', 'Region', 'Corps','Something']]
	assert len(result) == 2
	for res in expected_responses:
		match = False
		for res2 in result:
			if res == res2:
				match = True
		assert match == True

@given('basic static cuts with one historical cut')
def reader_with_historical_cut():
	reader = ConfigurationReader.ConfigurationReader()
	reader.config = {'cuts':{
							'Grade': {'dimensions':['Grade','Region','Corps']},
							'Region':{'dimensions':['Region','Corps','Something'],'cut_menus':['historical']}
							},
							'dimensions':
							{'Grade':{'all_together_label':"Lack of Ethnicity"},
							'Region':{'all_together_label':"Lack of Ethnicity"},
							'Corps':{'all_together_label':"Lack of Ethnicity"}}}
	reader.cuts
	return reader

@when('cuts_for_excel_menu is run with menu historical')
def run_cuts_for_excel_menu_with_historical(reader_with_historical_cut):
	pass
@then('only historical cut is output')
def historical_cut_output(reader_with_historical_cut):
	result = reader_with_historical_cut.cuts_for_excel_menu(menu='historical')

	expected_responses = [['Region', 'static', 'Region', 'Corps',"Something"]]
	assert len(result) == 1
	for res in expected_responses:
		match = False
		for res2 in result:
			if res == res2:
				match = True
		assert match == True