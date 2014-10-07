from sqlalchemy import Table, Column, Integer, String, MetaData, select
import pandas as pd

class Migrator(object):
    """docstring for migrate"""
    def __init__(self, connection):
        

        metadata = MetaData()
        #Tables
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
                                Column('question_type',String)
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
        self.table = {
            'numerical_responses':numerical_responses,
            'survey_specific_questions':survey_specific_questions,
            'question':question,
            'question_category':question_category,
            'response':response,
            'survey':survey,
            'survey_question':survey_question,
        }
        self.db = connection

    def survey_df():
        doc = "The survey_df property."
        def fget(self):
            if not hasattr(self,'_survey_df'):
                records = self.db.execute(select([self.table['survey_specific_questions'].c.survey]))
                df = pd.DataFrame({'survey':[r[0] for r in records.fetchall()]})
                _survey_df = df.drop_duplicates()
                _survey_df['survey_code'] = _survey_df.survey
                _survey_df['survey_id'] = [i + 1 for i in range(len(_survey_df.index))]
                self._survey_df = _survey_df
            return self._survey_df
        def fset(self, value):
            self._survey_df = value
        def fdel(self):
            del self._survey_df
        return locals()
    survey_df = property(**survey_df())

    def survey_id_survey_code_map():
        doc = "The survey_id_survey_code_map property."
        def fget(self):
            if not hasattr(self,'_survey_id_survey_code_map'):
                self._survey_id_survey_code_map = dict(zip(self.survey_df.survey_code.tolist(),self.survey_df.survey_id.tolist()))
            return self._survey_id_survey_code_map
        def fset(self, value):
            self._survey_id_survey_code_map = value
        def fdel(self):
            del self._survey_id_survey_code_map
        return locals()
    survey_id_survey_code_map = property(**survey_id_survey_code_map())

#Create survey question category map based on question code and asign arbitrary ids

#Create map of question code to question_category_id

#Extract survey code and title from survey_specific_questions

#Write survey title

#Assign survey_id and map to survey code

#Extract question code, title, confidential, survey_specific_qid and survey from survey_specific_questions

#Create question_code_survey column, survey_question_id and map

#Pick most recent question title based on most recent survey

#Create question_id and map

#Map question_category_id on survey_question

#Map survey_id on survey_question

#Map question_id on survey_question

#Create question_override title if survey question doesn't match with associated question

#Extract survey_specific_qid, cm_pid, repsonse from numeric_responses

#Map responses based on survey_specific_qid

#Map converted_net_value based on response

#Import survey

#Import survey_question_category

#Import survey_question

#Import question

#Import cm_survey_response