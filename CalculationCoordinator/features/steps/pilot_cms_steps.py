from behave import *
from CalculationCoordinator import CalculationCoordinator
import numpy as np

def import_table_as_rows(table):
	table_data = []
	headers = [header for header in table.headings]
	for row in table:
		row_data = [row[header] for header in headers]
		table_data.append(row_data)
	return table_data

@when('add_pilot_cms is called with')
def step(context):
	context.coordinator.add_pilot_cms(import_table_as_rows(context.table))

@then('respondent_id {id} has a value of "{value}" on "{column}"')
def step(context,id,value,column):
	print (context.coordinator.demographic_data.set_index(['respondent_id']))
	assert context.coordinator.demographic_data.set_index(['respondent_id']).ix[int(id),column] == value

@then('respondent_id {id} has a value of blank on "{column}"')
def step(context,id,column):
	result = context.coordinator.demographic_data.set_index(['respondent_id']).ix[int(id),column]
	# assert np.isnan(result)
	assert result == 'nan'