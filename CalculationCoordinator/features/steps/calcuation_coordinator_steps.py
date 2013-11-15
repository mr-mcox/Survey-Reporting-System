from behave import *
import pandas as pd
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