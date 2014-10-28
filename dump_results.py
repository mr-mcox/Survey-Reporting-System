from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.ResponsesRetriever import ResponsesRetriever
import logging
import sys
import re

logging.basicConfig(filename='debug.log',level=logging.WARNING)
arguments = sys.argv
command_run = arguments.pop(0)
output_file = 'responses.csv'

#If csv file is specified as a first argument, use that as the output
if re.search('\.csv',arguments[0]) is not None:
	output_file = arguments.pop(0)
else:
	if len(arguments) >= 2:
		output_file = 'hist_responses.csv'

# Read connection info
connect_info = 'mssql+pyodbc://survey_user:surveyProd1!@tpsd_survey'

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResponsesRetriever.ResponsesRetriever(db_connection=db)
print("Starting to retrieve responses")
responses = retriever.retrieve_responses_for_survey(survey_code=arguments)
responses_df = pd.DataFrame(responses['rows'])
responses_df.columns = responses['column_headings']

responses_df.to_csv(output_file)