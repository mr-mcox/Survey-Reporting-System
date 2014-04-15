from pytest_bdd import scenario, given, when, then
import re
from DimensionsImporter import DimensionsImporter
import os
import pandas as pd

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

@scenario('import_flat_file.feature', 'When an xlsx file is specified, a table of data is imported')
def test_import_table_from_xlsx():
    pass

@given('file cm_demographic_data.xlsx')
def demographic_file():
	return os.path.dirname(os.path.realpath(__file__)) + '/test_data/cm_demographics.xlsx'

@given('DimensionsImporter is initialized with xlsx file')
def importer_with_data(demographic_file):
	return DimensionsImporter(flat_file = demographic_file)

@then('demographic_data has a table with 6 rows')
def has_table(importer_with_data):
	assert len(importer_with_data.demographic_data.index) == 6


@scenario('import_flat_file.feature', 'When demographic_data is assigned a table with a column names that should be interpreted as respondent_id, the column name is changed')
def test_change_column_names():
    pass

@given(re.compile('demographic input data\n(?P<text_table>.+)', re.DOTALL))
def demograhpic_input(text_table):
	return import_table_data(text_table)

@given('an importer')
def importer():
    return DimensionsImporter()

@when('this data is assigned to demographic_data')
def assign_data_to_importer(importer, demograhpic_input):
	importer.demographic_data = pd.DataFrame(demograhpic_input)

@then('demographic_data has a column titled "respondent_id"')
def check_respondent_id_column(importer):
	assert 'respondent_id' in importer.demographic_data.columns