from sqlalchemy import Table, Column, Integer, String, MetaData, select
import pandas as pd
import numpy as np

class Migrator(object):
    """docstring for migrate"""
    def __init__(self, engine, connection):
        

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
        self.engine = engine

        self.survey_code_title_map = {
            '1415F8W' : '2014-15 First 8 Weeks CM Survey',
            '2014Inst-EIS' : '2014 End of Institute CM Survey',
        }
        self.question_category_df = pd.DataFrame({'question_category_id':[1,2],'question_category':['CALI','CSI']})
        self.question_category_question_code_map = {
                                                        'CSI2' : 2,
                                                        'CSI1' : 2,
                                                        'CSI8' : 2,
                                                        'CSI10' :2,
                                                        'CSI12' :2,
                                                        'CSI4' : 2,
                                                        'CSI5' : 2,
                                                        'CSI6' : 2,
                                                        'Culture1' : 2,
                                                        'CSI3' : 2,
                                                        'CSI7' : 2,
                                                        'CLI1' : 1,
                                                        'CLI2' : 1,
                                                        'CLI3' : 1,
                                                        'CLI4' : 1,
                                                        'CLI5' : 1,
                                                        'CLI6' : 1,
                                                        'CLI7' : 1,
                                                        'CLI8' : 1,
                                                    }
        self.survey_order = ['1415F8W','2014Inst-EIS']

    def survey_df():
        doc = "The survey_df property."
        def fget(self):
            if not hasattr(self,'_survey_df'):
                records = self.db.execute(select([self.table['survey_specific_questions'].c.survey]))
                df = pd.DataFrame({'survey':[r[0] for r in records.fetchall()]})
                _survey_df = df.drop_duplicates()
                _survey_df['survey_code'] = _survey_df.survey
                _survey_df['survey_id'] = [i + 1 for i in range(len(_survey_df.index))]
                _survey_df['survey_title'] = _survey_df.survey_code.map(self.survey_code_title_map)
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

    def survey_question_df():
        doc = "The survey_question_df property."
        def fget(self):
            if not hasattr(self,'_survey_question_df'):
                records = self.db.execute(select([self.table['survey_specific_questions']]))
                df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
                df['survey_question_code'] = df.survey + df.master_qid
                df['survey_question_id'] = [i + 1 for i in range(len(df.index))]
                df['question_category_id'] = df.master_qid.map(self.question_category_question_code_map)
                df['survey_id'] = df.survey.map(self.survey_id_survey_code_map)
                df['question_title_override'] = None
                self._survey_question_df = df.rename(columns={'confidential':'is_confidential'})
            return self._survey_question_df
        def fset(self, value):
            self._survey_question_df = value
        def fdel(self):
            del self._survey_question_df
        return locals()
    survey_question_df = property(**survey_question_df())

    def survey_question_code_survey_question_id_map():
        doc = "The survey_question_code_survey_question_id_map property."
        def fget(self):
            if not hasattr(self,'_survey_question_code_survey_question_id_map'):
                self._survey_question_code_survey_question_id_map = dict(zip(self.survey_question_df.survey_question_code.tolist(),
                                                                            self.survey_question_df.survey_question_id.tolist()))
            return self._survey_question_code_survey_question_id_map
        def fset(self, value):
            self._survey_question_code_survey_question_id_map = value
        def fdel(self):
            del self._survey_question_code_survey_question_id_map
        return locals()
    survey_question_code_survey_question_id_map = property(**survey_question_code_survey_question_id_map())


    def question_df():
        doc = "The question_df property."
        def fget(self):
            if not hasattr(self,'_question_df'):
                sq = self.survey_question_df.set_index('survey_question_code')
                records = list()
                #Create list of questions
                questions = self.survey_question_df.master_qid.unique().tolist()
                for question_code in questions:
                    found_question = False
                    question_title = None
                    for survey in self.survey_order:
                        if (survey + question_code) in sq.index:
                            question_title = sq.get_value((survey + question_code),'survey_specific_question')
                            found_question = True
                            break
                    assert found_question
                    records.append((question_code,question_title))
                df = pd.DataFrame.from_records(records,columns=['question_code','question_title'])
                df['question_id'] = [i + 1 for i in range(len(df.index))]
                self._question_df = df
            return self._question_df
        def fset(self, value):
            self._question_df = value
        def fdel(self):
            del self._question_df
        return locals()
    question_df = property(**question_df())

    def question_code_question_id_map():
        doc = "The question_code_question_id_map property."
        def fget(self):
            if not hasattr(self,'_question_code_question_id_map'):
                self._question_code_question_id_map = dict(zip(self.question_df.question_code.tolist(),
                                                                            self.question_df.question_id.tolist()))
                #This code smells. Is there a better way?
                if 'master_qid' in self.survey_question_df.columns:
                    self.survey_question_df['question_id'] = self.survey_question_df.master_qid.map(self._question_code_question_id_map)
                    #Set override
                    q = self.question_df.set_index('question_id')
                    for idx in self.survey_question_df.index:
                        if self.survey_question_df.get_value(idx, 'survey_specific_question') != q.get_value(self.survey_question_df.get_value(idx, 'question_id'),'question_title'):
                            self.survey_question_df.loc[idx,'question_title_override'] = self.survey_question_df.loc[idx,'survey_specific_question']
            return self._question_code_question_id_map
        def fset(self, value):
            self._question_code_question_id_map = value
        def fdel(self):
            del self._question_code_question_id_map
        return locals()
    question_code_question_id_map = property(**question_code_question_id_map())

    def response_df():
        doc = "The response_df property."
        def fget(self):
            if not hasattr(self,'_response_df'):
                records = self.db.execute(select([self.table['numerical_responses']]))
                df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys()).rename(columns={'cm_pid':'person_id'})
                survey_specific_qid_question_id_map = dict(zip(self.survey_question_df.survey_specific_qid.tolist(),
                                                                            self.survey_question_df.survey_question_id.tolist()))
                df['survey_question_id'] = df.survey_specific_qid.map(survey_specific_qid_question_id_map)
                df['converted_net_value'] = np.nan
                df.ix[df.response <= 2,'converted_net_value'] = 1
                df.ix[df.response == 3,'converted_net_value'] = 0
                df.ix[(df.response >= 4) & (df.response <= 7),'converted_net_value'] = -1
                self._response_df = df
            return self._response_df
        def fset(self, value):
            self._response_df = value
        def fdel(self):
            del self._response_df
        return locals()
    response_df = property(**response_df())

    def migrate_to_new_schema(self):
        self.survey_df.ix[:,['survey_id','survey_code','survey_title']].to_sql('cm_survey',self.engine,index=False,if_exists='append')
        self.response_df.ix[:,['person_id','survey_question_id','response','converted_net_value']].to_sql('cm_response',self.engine,index=False,if_exists='append')
        self.question_df.ix[:,['question_id',
                 'question_title',
                'question_code']
                ].to_sql('cm_question',self.engine,index=False,if_exists='append')
        self.survey_question_df.ix[:,['survey_question_id',
                                 'survey_id',
                                'is_confidential',
                                'question_type',
                                'question_title_override',
                                'question_id',
                                'question_category_id',]
                                ].to_sql('cm_survey_question',self.engine,index=False,if_exists='append')
