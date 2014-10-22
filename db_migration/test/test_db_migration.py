from SurveyReportingSystem.db_migration.migrate import Migrator
from sqlalchemy import Table, Column, Integer, String, MetaData, select, create_engine
from unittest.mock import MagicMock, patch
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def empty_db():
    engine = create_engine('sqlite:///:memory:')
    metadata = MetaData()

    numerical_responses = Table('numerical_responses',metadata,
                            Column('cm_pid', Integer),
                            Column('survey', String),
                            Column('survey_specific_qid', String),
                            Column('response', Integer))

    survey_specific_questions = Table('survey_specific_questions',metadata,
                            Column('survey_specific_qid',String),
                            Column('master_qid',String),
                            Column('survey',String),
                            Column('confidential',Integer),
                            Column('question_type',String),
                            Column('survey_specific_question',String(2000)),
                            )
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

    schema = {
            'numerical_responses':numerical_responses,
            'survey_specific_questions':survey_specific_questions,
            'question':question,
            'question_category':question_category,
            'response':response,
            'survey':survey,
            'survey_question':survey_question,
        }
    conn = engine.connect()

    return {'conn':conn,'schema':schema,'engine':engine}

@pytest.fixture
def migrator_with_ssq_for_survey(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    ssq_cols = ['survey_specific_qid', 'survey']
    ssq_rows = [('2014Inst-EIS-CSI1','2014Inst-EIS'),
                ('1415F8W-CSI1','1415F8W'),
                ('1415F8W-CSI2','1415F8W')]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_extract_survey_code_from_survey_specific_questions(migrator_with_ssq_for_survey):
    m = migrator_with_ssq_for_survey
    assert len(m.survey_df.index)==2

def test_assign_survey_id_and_map(migrator_with_ssq_for_survey):
    m = migrator_with_ssq_for_survey
    for i in m.survey_df.index:
        assert m.survey_df.loc[i,'survey_id'] == m.survey_id_survey_code_map[m.survey_df.loc[i,'survey_code']]

def test_assign_question_text(migrator_with_ssq_for_survey):
    m = migrator_with_ssq_for_survey
    assert m.survey_df.set_index('survey_code').get_value('1415F8W','survey_title') =='2014-15 First 8 Weeks CM Survey'

@pytest.fixture
def empty_migrator(empty_db):
    conn = empty_db['conn']
    return Migrator(empty_db['engine'],conn)

def test_basic_question_category_df(empty_migrator):
    m = empty_migrator
    expected_df = pd.DataFrame({'question_category_id':[1,2],'question_category':['CSI','CALI']})
    pd.util.testing.assert_frame_equal(m.question_category_df.set_index('question_category'), expected_df.set_index('question_category'))
    
@pytest.fixture
def migrator_with_ssq_for_survey_question(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
                ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_basic_fields_in_survey_question(migrator_with_ssq_for_survey_question):
    m = migrator_with_ssq_for_survey_question
    expected_records = [
                ('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
                ]
    expected_columns = ['survey_specific_qid','master_qid','survey','is_confidential','question_type','survey_specific_question']
    expected_df = pd.DataFrame.from_records(expected_records,columns=expected_columns)
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.survey_question_df,columns=expected_columns), expected_df)

def test_question_code_survey_column(migrator_with_ssq_for_survey_question):
    m = migrator_with_ssq_for_survey_question
    for i in m.survey_question_df.index:
        assert m.survey_question_df.get_value(i,'survey_question_code') == m.survey_question_df.get_value(i,'survey') + m.survey_question_df.get_value(i,'master_qid')

def test_survey_question_code_survey_question_id_map(migrator_with_ssq_for_survey_question):
    m = migrator_with_ssq_for_survey_question
    for i in m.survey_question_df.index:
        assert m.survey_question_df.loc[i,'survey_question_id'] == m.survey_question_code_survey_question_id_map[m.survey_question_df.loc[i,'survey_question_code']]

@pytest.fixture
def migrator_with_ssq_for_question(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('2014Inst-EIS-Institute1','Institute1','2014Inst-EIS',1,'7pt_1=SA','This is an institute question!'),
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
                ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_most_recent_version_of_question_used_on_question(migrator_with_ssq_for_question):
    m = migrator_with_ssq_for_question
    expected_records = [
                ('Institute1','This is an institute question!'),
                ('CSI1','This is CSI question 1!'),
                ('CSI2','This is CSI question 2!'),
                ]
    expected_columns = ['question_code','question_title']
    expected_df = pd.DataFrame.from_records(expected_records,columns=expected_columns)
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.question_df,columns=expected_columns).set_index('question_code').sort_index(), expected_df.set_index('question_code').sort_index())

