from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select
import logging

class ResponsesRetriever(object):
    """docstring for responseRetriever"""
    def __init__(self, **kwargs):
        self.db_connection = kwargs.pop('db_connection',None)

    def retrieve_responses_for_survey(self,**kwargs):
        survey_code = kwargs.pop('survey_code',None)
        if not type(survey_code) is list:
            survey_code = [survey_code]
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
            Column('survey_question_id', Integer, ForeignKey("cm_survey_question.survey_question_id"), primary_key=True, autoincrement=False),
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
            Column('survey_id', Integer, ForeignKey("cm_survey.survey_id")),
            Column('is_confidential', Integer),
            Column('question_type', String(20)),
            Column('question_title_override', String(2000)),
            Column('question_id', Integer, ForeignKey("cm_question.question_id")),
            Column('question_category_id', Integer),
            )
        assert survey_code != [None]
        sq = (select([survey],use_labels=True).where(survey.c.survey_code.in_(survey_code))).alias('sq')
        if len(survey_code) > 1:
            select_response = select([response.c.person_id.label('respondent_id'), response.c.response, question.c.question_code,survey_question.c.is_confidential,survey_question.c.question_type, sq.c.cm_survey_survey_code.label('survey_code')]).select_from(response.join(survey_question).join(question).join(sq))
        else:
            select_response = select([response.c.person_id.label('respondent_id'), response.c.response, question.c.question_code,survey_question.c.is_confidential,survey_question.c.question_type]).select_from(response.join(survey_question).join(question).join(select([survey],use_labels=True).where(survey.c.survey_code.in_(survey_code)).alias('sq')))
        logging.debug('retrieve_response_for_survey query:\n' + str(select_response))
        response = self.db_connection.execute(select_response)
        return  {'rows':response.fetchall(),'column_headings':response.keys()}