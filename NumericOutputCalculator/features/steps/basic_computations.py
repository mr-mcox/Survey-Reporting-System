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
	context.numeric_output_calculator = NumericOutputCalculator(responses=import_table_data(context.table))

@when('compute net is run')
def step(context):
	context.result = context.numeric_output_calculator.compute_net_results()

@then('the display_value for question_code {question_code} is {value}')
def step(context,question_code,value):
    if 'net_formatted_value' in context.result.columns:
        assert context.result.set_index('question_code').loc[int(question_code),'aggregation_value'] == float(value)
    else:
        assert context.result.set_index('question_code').loc[int(question_code),'aggregation_value'] == float(value)

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
    nfv = context.numeric_output_calculator.responses
    value_column = 'net_formatted_value'
    if 'net_formatted_value' not in nfv.columns:
        value_column = 'response'
    if value == 'blank':
        assert np.isnan(nfv.set_index('person_id').loc[int(person_id),value_column])
    else:
        assert nfv.set_index('person_id').loc[int(person_id),value_column] == int(value)
    

@given('raw 7pt questions results')
def step(context):
    context.numeric_output_calculator = NumericOutputCalculator(responses=import_table_data(context.table))

@when('compute average is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_average_results()

@then('there is a result_type column where all rows have value of net')
def step(context):
    assert 'result_type' in context.result.columns
    assert len(context.result['result_type'].unique()) == 1
    assert context.result.result_type.iloc[0] == 'net'

@when('compute sample size is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_sample_size_results()

@when('when compute_aggregation is run with net and strong')
def step(context):
    context.result = context.numeric_output_calculator.compute_aggregation(result_type=['net','strong'])

@then('there is a result_type column that include both net and strong')
def step(context):
    assert set(context.result['result_type'].unique()) == {'net','strong'}