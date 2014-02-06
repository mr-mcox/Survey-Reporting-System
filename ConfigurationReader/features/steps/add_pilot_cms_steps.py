from behave import *
from ConfigurationReader import ConfigurationReader

def import_table_as_rows(table):
	table_data = []
	headers = [header for header in table.headings]
	for row in table:
		row_data = [row[header] for header in headers]
		table_data.append(row_data)
	return table_data

@when('add_pilot_cuts is called with')
def step(context):
	context.reader.add_pilot_cuts(import_table_as_rows(context.table))

@then('cuts has a cut titled "pilot_1" which has dimensions "pilot_1", "region", and "corps"')
def step(context):
	cuts = context.reader.cuts
	assert 'pilot_1' in cuts
	cut_dimensions = [dimension.title for dimension in cuts['pilot_1'].dimensions]
	assert cut_dimensions == ['pilot_1','region', 'corps']

@then('there is a dimension called "pilot_1" that has composite dimensions "pilot_1-Target Group" and "pilot_1-All CMs"')
def step(context):
	dimension = context.reader.get_dimension_by_title('pilot_1')
	assert dimension.composite_dimensions == ['pilot_1-Target Group','pilot_1-All CMs']

@then('there is a dimension called "pilot_1" that has value order "Target Group" and "All CMs"')
def step(context):
	dimension = context.reader.get_dimension_by_title('pilot_1')
	assert dimension.value_order == ['Target Group','All CMs']