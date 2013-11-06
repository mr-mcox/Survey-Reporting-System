from behave import *

from NumericOutputCalculator import NumericOutputCalculator

def import_table_data(table):
    table_data = {header : [] for header in table.headings}
    for row in table:
        for header in table.headings:
            table_item = row[header]
            try:
                table_item = float(row[header])
            except ValueError:
                pass
            table_data[header].append(table_item)
    return table_data

@given('net formatted values')
def step(context):
	context.input_data = import_table_data(context.table)

@when('compute net is run')
def step(context):
	context.result = NumericOutputCalculator(net_formatted_values=context.input_data).net_results()

@then('the display_value for question_id 1 is 0.2')
def step(context):
	assert context.result.set_index('question_id').loc[1,'value'] == 0.2