def test_question_code_question_id_map(migrator_with_ssq_for_question):
    m = migrator_with_ssq_for_question
    assert m.question_df.set_index('question_id').index.is_unique
    for i in m.question_df.index:
        assert m.question_df.loc[i,'question_id'] == m.question_code_question_id_map[m.question_df.loc[i,'question_code']]

def test_map_of_question_category_id_on_survey_question(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    ssq_cols = ['master_qid','survey']
    ssq_rows = [
                ('CSI1','1415F8W'),
                ('CLI1','1415F8W'),
                ('OTH1','1415F8W'),
                ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    m = Migrator(empty_db['engine'],conn)
    df = m.survey_question_df.set_index('master_qid')
    cat_df = m.question_category_df.set_index('question_category')
    assert cat_df.loc['CSI','question_category_id'] == df.get_value('CSI1','question_category_id') 
    assert cat_df.loc['CALI','question_category_id'] == df.get_value('CLI1','question_category_id') 
    assert np.isnan(df.get_value('OTH1','question_category_id'))

def test_map_of_survey_id_on_survey_question(migrator_with_ssq_for_survey_question):
    m = migrator_with_ssq_for_survey_question
    s = m.survey_df.set_index('survey_id')
    sq = m.survey_question_df
    for idx in sq.index:
        assert s.get_value(sq.get_value(idx,'survey_id'),'survey_code') == sq.get_value(idx,'survey')

def test_map_of_question_id_on_survey_question(migrator_with_ssq_for_survey_question):
    m = migrator_with_ssq_for_survey_question
    q = m.question_df.set_index('question_id')
    m.question_code_question_id_map
    sq = m.survey_question_df
    for idx in sq.index:
        assert q.get_value(sq.get_value(idx,'question_id'),'question_code') == sq.get_value(idx,'master_qid')

def test_override_titlte(migrator_with_ssq_for_question):
    m = migrator_with_ssq_for_question
    m.question_code_question_id_map
    sq = m.survey_question_df.set_index('survey_specific_qid')
    assert sq.get_value('2014Inst-EIS-CSI1','question_title_override') == 'This is CSI question 1 for institute!'
    assert sq.get_value('2014Inst-EIS-Institute1','question_title_override') is None

@pytest.fixture
def migrator_with_ssq_and_nr_for_response(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    numerical_responses = empty_db['schema']['numerical_responses']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
                ]
    nr_cols = ['cm_pid','survey_specific_qid','response']
    nr_rows = [
        (1,'1415F8W-CSI1',1),
        (2,'1415F8W-CSI1',3),
        (3,'1415F8W-CSI1',5),
        (4,'1415F8W-CSI1',8),
    ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    for row in nr_rows:
        conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_basic_fields_for_response(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    expected_records = [
        (1,'1415F8W-CSI1',7.0),
        (2,'1415F8W-CSI1',5.0),
        (3,'1415F8W-CSI1',3.0),
        (4,'1415F8W-CSI1',np.nan),
    ]
    expected_columns = ['person_id','survey_specific_qid','response']
    expected_df = pd.DataFrame.from_records(expected_records,columns=expected_columns)
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.response_df,columns=expected_columns), expected_df)

def test_map_survey_question_id_on_response(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    sq = m.survey_question_df.set_index('survey_question_id')
    resp = m.response_df
    for idx in resp.index:
        assert sq.get_value(resp.get_value(idx,'survey_question_id'),'survey_specific_qid') == resp.get_value(idx,'survey_specific_qid')

def test_converted_net_value_mapping(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    assert (m.response_df.ix[m.response_df.response >= 6,'converted_net_value'] == 1).all()
    assert (m.response_df.ix[(m.response_df.response <= 4) & (m.response_df.response >= 0),'converted_net_value'] == -1).all()
    assert (m.response_df.ix[m.response_df.response == 5,'converted_net_value'] == 0).all()
    assert (np.isnan(m.response_df.ix[m.response_df.response.isnull(),'converted_net_value'])).all()

def test_migrate_survey_table_to_new_schema(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    m.migrate_to_new_schema()
    records = m.db.execute(select([m.table['survey']]))
    table_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.survey_df,columns=records.keys()), table_df)

def test_migrate_response_table_to_new_schema(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    m.migrate_to_new_schema()
    records = m.db.execute(select([m.table['response']]))
    table_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.response_df,columns=records.keys()), table_df)

def test_migrate_question_table_to_new_schema(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    m.migrate_to_new_schema()
    records = m.db.execute(select([m.table['question']]))
    table_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.question_df,columns=records.keys()), table_df)

def test_migrate_survey_question_table_to_new_schema(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    m.migrate_to_new_schema()
    records = m.db.execute(select([m.table['survey_question']]))
    table_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.survey_question_df,columns=records.keys()), table_df.convert_objects())

