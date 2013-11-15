from behave import *
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

@given('demographic data')
def step(context):
	context.demographic_data = context.numeric_output_calculator.demographic_data = pd.DataFrame(import_table_data(context.table))

@when('compute net with cut_demographic = region is run')
def step(context):
	context.result = context.numeric_output_calculator.compute_net_results(cut_demographic='region')

@then('the display_value including region for question_id 1 and region "Atlanta" is 0.5')
def step(context):
	assert context.result.set_index(['question_id','region']).loc[(1,'Atlanta'),'value'] == 0.5

@when('compute net with cut_demographic = region and gender is run')
def step(context):
	context.result = context.numeric_output_calculator.compute_net_results(cut_demographic=['region','gender'])

@then('the display_value including region and gender for question_id 1 and region "Atlanta" gender "Female" is 0.5')
def step(context):
	assert context.result.set_index(['question_id','region','gender']).loc[(1,'Atlanta','Female'),'value'] == 0.5
