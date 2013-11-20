from behave import *
from CalculationCoordinator import CalculationCoordinator

@given('a CalculationCoordinator object')
def step(context):
	context.calc = CalculationCoordinator()

@when('rc_to_range is called with input of row = 2 and col = 3')
def step(context):
	context.result = context.calc.rc_to_range(row = 2, col = 3)

@then("the return is '{result}'")
def step(context, result):
	assert context.result == result

@when('rc_to_range is called with input of row = 2, col = 3, height = 3, width = 2')
def step(context):
	context.result = context.calc.rc_to_range(row = 2, col = 3, height = 3, width = 2)