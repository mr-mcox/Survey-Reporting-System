from behave import *
from DimensionsImporter import DimensionsImporter
import os

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

