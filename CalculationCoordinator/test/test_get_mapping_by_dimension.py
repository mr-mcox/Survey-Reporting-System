from pytest_bdd import scenario, given, then
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator

@scenario('get_mapping_by_dimension.feature', 'A basic mapping is returned when a dimension is provided')
def test_calculate_cuts_from_config_reader():
    pass

@given('a CalculationCoordinator integer label mapping')
def calculation_coordinator_with_integer_label_mapping():
	cc = CalculationCoordinator.CalculationCoordinator()
	cc.labels_for_cut_dimensions = {'Region':{'Atlanta':'01','SoDak':'02'},'Gender':{'Male':'03','Female':'04'}}
	return cc

@then('get_integer_string_mapping with "Gender" is called returns a dict with two arrays that correspond to the integers and labels for Gender')
def step(calculation_coordinator_with_integer_label_mapping):
	result = calculation_coordinator_with_integer_label_mapping.get_integer_string_mapping('Gender')
	reconstructed_mapping = dict(zip(result['labels'],result['integer_strings']))
	assert reconstructed_mapping == {'Male':'03','Female':'04'}