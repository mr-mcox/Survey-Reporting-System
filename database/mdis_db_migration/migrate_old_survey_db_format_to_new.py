import pandas as pd

#Read data
responses = pd.read_csv('numerical_responses.csv')
question_table = pd.read_csv('survey_specific_questions.csv')

#Create survey table data
survey_codes = question_table.survey.unique().tolist()
survey_map = dict(zip(survey_codes,range(len(survey_codes))))
survey_ids = [survey_map[survey_name] for survey_name in survey_codes]

pd.DataFrame({'id':survey_ids,'survey_code':survey_codes}).to_csv('surveys.csv')

#Create question table data
questions = question_table.survey_specific_qid.unique().tolist()
question_map = dict(zip(questions,range(len(questions))))

question_table['question_id'] = question_table.survey_specific_qid.map(question_map)
question_table['survey_id'] = question_table.survey.map(survey_map)
question_table = question_table.rename(columns={'master_qid':'question_code','question_id':'id'})
pd.DataFrame(question_table,columns=['id','survey_id','question_code']).to_csv('questions.csv')

#Map survey id and question id onto survey responses
responses['question_id'] = responses.survey_specific_qid.map(question_map)
responses['survey_id'] = responses.survey.map(survey_map)
responses = responses.rename(columns={'cm_pid':'respondent_id'})

#Create results table
pd.DataFrame(responses,columns=['respondent_id','survey_id','question_id','response']).to_csv('responses.csv')
