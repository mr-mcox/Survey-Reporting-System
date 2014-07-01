from pytest_bdd import scenario, given, when, then
import re
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator

@scenario('excel_helper.feature', 'When given a row and column with a start index of 0, convert that to a range string')
def test_convert_row_column_to_range_string():
    pass

@scenario('excel_helper.feature', 'When a range is indicated, return the range as a string')
def test_convert_row_column_to_range_string_with_range():
    pass

@given('a generic coordinator')
def generic_coordinator():
	return CalculationCoordinator.CalculationCoordinator()

@then('the result of rc_to_range with row = 2 and col = 3 is "D3"')
def step(generic_coordinator):
	assert generic_coordinator.rc_to_range(row = 3, col = 4) == "D3"

@then('the result of rc_to_range with row = 2, col = 3, height = 3, width = 2 is "D3:E5"')
def step(generic_coordinator):
	assert generic_coordinator.rc_to_range(row = 3, col = 4, height = 3, width = 2) == "D3:E5"