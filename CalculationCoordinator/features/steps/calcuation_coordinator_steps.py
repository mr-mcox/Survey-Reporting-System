from behave import *
import pandas as pd
import numpy as np
import re
from CalculationCoordinator import CalculationCoordinator

def import_table_data(table):
	table_data = {header : [] for header in table.headings}
	for row in table:
		for header in table.headings:
			table_item = row[header]
			if table_item == "":
				table_item = None
			try:
				table_item = float(row[header])
			except ValueError:
				pass
			table_data[header].append(table_item)
	return table_data

@given('net formatted values')
def step(context):
	context.coordinator = CalculationCoordinator()
	context.coordinator.results = import_table_data(context.table)

@given('demographic data')
def step(context):
	context.demographic_data = context.coordinator.demographic_data = pd.DataFrame(import_table_data(context.table))

@when('compute net with cut_demographic = region is run')
def step(context):
	context.coordinator.compute_aggregation(cut_demographic='region',result_type='net')

@then('the display_value including region for question_id 1 and region "Atlanta" is 0.5')
def step(context):
	results = context.coordinator.get_aggregation(cuts='region',result_type='net')
	assert results.set_index(['question_id','region']).loc[(1,'Atlanta'),'aggregation_value'] == 0.5

@when('compute net with cut_demographic = region and gender is run')
def step(context):
	context.coordinator.compute_aggregation(cut_demographic=['region','gender'],result_type='net')

@then('computations_generated has a length of 2')
def step(context):
	assert len(context.coordinator.computations_generated.keys()) == 2

@given('computations generated that include a cut by gender and a cut by region')
def step(context):
	context.coordinator = CalculationCoordinator()
	context.coordinator.computations_generated = {
		('gender','net') : pd.DataFrame({'question_id':[0,1,1],'gender':['Male','Female',"Male"]}),
		('region','net') : pd.DataFrame({'question_id':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
	}

@when('replace_dimensions_with_integers is run')
def step(context):
	context.coordinator.replace_dimensions_with_integers()

@then('columns of computations_generated are strings with filled numbers')
def step(context):
	for key, df in context.coordinator.computations_generated.items():
		for column in df.columns:
			if column != 'aggregation_value':
				for value in df[column].unique():
					assert type(value) == str
					assert re.search('^\d+$',value) != None

@then('same number of unique values in dimension columns exists before and after')
def step(context):
	values = list()
	for key, df in context.coordinator.computations_generated.items():
		for column in df.columns:
			if column != 'aggregation_value':
				values = values + df[column].unique().tolist()
	values = set(values)
	assert len(values) == 6

@given('computations generated that include a cut by gender and a cut by region with duplicates')
def step(context):
	context.coordinator = CalculationCoordinator()
	context.coordinator.computations_generated = {
		('gender','net') : pd.DataFrame({'question_id':[0,1,1],'gender':['Male','Female',"Male"]}),
		('region','net') : pd.DataFrame({'question_id':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
		('region','strong') : pd.DataFrame({'question_id':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
	}

@then('there is a mapping of the values back to numbers')
def step(context):
	mapping = context.coordinator.dimension_integer_mapping
	assert {'Male','Atlanta'} <= set(mapping['values'])