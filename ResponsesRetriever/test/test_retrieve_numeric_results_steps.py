from pytest_bdd import scenario, given, when, then
import pytest
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from SurveyReportingSystem.ResponsesRetriever import ResponsesRetriever
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
    question = Table('cm_question',metadata,
        Column('question_id', Integer, primary_key=True, autoincrement=False),
        Column('question_title', String(2000)),
        Column('question_code', String(20)),
        )
    question_category = Table('cm_question_category',metadata,
        Column('question_category_id', Integer, primary_key=True, autoincrement=False),
        Column('question_category', String(20)),
        )
    response = Table('cm_response',metadata,
        Column('person_id', Integer, primary_key=True, autoincrement=False),
        Column('survey_question_id', Integer, primary_key=True, autoincrement=False),
        Column('response', Integer),
        Column('converted_net_value', Integer),
        )
    survey = Table('cm_survey',metadata,
        Column('survey_id', Integer, primary_key=True, autoincrement=False),
        Column('survey_code', String(20)),
        Column('survey_title', String(2000)),
        )
    survey_question = Table('cm_survey_question',metadata,
        Column('survey_question_id', Integer, primary_key=True, autoincrement=False),
        Column('survey_id', Integer),
        Column('is_confidential', Integer),
        Column('question_type', String(20)),
        Column('question_title_override', String(2000)),
        Column('question_id', Integer),
        Column('question_category_id', Integer),
        )
    metadata.create_all(engine)

    conn = engine.connect()
    database = dict()
    database["engine"] = engine
    database["db"] = conn
    database["response_table"] = response
    database["survey_table"] = survey
    database["question_table"] = question
    database["survey_question_table"] = survey_question
    database["question_category_table"] = question_category
    return database

@given('8 repsonse db')
def eight_response_db(empty_database):
    responses = [{'response':1,'survey_question_id':1,'person_id':x+1} for x in range(8)]
    survey_questions = [{'question_id':1,'survey_question_id':1}]
    questions = [{'question_id':1}]
    empty_database["db"].execute(empty_database["response_table"].insert(),responses)
    empty_database["db"].execute(empty_database["question_table"].insert(),questions)
    empty_database["db"].execute(empty_database["survey_question_table"].insert(),survey_questions)

@given('two survey db')
def two_survey_db(empty_database):
    response_survey_one = [{'response':1,'survey_question_id':1,'person_id':x+1} for x in range(8)]
    response_survey_two = [{'response':1,'survey_question_id':2,'person_id':x+1} for x in range(2)]
    responses = response_survey_one + response_survey_two
    survey_questions = [
        {'survey_question_id':1,'question_id':1,'is_confidential':1,'question_type':'7pt_1=SA','survey_id':1},
        {'survey_question_id':2,'question_id':1,'is_confidential':1,'question_type':'7pt_1=SA','survey_id':2},
                ]
    questions = [{'question_id':1,'question_code':'CSI'}]
    surveys = [{'survey_id':1,'survey_code':'1314F8W'},{'survey_id':2,'survey_code':'1314MYS'}]
    empty_database["db"].execute(empty_database["response_table"].insert(),responses)
    empty_database["db"].execute(empty_database["question_table"].insert(),questions)
    empty_database["db"].execute(empty_database["survey_table"].insert(),surveys)
    empty_database["db"].execute(empty_database["survey_question_table"].insert(),survey_questions)

@pytest.fixture
def responses_object():
    return dict()

@when('retrieve responses for survey_id 1 is run')
def retrieve_response_survey_1(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever.ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_id=1)

@then(re.compile('there are (?P<number>\d+) rows returned'), converters=dict(number=int))
def check_rows_returned(number, responses_object):
    assert len(responses_object["responses"]['rows'])==int(number)

@when('retrieve responses for survey_code 1314F8W is run')
def retrieve_responses_for_1314F8W(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever.ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_code="1314F8W")

@then(re.compile('one of the columns returned is (?P<column>.+)'))
def one_column_returned(column, responses_object):
    assert column in responses_object["responses"]['column_headings']

@when('retrieve responses for multiple surveys with survey_code 1314F8W and 1314MYS is run')
def retrieve_responses_multiple_surveys(responses_object, empty_database):
    responses_object["responses"] = ResponsesRetriever.ResponsesRetriever(db_connection=empty_database["db"]).retrieve_responses_for_survey(survey_code=["1314F8W","1314MYS"])

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