from sqlalchemy import Table, Column, Integer, String, MetaData, select
import pandas as pd
import numpy as np
from SurveyReportingSystem.NumericOutputCalculator.noc_helper import map_responses_to_net_formatted_values
import logging
import pdb

class Migrator(object):
    """docstring for migrate"""
    def __init__(self, engine, connection, **kwargs):

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

        self.question_category_csv = kwargs.pop('question_category_csv',None)
        self.survey_title_csv = kwargs.pop('survey_title_csv',None)
        self.cm_id_map_csv = kwargs.pop('cm_id_map_csv',None)
        self.legal_person_ids_csv = kwargs.pop('legal_person_ids_csv',None)
        self.surveys_to_migrate = kwargs.pop('surveys_to_migrate',list())
        self.clean_CSI = kwargs.pop('clean_CSI',False)
        self.clean_CALI = kwargs.pop('clean_CALI',False)

    def survey_code_title_map():
        doc = "The survey_code_title_map property."
        def fget(self):
            if not hasattr(self,'_survey_code_title_map'):
                if self.survey_title_csv is None:
                    self._survey_code_title_map = pd.Series(
                        ['2013-14 End of Year CM Survey','2014 End of Institute CM Survey','2014-15 First 8 Weeks CM Survey'],
                        ['1314EYS','2014Inst-EIS','1415F8W'])
                else:
                    df = pd.read_csv(self.survey_title_csv)
                    self._survey_code_title_map = df.set_index('survey_code').survey_title
            return self._survey_code_title_map
        def fset(self, value):
            self._survey_code_title_map = value
        def fdel(self):
            del self._survey_code_title_map
        return locals()
    survey_code_title_map = property(**survey_code_title_map())

    def survey_order():
        doc = "The survey_order property."
        def fget(self):
            if not hasattr(self,'_survey_order'):
                self._survey_order = [x for x in reversed(self.survey_code_title_map.index.tolist())]
            return self._survey_order
        def fset(self, value):
            self._survey_order = value
        def fdel(self):
            del self._survey_order
        return locals()
    survey_order = property(**survey_order())

    def survey_df():
        doc = "The survey_df property."
        def fget(self):
            if not hasattr(self,'_survey_df'):
                records = None
                ssq = self.table['survey_specific_questions']
                if self.surveys_to_migrate:
                    records = self.db.execute(select([ssq.c.survey]).where(ssq.c.survey.in_(self.surveys_to_migrate)))
                else:
                    records = self.db.execute(select([ssq.c.survey]))
                df = pd.DataFrame({'survey':[r[0] for r in records.fetchall()]})
                _survey_df = df.drop_duplicates()
                _survey_df['survey_code'] = _survey_df.survey
                _survey_df['survey_id'] = [i + + self.max_id_for_table('survey') + 1 for i in range(len(_survey_df.index))]
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
                records = None
                ssq = self.table['survey_specific_questions'] 

                if self.surveys_to_migrate:
                    records = self.db.execute(select([ssq]).where(ssq.c.survey.in_(self.surveys_to_migrate)))
                else:
                    records = self.db.execute(select([ssq]))
                df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
                df['survey_question_code'] = df.survey + df.master_qid
                df['question_code'] = df.master_qid
                df['survey_question_id'] = [i + + self.max_id_for_table('survey_question') + 1 for i in range(len(df.index))]
                df['survey_id'] = df.survey.map(self.survey_id_survey_code_map)
                df['question_title_override'] = None
                #Fix question_types
                df.ix[df.question_type == '7pt_Net_1=SA','question_type'] = '7pt_1=SA'
                df.ix[df.question_type == '7pt_NCS_1=SA','question_type'] = '7pt_1=SA'
                df.ix[df.question_type == '7pt_NCS_7=SA','question_type'] = '7pt_7=SA'
                #Add question category id
                df = df.merge(self.survey_question_question_category_df, how='left')
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

                #First copy existing old ids
                question_records = self.db.execute(select([self.table['question']]))
                current_question_df = pd.DataFrame.from_records(question_records.fetchall(),columns=question_records.keys())
                existing_ids = current_question_df.set_index('question_code').question_id
                df = df.set_index('question_code')
                df['question_id'] = existing_ids
                df = df.reset_index()
                df['question_id_in_db'] = True

                #Create new ids
                df.ix[df.question_id.isnull(), 'question_id_in_db'] = False
                df.ix[df.question_id.isnull(), 'question_id'] = [i + self.max_id_for_table('question')+ 1 for i in range(df.question_id.isnull().sum())]
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

    def read_cm_id_map(self):
        return pd.read_csv(self.cm_id_map_csv)

    def read_legal_person_ids(self):
        return pd.read_csv(self.legal_person_ids_csv)

    def response_df():
        doc = "The response_df property."
        def fget(self):
            if not hasattr(self,'_response_df'):
                records = None
                nr = self.table['numerical_responses'] 
                if self.surveys_to_migrate:
                    records = self.db.execute(select([nr]).where(nr.c.survey.in_(self.surveys_to_migrate)))
                else:
                    records = self.db.execute(select([nr]))
                df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys()).rename(columns={'cm_pid':'person_id'})
                survey_specific_qid_question_id_map = dict(zip(self.survey_question_df.survey_specific_qid.tolist(),
                                                                            self.survey_question_df.survey_question_id.tolist()))
                df['survey_question_id'] = df.survey_specific_qid.map(survey_specific_qid_question_id_map)

                #Map ids
                if hasattr(self,'cm_id_map_csv') and self.cm_id_map_csv is not None:
                    cm_map = self.read_cm_id_map()
                    assert 'person_id' in cm_map
                    assert 'survey' in cm_map
                    assert 'new_person_id' in cm_map
                    assert 'person_id' in df
                    assert 'survey' in df
                    df = df.merge(cm_map, how='left')
                    if 'new_person_id' in df.columns:
                        df.ix[df.new_person_id.notnull(),'person_id'] = df.ix[df.new_person_id.notnull(),'new_person_id']

                pdb.set_trace()
                #Remove duplicate records
                df.drop_duplicates(['person_id','survey_question_id'],inplace=True)
                df = df.ix[df.survey_question_id.notnull() & df.person_id.notnull()]#Change this behaviour later

                pdb.set_trace()
                #Remove illegal person_ids
                if hasattr(self,'legal_person_ids_csv') and self.legal_person_ids_csv is not None:
                    legal_person_ids = self.read_legal_person_ids()
                    #Log ids removed
                    cms_to_remove = df.ix[~df.person_id.isin(legal_person_ids.person_id),['person_id','survey']].drop_duplicates()
                    for row in cms_to_remove.itertuples(index=False):
                        logging.info('person_id ' + str(row[0]) + ' removed from survey ' + row[1])
                    df = df.ix[df.person_id.isin(legal_person_ids.person_id)]

                pdb.set_trace()
                #Remove incomplete CSI
                if hasattr(self,'clean_CSI') and self.clean_CSI:
                    if 'question_category' not in df.columns:
                        df = df.merge(self.survey_question_df.ix[:,['survey_question_id','question_category']],how='outer')
                    clean_df = df.merge(self.survey_question_df)
                    count_by_pid = clean_df.groupby(['person_id','question_category','survey']).size()
                    count_by_pid.name = 'count'
                    count_by_pid = count_by_pid.reset_index()
                    count_for_max_response = count_by_pid.copy().drop('person_id',axis=1)
                    max_response = count_for_max_response.groupby(['question_category','survey']).max().rename(columns={'count':'max_count'}).reset_index()

                    df_with_max = count_by_pid.merge(max_response)

                    cm_to_remove = df_with_max.ix[(df_with_max['count'] < df_with_max.max_count) &  (df_with_max.question_category=='CSI')].set_index(['person_id','survey','question_category'])

                    if len(cm_to_remove.index) > 0:
                        df = df.set_index(['person_id','survey','question_category'])                   
                        df = df.ix[(~df.index.isin(cm_to_remove.index))].reset_index()
                pdb.set_trace()
                #Remove incomplete CALI
                if hasattr(self,'clean_CALI') and self.clean_CALI:
                    if 'question_category' not in df.columns:
                        df = df.merge(self.survey_question_df.ix[:,['survey_question_id','question_category']],how='outer')
                    clean_df = df.merge(self.survey_question_df)
                    count_by_pid = clean_df.groupby(['person_id','question_category','survey']).size()
                    count_by_pid.name = 'count'
                    count_by_pid = count_by_pid.reset_index()
                    count_for_max_response = count_by_pid.copy().drop('person_id',axis=1)
                    max_response = count_for_max_response.groupby(['question_category','survey']).max().rename(columns={'count':'max_count'}).reset_index()
                    df_with_max = count_by_pid.merge(max_response)
                    cm_to_remove = df_with_max.ix[(df_with_max['count'] < df_with_max.max_count) &  (df_with_max.question_category=='CALI')].set_index(['person_id','survey','question_category'])
                    
                    if len(cm_to_remove.index) > 0:
                        df = df.set_index(['person_id','survey','question_category'])
                        df = df.ix[(~df.index.isin(cm_to_remove.index))].reset_index()


                #Map converted_net_value
                df = df.set_index('survey_question_id').join(self.survey_question_df.set_index('survey_question_id').ix[:,'question_type']).reset_index()
                df = map_responses_to_net_formatted_values(df,responses_transformed=False).convert_objects()
                df['converted_net_value'] = df.net_formatted_value

                pdb.set_trace()
                self._response_df = df
            return self._response_df
        def fset(self, value):
            self._response_df = value
        def fdel(self):
            del self._response_df
        return locals()
    response_df = property(**response_df())

    def migrate_to_new_schema(self):
        logging.info("Deleting old responses")
        if hasattr(self,'surveys_to_migrate') and len(self.surveys_to_migrate) > 0:
            self.remove_old_migrated_data()
        else:
            self.db.execute(self.table['survey'].delete())
            self.db.execute(self.table['question'].delete())
            self.db.execute(self.table['survey_question'].delete())
            self.db.execute(self.table['question_category'].delete())
            self.db.execute(self.table['response'].delete())
        logging.info("Inserting survey records")
        self.db.execute(self.table['survey'].insert(),df_to_dict_array(self.survey_df.ix[:,['survey_id','survey_code','survey_title']]))
        question_category_records = self.question_df.ix[~self.question_df.question_id_in_db,['question_id','question_title','question_code']]
        if len(question_category_records.index) > 0:
            logging.info("Inserting question records")
            self.db.execute(self.table['question'].insert(),df_to_dict_array(question_category_records))
        question_category_records = self.question_category_df.ix[~self.question_category_df.question_category_id_in_db,['question_category_id','question_category']]
        if len(question_category_records.index) > 0:
            logging.info("Inserting question_category records")
            self.db.execute(self.table['question_category'].insert(),df_to_dict_array(question_category_records))
        logging.info("Inserting survey_question records")
        self.question_code_question_id_map #Also code smell
        survey_question_records = self.survey_question_df.ix[:,['survey_question_id',
                                                                'survey_id',
                                                                'is_confidential',
                                                                'question_type',
                                                                'question_title_override',
                                                                'question_id',
                                                                'question_category_id',]]
        if len(survey_question_records) > 0:
            self.db.execute(self.table['survey_question'].insert(),df_to_dict_array(survey_question_records))
        else:
            logging.info("No new survey questions were recorded")
        logging.info("Inserting response records")
        if len(self.surveys_to_migrate) > 0:
            for survey in self.surveys_to_migrate:
                logging.info("Inserting response records for survey " + str(survey))
                response_records = self.response_df.ix[self.response_df.survey == survey,['person_id','survey_question_id','response','converted_net_value']]
                if len(response_records.index) > 0:
                    self.db.execute(self.table['response'].insert(),df_to_dict_array(response_records))
                else:
                    logging.info("Survey " + str(survey) +  " has no responses to be recorded")
        else:
            response_records = self.response_df.ix[:,['person_id','survey_question_id','response','converted_net_value']]
            self.db.execute(self.table['response'].insert(),df_to_dict_array(response_records))
         
    def remove_old_migrated_data(self):
        survey = self.table['survey']
        survey_id_records = self.db.execute(select([survey.c.survey_id]).where(survey.c.survey_code.in_(self.surveys_to_migrate)))
        survey_to_delete_df = pd.DataFrame.from_records(survey_id_records.fetchall(),columns=survey_id_records.keys())
        self.db.execute(survey.delete().where(survey.c.survey_code.in_(self.surveys_to_migrate)))

        survey_question = self.table['survey_question']
        survey_id_to_delete = [ int(x) for x in survey_to_delete_df.survey_id.tolist() ]
        survey_question_id_records = self.db.execute(select([survey_question.c.survey_question_id]).where(survey_question.c.survey_id.in_(survey_id_to_delete)))
        survey_question_to_delete_df = pd.DataFrame.from_records(survey_question_id_records.fetchall(),columns=survey_question_id_records.keys())
        if len(survey_id_to_delete) > 0:
            self.db.execute(survey_question.delete().where(survey_question.c.survey_id.in_(survey_id_to_delete)))

        response = self.table['response']
        survey_question_id_to_delete = [ int(x) for x in survey_question_to_delete_df.survey_question_id.tolist() ]
        if len(survey_question_id_to_delete) > 0:
            self.db.execute(response.delete().where(response.c.survey_question_id.in_(survey_question_id_to_delete)))

        survey_question_records = self.db.execute(select([survey_question]))
        survey_question_df = pd.DataFrame.from_records(survey_question_records.fetchall(),columns=survey_question_records.keys())
        question = self.table['question']
        question_records = self.db.execute(select([question]))
        question_df = pd.DataFrame.from_records(question_records.fetchall(),columns=question_records.keys())
        orphaned_questions = question_df.ix[~question_df.question_id.isin(survey_question_df.question_id),'question_id']
        question_id_to_delete = [ int(x) for x in orphaned_questions.tolist() ]
        if len(question_id_to_delete) > 0:
            self.db.execute(question.delete().where(question.c.question_id.in_(question_id_to_delete)))

    def survey_question_question_category_df():
        doc = "The survey_question_question_category_df property."
        def fget(self):
            if not hasattr(self,'_survey_question_question_category_df'):
                df = pd.DataFrame()
                if self.question_category_csv is not None:
                    df = pd.read_csv(self.question_category_csv)
                    assert 'survey' in df.columns
                    assert 'question_code' in df.columns
                    assert 'question_category' in df.columns
                else:
                    df = pd.DataFrame.from_records([
                        ('CSI2'     , 'CSI'),
                        ('CSI1'     , 'CSI'),
                        ('CSI8'     , 'CSI'),
                        ('CSI10'    , 'CSI'),
                        ('CSI12'    , 'CSI'),
                        ('CSI4'     , 'CSI'),
                        ('CSI5'     , 'CSI'),
                        ('CSI6'     , 'CSI'),
                        ('Culture1' , 'CSI'),
                        ('CSI3'     , 'CSI'),
                        ('CSI7'     , 'CSI'),
                        ('CLI1'     , 'CALI'),
                        ('CLI2'     , 'CALI'),
                        ('CLI3'     , 'CALI'),
                        ('CLI4'     , 'CALI'),
                        ('CLI5'     , 'CALI'),
                        ('CLI6'     , 'CALI'),
                        ('CLI7'     , 'CALI'),
                        ('CLI8'     , 'CALI'),
                    ],columns=['question_code','question_category'])

                #First copy existing old ids
                question_category_records = self.db.execute(select([self.table['question_category']]))
                current_question_category_df = pd.DataFrame.from_records(question_category_records.fetchall(),columns=question_category_records.keys())
                existing_ids = current_question_category_df.set_index('question_category').question_category_id
                unique_category = df.question_category.unique().tolist()
                category_id_df = pd.DataFrame({'question_category':unique_category}).set_index('question_category')
                category_id_df['question_category_id'] = existing_ids
                category_id_df = category_id_df.reset_index()

                category_id_df['question_category_id_in_db'] = True


                #Then set new ids
                category_id_df.ix[category_id_df.question_category_id.isnull(),'question_category_id_in_db'] = False
                category_id_df.ix[category_id_df.question_category_id.isnull(),'question_category_id'] = [x + self.max_id_for_table('question_category') + 1 for x in range(category_id_df.question_category_id.isnull().sum())]                

                df = df.merge(category_id_df)
                self._survey_question_question_category_df = df
            return self._survey_question_question_category_df
        def fset(self, value):
            self._survey_question_question_category_df = value
        def fdel(self):
            del self._survey_question_question_category_df
        return locals()
    survey_question_question_category_df = property(**survey_question_question_category_df())

    def question_category_df():
        doc = "The question_category_df property."
        def fget(self):
            if not hasattr(self,'_question_category_df'):
                self._question_category_df = self.survey_question_question_category_df.ix[self.survey_question_question_category_df.question_category.notnull(),['question_category','question_category_id','question_category_id_in_db']].drop_duplicates()
            return self._question_category_df
        def fset(self, value):
            self._question_category_df = value
        def fdel(self):
            del self._question_category_df
        return locals()
    question_category_df = property(**question_category_df())

    def max_id_for_table(self,table):
        records = self.db.execute(select([self.table[table]]))
        current_df = pd.DataFrame.from_records(records.fetchall(),columns=records.keys())
        max_id = current_df[table + '_id'].max()
        if np.isnan(max_id):
            max_id = 0
        return max_id

#Some basic conversion of types needs to occur for the database library to be ok with it
def convert_types_for_db(values):
    new_values = list()
    for value in values:
        new_value = value
        if type(value) != str and type(value) != int and new_value is not None:
            new_value = np.asscalar(value)
        if type(new_value) == str:
            try:
                new_value = float(new_value)
            except:
                pass
        if type(new_value) != str  and new_value is not None:
            if np.isnan(new_value):
                new_value = None
            elif int(new_value) == new_value:
                new_value = int(new_value)
        new_values.append(new_value)
    return new_values

#Insert in new db
def df_to_dict_array(df):
    columns = df.columns
    list_of_rows = list()
    for row in df.itertuples(index=False):
        list_of_rows.append(dict(zip(columns,convert_types_for_db(row))))
    return list_of_rows