from pytest_bdd import scenario, given, when, then
import pytest
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from ResponsesRetriever import ResponsesRetriever
import pandas as pd
import re

def table_line_to_array(line):
    line = re.findall("\|(.*)\|", line)[0]
    items = re.split("\|",line)
    return [item.strip() for item in items]

def table_for_db(table):
    lines = re.split("\n",table)
    headings = table_line_to_array(lines.pop(0))
    rows = []
    for line in lines:
        row = table_line_to_array(line)
        row_dict = dict()
        for i, header in enumerate(headings):
            value = row[i]
            try:
                value = int(value)
            except:
                pass
            row_dict[header] = value
        rows.append(row_dict)
    return rows

@given('set up database schema')
def empty_database():
    engine = create_engine('sqlite:///:memory:')
    metadata = MetaData()
    responses = Table('cm_responses',metadata,
                    Column('respondent_id', Integer),
                    Column('survey_id', Integer, ForeignKey('cm_surveys.id')),
                    Column('question_id', Integer, ForeignKey('cm_questions.id')),
                    Column('response', Integer))
    surveys = Table('cm_surveys',metadata,
                    Column('id', Integer, primary_key=True),
                    Column('survey_code', String))
    questions = Table('cm_questions',metadata,
                    Column('id', Integer, primary_key=True),
                    Column('survey_id', Integer),
                    Column('question_code', String(20)),
                    Column('is_confidential', Integer),
                    Column('question_type', String(20)),)
    metadata.create_all(engine)

    conn = engine.connect()
    database = dict()
    database["engine"] = engine
    database["db"] = conn
    database["responses_table"] = responses
    database["surveys_table"] = surveys
    database["questions_table"] = questions
    return database

@given('8 repsonse db')
def eight_response_db(empty_database):
    responses = [{'survey_id':1,'response':1,'question_id':1,'respondent_id':x} for x in range(8)]
    questions = [{'question_id':1}]
    empty_database["db"].execute(empty_database["responses_table"].insert(),responses)
    empty_database["db"].execute(empty_database["questions_table"].insert(),questions)

@given('two survey db')
def two_survey_db(empty_database):
    response_survey_one = [{'survey_id':1,'response':1,'question_id':1,'respondent_id':x} for x in range(8)]
    response_survey_two = [{'survey_id':2,'response':1,'question_id':1,'respondent_id':x} for x in range(2)]
    responses = response_survey_one + response_survey_two
    questions = [{'question_id':1,'question_code':'CSI1','is_confidential':1,'question_type':'7pt_1=SA'}]
    surveys = [{'survey_id':1,'survey_code':'1314F8W'},{'survey_id':2,'survey_code':'1314MYS'}]
    empty_database["db"].execute(empty_database["responses_table"].insert(),responses)
    empty_database["db"].execute(empty_database["questions_table"].insert(),questions)
    empty_database["db"].execute(empty_database["surveys_table"].insert(),surveys)

@pytest.fixture
def responses_object():
    return dict()

@when('retrieve responses for survey_id 1 is run')
def retrieve_response_survey_1(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_id=1)

@then(re.compile('there are (?P<number>\d+) rows returned'), converters=dict(number=int))
def check_rows_returned(number, responses_object):
    assert len(responses_object["responses"]['rows'])==int(number)

@when('retrieve responses for survey_code 1314F8W is run')
def retrieve_responses_for_1314F8W(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_code="1314F8W")

@then(re.compile('one of the columns returned is (?P<column>.+)'))
def one_column_returned(column, responses_object):
    assert column in responses_object["responses"]['column_headings']

@when('retrieve responses for multiple surveys with survey_code 1314F8W and 1314MYS is run')
def retrieve_responses_multiple_surveys(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_code=["1314F8W","1314MYS"])

@scenario('retrieve_numeric_results.feature', "Retrieve all responses from a survey when there is only one survey")
def test_retrieve_all_responses_from_one_survey():
    pass

@scenario('retrieve_numeric_results.feature', "Retrieve all responses from a survey when there is more than one survey")
def test_retrieve_all_responses_from_one_survey_when_more_than_one_in_db():
    pass

@scenario('retrieve_numeric_results.feature', "Retrieve all responses from a survey by name")
def test_retrieve_by_code():
    pass

@scenario('retrieve_numeric_results.feature', "Retrieve question code with responses rather than question_id")
def test_retrieve_question_code():
    pass

@scenario('retrieve_numeric_results.feature', "Return is_confidential column")
def test_return_is_confidential():
    pass

@scenario('retrieve_numeric_results.feature', "Return question_type column")
def test_return_question_type():
    pass

@scenario('retrieve_numeric_results.feature', "Retrieve responses for multiple surveys")
def test_return_multiple_surveys():
    pass

@scenario('retrieve_numeric_results.feature', "Include survey_code in result output if there is more than one survey listed")
def test_return_survey_code_if_more_than_one_survey_listed():
    pass