def test_migrate_question_category_table_to_new_schema(migrator_with_ssq_and_nr_for_response):
    m = migrator_with_ssq_and_nr_for_response
    m.migrate_to_new_schema()
    records = m.db.execute(select([m.table['question_category']]))
    table_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    pd.util.testing.assert_frame_equal(pd.DataFrame(m.question_category_df,columns=records.keys()).set_index('question_category'), table_df.convert_objects().set_index('question_category'))

def test_remove_duplicate_response_row(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    numerical_responses = empty_db['schema']['numerical_responses']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ]
    nr_cols = ['cm_pid','survey_specific_qid','response']
    nr_rows = [
        (1,'1415F8W-CSI1',1),
        (2,'1415F8W-CSI1',3),
        (2,'1415F8W-CSI1',4),
        (3,'1415F8W-CSI1',5),
        (4,'1415F8W-CSI1',8),
    ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    for row in nr_rows:
        conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
    m = Migrator(empty_db['engine'],conn)
    assert (m.response_df.groupby('person_id').size()==1).all()

def test_get_question_category_from_csv(empty_migrator):
    m = empty_migrator
    survey_specific_questions = m.table['survey_specific_questions']
    ssq_cols = ['master_qid','survey']
    ssq_rows = [
        ('Culture7','1314MYS'),
        ('Culture7','1415F8W')
    ]
    m.survey_order = ['1415F8W','1314MYS']
    for row in ssq_rows:
        m.db.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})


    question_category_df = pd.DataFrame({'question_code':['Culture7'],'survey':['1415F8W'],'question_category':'CSI'})
    m.question_category_csv = 'sample_file.csv'
    with patch('pandas.read_csv',return_value=question_category_df) as mock_question_category_csv:
        m.question_code_question_id_map
        df = m.survey_question_df.merge(m.question_df, how='outer').merge(m.question_category_df, how='outer').merge(m.survey_df, how='outer').ix[:,['survey_code','question_category']].set_index('survey_code')
    mock_question_category_csv.assert_called_with('sample_file.csv')
    assert df.get_value('1415F8W','question_category') == 'CSI'
    assert np.isnan(df.get_value('1314MYS','question_category'))

def test_import_of_survey_titles_from_external_file(empty_migrator):
    m = empty_migrator
    survey_title_df  = pd.DataFrame({'survey_code':['1314F8W','1314MYS'],'survey_title':['A F8W survey','A mid-year survey']})
    m.survey_title_csv = 'sample_file.csv'
    with patch('pandas.read_csv',return_value=survey_title_df) as mock_survey_title_csv:
        assert m.survey_code_title_map['1314F8W'] == 'A F8W survey'
    mock_survey_title_csv.assert_called_with('sample_file.csv')

def test_order_of_surveys_extracted_from_survey_title(empty_migrator):
    m = empty_migrator
    m.survey_code_title_map = pd.Series(['Most recent survey','An older survey'],['SUR1','SUR2'])
    assert m.survey_order == ['SUR1','SUR2']

