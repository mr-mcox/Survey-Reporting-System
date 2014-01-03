from behave import *
from NumericOutputCalculator import NumericOutputCalculator
from unittest.mock import MagicMock

@given('a generic NumericOutputCalculator')
def step(context):
	responses = {'respondent_id':[0,1],'net_formatted_value':[-1,0]}
	context.calc = NumericOutputCalculator(responses=responses)
	context.calc.compute_aggregation = MagicMock()

@when('bootstrap_net_significance is called for cut ["ethnicity","region","corps"]')
def step(context):
	context.calc.bootstrap_net_significance(cuts=['ethnicity','region','corps'])

@then('compute_aggregation is called for cuts ["ethnicity","region","corps"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["ethnicity","region","corps"], result_type=["sample_size","strong_count","weak_count"])

@then('compute_aggregation is called for cuts ["region","corps"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["region","corps"], result_type=["sample_size","strong_count","weak_count"])

@when('bootstrap_net_significance is called for cut ["region"]')
def step(context):
	context.calc.bootstrap_net_significance(cuts=['region'])

@then('compute_aggregation is called for cuts ["region"] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=["region"], result_type=["sample_size","strong_count","weak_count"])

@then('compute_aggregation is called for cuts [] and result_type ["sample_size","strong_count","weak_count"]')
def step(context):
	context.calc.compute_aggregation.assert_any_call(cut_demographic=[], result_type=["sample_size","strong_count","weak_count"])