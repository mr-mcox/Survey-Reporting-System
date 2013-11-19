from behave import *
import pandas as pd
import numpy as np
import re
import os
from openpyxl import load_workbook
from openpyxl import Workbook
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

@then('the display_value including region for question_code 1 and region "Atlanta" is 0.5')
def step(context):
	results = context.coordinator.get_aggregation(cuts='region',result_type='net')
	assert results.set_index(['question_code','region']).loc[(1,'Atlanta'),'aggregation_value'] == 0.5

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
		('gender','net') : pd.DataFrame({'question_code':[0,1,1],'gender':['Male','Female',"Male"]}),
		('region','net') : pd.DataFrame({'question_code':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
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
		('gender','net') : pd.DataFrame({'question_code':[0,1,1],'gender':['Male','Female',"Male"]}),
		('region','net') : pd.DataFrame({'question_code':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
		('region','strong') : pd.DataFrame({'question_code':[0,1,1],'region':['Atlanta','Atlanta',"SoDak"]}),
	}

@then('there is a mapping of the values back to numbers')
def step(context):
	mapping = context.coordinator.dimension_integer_mapping
	assert {'Male','Atlanta'} <= set(mapping['values'])

@given('a set of calculations generated with region and gender and with integer labels')
def step(context):
	context.coordinator = CalculationCoordinator()
	context.coordinator.computations_generated = {
		('gender','net') : pd.DataFrame(
			{
				'question_code':['0','1','1'],
				'gender':['2','3','2'],
				'result_type':['6','6','6'],
				'aggregation_value':[0.2,0.3,0.4]
			}),
		('region','net') : pd.DataFrame(
			{'question_code':['0','1','1'],
			'region':['4','4',"5"],
			'result_type':['6','6','6'],
			'aggregation_value':[0.2,0.3,0.4]
			}),
		('region','strong') : pd.DataFrame({
			'question_code':['0','1','1'],
			'region':['4','4',"5"],
			'result_type':['7','7','7'],
			'aggregation_value':[0.2,0.3,0.4]
			}),
	}
@when('create row and column headers is run')
def step(context):
	context.coordinator.create_row_column_headers()

@then('each calcualation table has row and column header columns')
def step(context):
	for key, df in context.coordinator.computations_generated.items():
		assert {'row_heading','column_heading'} <= set(df.columns)

@then('the column header consists of question and result type joined by a ";"')
def step(context):
	for key, df in context.coordinator.computations_generated.items():
		for i in range(len(df.index)):
			assert df.loc[i,'column_heading'] == df.loc[i,'question_code'] + ";" + df.loc[i,"result_type"]

@then('the row header consists of either gender or region')
def step(context):
	for key, df in context.coordinator.computations_generated.items():
		for i in range(len(df.index)):
			if 'gender' in df.columns:
				assert df.loc[i,'row_heading'] == df.loc[i,'gender']
			else:
				assert df.loc[i,'row_heading'] == df.loc[i,'region']

@given('a set of calculations with column and header rows (and maybe some other stuff)')
def step(context):
	context.coordinator = CalculationCoordinator()
	context.coordinator.computations_generated = {
		('gender','net') : pd.DataFrame(
			{	
				'column_heading':['6.0','6.1','6.1'],
				'row_heading':['2','3','2'],
				'question_code':['0','1','1'],
				'gender':['2','3','2'],
				'result_type':['6','6','6'],
				'aggregation_value':[0.2,0.3,0.4]
			}),
		('region','net') : pd.DataFrame(
			{
				'column_heading':['6.0','6.1','6.1'],
				'row_heading':['4','4','5'],
				'question_code':['0','1','1'],
				'region':['4','4',"5"],
				'result_type':['6','6','6'],
				'aggregation_value':[0.2,0.3,0.4]
			}),
		('region','strong') : pd.DataFrame(
			{
				'column_heading':['7.0','7.1','7.1'],
				'row_heading':['4','4','5'],
				'question_code':['0','1','1'],
				'region':['4','4',"5"],
				'result_type':['7','7','7'],
				'aggregation_value':[0.2,0.3,0.4]
			}),
	}

@when('master aggregations is accessed')
def step(context):
	context.result  = context.coordinator.master_aggregation

@then('the total number of rows is equal to the number of rows in each of the individual tables')
def step(context):
	total_rows = sum([len(df.index) for (key, df) in context.coordinator.computations_generated.items() ])
	assert len(context.result.index) == total_rows

@then('the mapping is in order by integer strings')
def step(context):
	integers = context.coordinator.dimension_integer_mapping['integers']
	assert integers == sorted(integers)

@then('the values column corresponds with the appropriate integer strings')
def step(context):
	values_by_column = context.coordinator.labels_for_cut_dimensions
	dim = context.coordinator.dimension_integer_mapping
	integers = dim['integers']
	for column, value_dict in values_by_column.items():
		for label, integer in value_dict.items():
			for i, string in enumerate(integers):
				if string == integer:
					assert dim['values'][i] == label