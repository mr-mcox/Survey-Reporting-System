from behave import *
import numpy as np
from NumericOutputCalculator import NumericOutputCalculator
from SurveyReportingSystem.NumericOutputCalculator.noc_helper import map_responses_to_net_formatted_values
import pdb

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
    context.responses = import_table_data(context.table)
    context.numeric_output_calculator = NumericOutputCalculator(responses=context.responses)

@when('compute net is run')
def step(context):
	context.result = context.numeric_output_calculator.compute_net_responses()

@then('the display_value for question_code {question_code} is {value}')
def step(context,question_code,value):
    if value == 'blank':
        print( context.result )
        assert np.isnan( context.result.set_index('question_code').ix[int(question_code),'aggregation_value'] )
    else:
        if 'net_formatted_value' in context.result.columns:
            assert context.result.set_index('question_code').ix[int(question_code),'aggregation_value'] == float(value)
        else:
            assert context.result.set_index('question_code').ix[int(question_code),'aggregation_value'] == float(value)

@then('the "{column}" display_value for question_code "{question_code}" is {value}')
def step(context,column,question_code,value):
    if value == 'blank':
        print( context.result )
        assert np.isnan( context.result.set_index(['question_code','result_type']).ix[(float(question_code),column)].get('aggregation_value') )
    else:
        if 'net_formatted_value' in context.result.columns:
            assert context.result.set_index(['question_code','result_type']).ix[(float(question_code),column)].get('aggregation_value') == float(value)
        else:
            assert context.result.set_index(['question_code','result_type']).ix[(float(question_code),column)].get('aggregation_value') == float(value)

@then('the regional "{column}" display_value for question_code "{question_code}" and region "{region}" is {value}')
def step(context,column,question_code,region, value):
    if value == 'blank':
        print( context.result )
        assert np.isnan( context.result.set_index(['question_code','result_type','region']).ix[(float(question_code),column,region)].get('aggregation_value') )
    else:
        if 'net_formatted_value' in context.result.columns:
            assert context.result.set_index(['question_code','result_type','region']).ix[(float(question_code),column,region)].get('aggregation_value') == float(value)
        else:
            print(context.result.set_index(['question_code','result_type','region']).ix[(float(question_code),column,region)])
            assert context.result.set_index(['question_code','result_type','region']).ix[(float(question_code),column,region)].get('aggregation_value') == float(value)

@when('compute strong is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_strong_responses()

@when('compute weak is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_weak_responses()

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
    

@given('raw 7pt questions responses')
def step(context):
    context.numeric_output_calculator = NumericOutputCalculator(responses=import_table_data(context.table))

@when('compute average is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_average_responses()

@then('there is a result_type column where all rows have value of net')
def step(context):
    assert 'result_type' in context.result.columns
    assert len(context.result['result_type'].unique()) == 1
    assert context.result.result_type.iloc[0] == 'net'

@when('compute sample size is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_sample_size_responses()

@when('when compute_aggregation is run with net and strong')
def step(context):
    context.result = context.numeric_output_calculator.compute_aggregation(result_type=['net','strong'])

@then('there is a result_type column that include both net and strong')
def step(context):
    assert set(context.result['result_type'].unique()) == {'net','strong'}


@when('compute strong_count is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_aggregation(result_type=['strong_count'])

@when('compute weak_count is run')
def step(context):
    context.result = context.numeric_output_calculator.compute_aggregation(result_type=['weak_count'])

@then('the response value for person_id {person_id} is {value}')
def step(context, person_id, value):
    nfv = context.numeric_output_calculator.responses
    value_column = 'response'
    if value == 'blank':
        assert np.isnan(nfv.set_index('person_id').loc[int(person_id),value_column])
    else:
        assert nfv.set_index('person_id').loc[int(person_id),value_column] == int(value)

@then('the display_value for string based question_code {question_code} is {value}')
def step(context,question_code,value):
    if value == 'blank':
        print( context.result )
        assert np.isnan( context.result.set_index(['question_code','result_type']).ix[(question_code,'net'),'aggregation_value'] )
    else:
        if 'net_formatted_value' in context.result.columns:
            assert context.result.set_index('question_code').loc[question_code,'aggregation_value'] == float(value)
        else:
            assert context.result.set_index('question_code').loc[question_code,'aggregation_value'] == float(value)

@then('the net display_value for string based question_code {question_code} is {value}')
def step(context,question_code,value):
    if value == 'blank':
        print( context.result )
        assert np.isnan( context.result.set_index(['question_code','result_type']).ix[(question_code,'net'),'aggregation_value'] )
    else:
        if 'net_formatted_value' in context.result.columns:
            assert context.result.set_index('question_code').loc[question_code,'aggregation_value'] == float(value)
        else:
            assert context.result.set_index(['question_code','result_type']).sortlevel().loc[(question_code,'net'),'aggregation_value'] == float(value)

@then('the regional display_value for string based question_code {question_code} and region "Atlanta" is {value}')
def step(context,question_code,value):
    print(context.result)
    if value == 'blank':
        assert np.isnan(context.result.set_index(['question_code','result_type','region']).ix[('NQ','net','Atlanta'),'aggregation_value'])
    else:
        assert context.result.set_index(['question_code','result_type','region']).ix[('NQ','net','Atlanta'),'aggregation_value'] == float(value)

@when('compute net is run with composite of NQ is q1 and q2 and region cut')
def step(context):
    context.result = context.numeric_output_calculator.compute_net_responses(cut_demographic = 'region', composite_questions = {'NQ':['q1','q2']})

@when('compute {result_type} is run with composite of NQ is q1 and q2')
def step(context,result_type):
    context.result = context.numeric_output_calculator.compute_aggregation(result_type=[result_type],composite_questions = {'NQ':['q1','q2']})

@then('display_value for question_code 1 and result_type "{result_type}" is {value}')
def step(context,result_type,value):
    # print("\n" + str(context.result.set_index(['question_code','result_type'])))
    if value == 'blank':
        print("The result:")
        print(context.result.set_index(['question_code','result_type']).ix[(1.0,result_type),'aggregation_value'])
        assert np.isnan(context.result.set_index(['question_code','result_type']).ix[(1.0,result_type),'aggregation_value'])
    else:
        assert context.result.set_index(['question_code','result_type']).ix[(1.0,result_type),'aggregation_value'] == float(value)

@then('responses_with_dimensions has region of "{region}" for respondent_id 1 and survey_code "{survey_code}"')
def step(context,region,survey_code):
    print(context.numeric_output_calculator.responses_with_dimensions)
    print(context.numeric_output_calculator.demographic_data)
    print(context.numeric_output_calculator.responses)
    assert context.numeric_output_calculator.responses_with_dimensions.set_index(['respondent_id','survey_code']).ix[(1,survey_code),'region'] == region

@when('NumericOutputCalculator is initialized with responses and demographic_data')
def step(context):
    context.numeric_output_calculator = NumericOutputCalculator(responses=context.responses,demographic_data=context.demographic_data)

@then('the display_value including region and gender for question_code 1, result_type "{result_type}" and region "Atlanta", gender "Female" is {value}')
def step(context,result_type,value):
    print("\n" + str(context.result.set_index(['question_code','result_type'])))
    assert context.result.set_index(['question_code','result_type','region','gender']).ix[(1.0,result_type,'Atlanta','Female'),'aggregation_value'] == float(value)