@pytest.fixture
def migrator_with_ssq_and_nr_for_nps_computations(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    numerical_responses = empty_db['schema']['numerical_responses']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('2014Inst-EIS-NPS1','NPS1','2014Inst-EIS',1,'10pt_NPS_1=SA','This is NPS question 1 for institute!'),
                ('1415F8W-NPS1','NPS1','1415F8W',1,'10pt_NPS_1=SA','This is NPS question 1!'),
                ('1415F8W-NPS2','NPS2','1415F8W',1,'10pt_NPS_1=SA','This is NPS question 2!')
                ]
    nr_cols = ['cm_pid','survey_specific_qid','response']
    nr_rows = [
        (1,'1415F8W-NPS1',1),
        (2,'1415F8W-NPS1',4),
        (3,'1415F8W-NPS1',8),
        (4,'1415F8W-NPS1',11),
    ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    for row in nr_rows:
        conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_converted_net_value_mapping_for_nps(migrator_with_ssq_and_nr_for_nps_computations):
    m = migrator_with_ssq_and_nr_for_nps_computations
    assert (m.response_df.ix[m.response_df.response >= 9,'converted_net_value'] == 1).all()
    assert (m.response_df.ix[(m.response_df.response <= 6) & (m.response_df.response >= 1),'converted_net_value'] == -1).all()
    assert (m.response_df.ix[(m.response_df.response <= 8) & (m.response_df.response >= 7),'converted_net_value'] == 0).all()
    assert (np.isnan(m.response_df.ix[m.response_df.response.isnull(),'converted_net_value'])).all()

@pytest.fixture
def migrator_with_ssq_and_nr_for_separate_surveys(empty_db):
    conn = empty_db['conn']
    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    numerical_responses = empty_db['schema']['numerical_responses']
    ssq_cols = ['survey_specific_qid','master_qid','survey','confidential','question_type','survey_specific_question']
    ssq_rows = [
                ('2014Inst-EIS-CSI1','CSI1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('2014Inst-EIS-Inst1','Inst1','2014Inst-EIS',1,'7pt_1=SA','This is CSI question 1 for institute!'),
                ('1415F8W-CSI1','CSI1','1415F8W',1,'7pt_1=SA','This is CSI question 1!'),
                ('1415F8W-CSI2','CSI2','1415F8W',1,'7pt_1=SA','This is CSI question 2!')
                ]
    nr_cols = ['cm_pid','survey','survey_specific_qid','response']
    nr_rows = [
        (1,'2014Inst','2014Inst-EIS-CSI1',1),
        (2,'2014Inst','2014Inst-EIS-Inst1',3),
        (3,'1415F8W','1415F8W-CSI1',5),
        (4,'1415F8W','1415F8W-CSI2',8),
    ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    for row in nr_rows:
        conn.execute(numerical_responses.insert(), {c:v for c,v in zip(nr_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_survey_df_when_survey_specified(migrator_with_ssq_and_nr_for_separate_surveys):
    m = migrator_with_ssq_and_nr_for_separate_surveys
    m.surveys_to_migrate = ['1415F8W']
    assert (m.survey_df.survey_code == '1415F8W').all()

def test_survey_question_df_when_survey_specified(migrator_with_ssq_and_nr_for_separate_surveys):
    m = migrator_with_ssq_and_nr_for_separate_surveys
    m.surveys_to_migrate = ['1415F8W']
    df = m.survey_question_df.merge(m.survey_df,how='outer')
    assert (df.survey_code == '1415F8W').all()

def test_question_df_when_survey_specified(migrator_with_ssq_and_nr_for_separate_surveys):
    m = migrator_with_ssq_and_nr_for_separate_surveys
    m.surveys_to_migrate = ['1415F8W']
    df = m.survey_question_df.merge(m.survey_df,how='outer').merge(m.question_df,how='outer')
    assert (df.survey_code == '1415F8W').all()

def test_response_df_when_survey_specified(migrator_with_ssq_and_nr_for_separate_surveys):
    m = migrator_with_ssq_and_nr_for_separate_surveys
    m.surveys_to_migrate = ['1415F8W']
    df = m.response_df.merge(m.survey_question_df,how='outer').merge(m.survey_df,how='outer')
    assert (df.survey_code == '1415F8W').all()

@pytest.fixture
def migrator_with_data_already_migrated(empty_db):
    conn = empty_db['conn']
    survey = empty_db['schema']['survey']
    survey_cols = ['survey_id','survey_code']
    survey_rows = [
                (1,'1415F8W'),
                (2,'1314EYS'),
                ]
    for row in survey_rows:
        conn.execute(survey.insert(), {c:v for c,v in zip(survey_cols,row)})
    survey_question = empty_db['schema']['survey_question']
    survey_question_cols = ['survey_question_id','survey_id','question_id']
    survey_question_rows = [
                (1,1,1),
                (2,2,2),
                (3,1,3),
                (4,2,3),
                ]
    for row in survey_question_rows:
        conn.execute(survey_question.insert(), {c:v for c,v in zip(survey_question_cols,row)})

    response = empty_db['schema']['response']
    response_cols = ['person_id','survey_question_id']
    response_rows = [
                (1,1),
                (2,2),
                ]
    for row in response_rows:
        conn.execute(response.insert(), {c:v for c,v in zip(response_cols,row)})

    question = empty_db['schema']['question']
    question_cols = ['question_id','question_code']
    question_rows = [
                (1,'F8W1'),
                (2,'MYS1'),
                (3,'ALL1'),
                ]
    for row in question_rows:
        conn.execute(question.insert(), {c:v for c,v in zip(question_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_clean_up_survey_df(migrator_with_data_already_migrated):
    m = migrator_with_data_already_migrated
    m.surveys_to_migrate = ['1415F8W']
    m.remove_old_migrated_data()
    records = m.db.execute(select([m.table['survey']]))
    df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
    assert (~df.survey_code.isin(m.surveys_to_migrate)).all()

def test_clean_up_survey_question_df(migrator_with_data_already_migrated):
    m = migrator_with_data_already_migrated
    m.surveys_to_migrate = ['1415F8W']
    m.remove_old_migrated_data()
    survey_records = m.db.execute(select([m.table['survey']]))
    survey_df = pd.DataFrame.from_records(survey_records.fetchall(),columns=survey_records.keys())
    survey_question_records = m.db.execute(select([m.table['survey_question']]))
    survey_question_df = pd.DataFrame.from_records(survey_question_records.fetchall(),columns=survey_question_records.keys())
    df = survey_question_df.merge(survey_df,how='outer')
    assert ((~df.survey_code.isin(m.surveys_to_migrate)) & df.survey_code.notnull()).all()

def test_clean_up_response_df(migrator_with_data_already_migrated):
    m = migrator_with_data_already_migrated
    m.surveys_to_migrate = ['1415F8W']
    m.remove_old_migrated_data()
    survey_records = m.db.execute(select([m.table['survey']]))
    survey_df = pd.DataFrame.from_records(survey_records.fetchall(),columns=survey_records.keys())
    survey_question_records = m.db.execute(select([m.table['survey_question']]))
    survey_question_df = pd.DataFrame.from_records(survey_question_records.fetchall(),columns=survey_question_records.keys())
    response_records = m.db.execute(select([m.table['response']]))
    response_df = pd.DataFrame.from_records(response_records.fetchall(),columns=response_records.keys())
    df = response_df.merge(survey_question_df,how='outer').merge(survey_df,how='outer')
    assert ((~df.survey_code.isin(m.surveys_to_migrate)) & df.survey_code.notnull()).all()

def test_remove_orphaned_questions(migrator_with_data_already_migrated):
    m = migrator_with_data_already_migrated
    m.surveys_to_migrate = ['1415F8W']
    m.remove_old_migrated_data()
    survey_records = m.db.execute(select([m.table['survey']]))
    survey_df = pd.DataFrame.from_records(survey_records.fetchall(),columns=survey_records.keys())
    survey_question_records = m.db.execute(select([m.table['survey_question']]))
    survey_question_df = pd.DataFrame.from_records(survey_question_records.fetchall(),columns=survey_question_records.keys())
    question_records = m.db.execute(select([m.table['question']]))
    question_df = pd.DataFrame.from_records(question_records.fetchall(),columns=question_records.keys())
    df = question_df.merge(survey_question_df,how='outer').merge(survey_df,how='outer')
    assert ((~df.survey_code.isin(m.surveys_to_migrate)) & df.survey_code.notnull()).all()
    assert 'ALL1' in df.question_code.values

@pytest.fixture
def migrator_with_data_already_migrated_and_new_ssq_and_nr(empty_db):
    conn = empty_db['conn']
    survey = empty_db['schema']['survey']
    survey_cols = ['survey_id','survey_code']
    survey_rows = [
                (1,'1314EYS'),
                ]
    for row in survey_rows:
        conn.execute(survey.insert(), {c:v for c,v in zip(survey_cols,row)})

    survey_specific_questions = empty_db['schema']['survey_specific_questions']
    numerical_responses = empty_db['schema']['numerical_responses']
    ssq_cols = ['survey_specific_qid','master_qid','survey']
    ssq_rows = [
                ('1415F8W-CSI1','CSI1','1415F8W'),
                ]
    for row in ssq_rows:
        conn.execute(survey_specific_questions.insert(), {c:v for c,v in zip(ssq_cols,row)})
    return Migrator(empty_db['engine'],conn)

def test_new_survey_id_creation(migrator_with_data_already_migrated_and_new_ssq_and_nr):
    m = migrator_with_data_already_migrated_and_new_ssq_and_nr
    m.surveys_to_migrate = ['1415F8W']
    survey_records = m.db.execute(select([m.table['survey']]))
    survey_df = pd.DataFrame.from_records(survey_records.fetchall(),columns=survey_records.keys())
    assert (~m.survey_df.survey_id.isin(survey_df.survey_id)).all()