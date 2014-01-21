from behave import *
from NumericOutputCalculator import NumericOutputCalculator
from unittest.mock import MagicMock
import pandas as pd
import numpy as np

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

@given('a generic NumericOutputCalculator')
def step(context):
	responses = {'respondent_id':[0,1],'net_formatted_value':[-1,0]}
	context.calc = NumericOutputCalculator(responses=responses)
	context.calc.compute_aggregation = MagicMock()

@when('aggregations_for_net_significance is called for cut ["ethnicity","region","corps"]')
def step(context):
	context.calc.aggregations_for_net_significance(cuts=['ethnicity','region','corps'])

@then('compute_aggregation is called for cuts ["ethnicity","region","corps"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["ethnicity","region","corps"], result_type=["sample_size","strong_count","weak_count"])

@then('compute_aggregation is called for cuts ["region","corps"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["region","corps"], result_type=["sample_size","strong_count","weak_count"])

@when('aggregations_for_net_significance is called for cut ["region"]')
def step(context):
	context.calc.aggregations_for_net_significance(cuts=['region'])

@then('compute_aggregation is called for cuts ["region"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["region"], result_type=["sample_size","strong_count","weak_count"])

@then('compute_aggregation is called for cuts [] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=[], result_type=["sample_size","strong_count","weak_count"])

@when('bootstrap_net_significance is called for cut ["gender","region"]')
def step(context):
	context.numeric_output_calculator.bootstrap_net_significance(cuts=['gender','region'])

@then('count for region "SoDak" gender "Male" and column "{column}" is {count}')
def step(context,column,count):
	result = context.numeric_output_calculator.counts_for_significance.loc[('Male','SoDak',1),column]
	assert result == int(count), "Count should be " + count + " but is " + str(result)

@when('bootstrap_net_significance is called for cut ["region"]')
def step(context):
	context.numeric_output_calculator.bootstrap_net_significance(cuts=['region'])

@then('count for region "SoDak" and column "{column}" is {count}')
def step(context,column,count):
	result = context.numeric_output_calculator.counts_for_significance.loc[('SoDak',1),column]
	assert result == int(count), "Count should be " + count + " but is " + str(result)

@given('statistical significance frequency table for cut region and gender')
def step(context):
	responses = {'respondent_id':[0,1],'net_formatted_value':[-1,0]}
	context.calc = NumericOutputCalculator(responses=responses)
	context.freq_table = pd.DataFrame(import_table_data(context.table)).set_index(['question_code','region','gender'])

@when('bootstrap_result_from_frequency_table is run')
def step(context):
	context.result = context.calc.bootstrap_result_from_frequency_table(context.freq_table)

@then('aggregation_value for region "{region}" and gender "{gender}" is "{result}"')
def step(context,region,gender,result):
	# print(context.result)
	assert context.result.ix[(1,region, gender),'aggregation_value'] == result

@then('aggregation_value for region "{region}" and gender "{gender}" is blank')
def step(context,region,gender):
	assert context.result.loc[(1,region, gender),'aggregation_value'] == ''

@when('bootstrap_net_significance is called for cut ["gender","region"] with no_stat_significance_computation = True')
def step(context):
	context.result = context.numeric_output_calculator.bootstrap_net_significance(cuts=['gender','region'],no_stat_significance_computation=True)

@then('statistical significance aggregation_value for region "{region}" and gender "{gender}" is blank')
def step(context,region,gender):
	# print(context.result.loc[(1,region, gender),'aggregation_value'])
	assert context.result.iloc[0]['aggregation_value'] == ''