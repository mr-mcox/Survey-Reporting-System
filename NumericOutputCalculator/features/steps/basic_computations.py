from behave import *
import numpy as np
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
	context.numeric_output_calculator = NumericOutputCalculator(net_formatted_values=import_table_data(context.table))

@when('compute net is run')
def step(context):
	context.result = context.numeric_output_calculator.compute_net_results()

@then('the display_value for question_id {question_id} is {value}')
def step(context,question_id,value):
    if 'value' in context.result.columns:
        assert context.result.set_index('question_id').loc[int(question_id),'value'] == float(value)
    else:
        assert context.result.set_index('question_id').loc[int(question_id),'response'] == float(value)

@when('compute strong is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_strong_results()

@when('compute weak is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_weak_results()

@when('NumericOutputCalculator is initialized')
def step(context):
    pass

@then('net formatted value for person_id {person_id} is {value}')
def step(context, person_id, value):
    nfv = context.numeric_output_calculator.net_formatted_values
    value_column = 'value'
    if 'value' not in nfv.columns:
        value_column = 'response'
    if value == 'blank':
        assert np.isnan(nfv.set_index('person_id').loc[int(person_id),value_column])
    else:
        assert nfv.set_index('person_id').loc[int(person_id),value_column] == int(value)
    

@given('raw 7pt questions results')
def step(context):
    context.numeric_output_calculator = NumericOutputCalculator(raw_values=import_table_data(context.table))

@when('compute average is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_average_results()