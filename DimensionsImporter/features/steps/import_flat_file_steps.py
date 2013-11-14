from behave import *
from DimensionsImporter import DimensionsImporter
import os
import pandas as pd

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


@given('file cm_demographic_data.xlsx')
def step(context):
	context.file = os.getcwd() + '/features/steps/test_data/cm_demographics.xlsx'

@when('DimensionsImporter is initialized with xlsx file')
def step(context):
	context.importer = DimensionsImporter(flat_file = context.file)

@then('demographic_data has a table with 6 rows')
def step(context):
	print(context.importer.demographic_data)
	assert len(context.importer.demographic_data.index) == 6

@given('demographic input data')
def step(context):
	context.demograph_input = import_table_data(context.table)

@when('this data is assigned to demographic_data')
def step(context):
	context.importer = DimensionsImporter()
	context.importer.demographic_data = pd.DataFrame(context.demograph_input)

@then('demographic_data has a column titled "respondent_id"')
def step(context):
	assert 'respondent_id' in context.importer.demographic_data.columns