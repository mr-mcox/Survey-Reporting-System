from behave import *

from NumericOutputCalculator import NumericOutputCalculator

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
	context.input_data = import_table_data(context.table)

@when('compute net is run')
def step(context):
	context.result = NumericOutputCalculator(net_formatted_values=context.input_data).compute_net_results()

@then('the display_value for question_id 1 is {value}')
def step(context,value):
    print(context.result)
    assert context.result.set_index('question_id').loc[1,'value'] == float(value)

@when('compute strong is run')
def step(context):
    context.result = NumericOutputCalculator(net_formatted_values=context.input_data).compute_strong_results()