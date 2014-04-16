from pytest_bdd import scenario, given, when, then
import re
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
import numpy as np
import pandas as pd

@scenario('add_pilot_cms.feature','Given a set of pilot CMs, add labels to the demograhpic table')
def test_add_pilot_cms():
	pass

@given(re.compile('net formatted values\n(?P<text_table>.+)', re.DOTALL))
def coordinator_with_net_formatted_values(text_table):
	coordinator = CalculationCoordinator.CalculationCoordinator()
	coordinator.results = pd.DataFrame(import_table_data(text_table))
	return coordinator

@given(re.compile('demographic data passed to coordinator\n(?P<text_table>.+)', re.DOTALL))
def demographic_data(text_table, coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.demographic_data = pd.DataFrame(import_table_data(text_table))

@when(re.compile('add_pilot_cms is called with\n(?P<text_table>.+)', re.DOTALL))
def add_pilot_cms(text_table, coordinator_with_net_formatted_values):
	coordinator_with_net_formatted_values.add_pilot_cms(import_table_as_rows(text_table))

@then(re.compile('respondent_id (?P<id>\d+) has a value of "(?P<value>.+)" on "(?P<column>.+)"'),converters=dict(id=int,column=str, value=str))
def check_respondent_id_value(id,value,column, coordinator_with_net_formatted_values):
	assert coordinator_with_net_formatted_values.demographic_data.set_index(['respondent_id']).ix[int(id),column] == value

@then(re.compile('respondent_id (?P<id>\d+) has a value of blank on "(?P<column>.+)"'),converters=dict(id=int,column=str))
def check_respondent_id_value_blank(id,column, coordinator_with_net_formatted_values):
	result = coordinator_with_net_formatted_values.demographic_data.set_index(['respondent_id']).ix[int(id),column]
	assert result == 'nan'

def import_table_as_rows(text_table):
    lines = re.split("\n",text_table)
    headings = table_line_to_array(lines.pop(0))
    rows = []
    for line in lines:
        row = list()
        line_items = table_line_to_array(line)
        assert len(line_items) == len(headings)
        for i, item in enumerate(line_items):
            row.append(item)
        rows.append(row)
    return rows

def import_table_data(text_table):
    lines = re.split("\n",text_table)
    headings = table_line_to_array(lines.pop(0))
    rows = []
    for line in lines:
        row = dict()
        line_items = table_line_to_array(line)
        assert len(line_items) == len(headings)
        for i, item in enumerate(line_items):
            if item == "":
                item = None
            try:
                item = float(item)
            except(TypeError, ValueError):
                pass
            row[headings[i]] = item
        rows.append(row)
    return rows

def table_line_to_array(line):
    line = re.findall("\|(.*)\|", line)[0]
    items = re.split("\|",line)
    return [item.strip() for item in items]