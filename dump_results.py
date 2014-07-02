from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging
import sys
import re

logging.basicConfig(filename='debug.log',level=logging.WARNING)
arguments = sys.argv
command_run = arguments.pop(0)
output_file = 'results.csv'

#If csv file is specified as a first argument, use that as the output
if re.search('\.csv',arguments[0]) is not None:
	output_file = arguments.pop(0)
else:
	if len(arguments) >= 2:
		output_file = 'hist_results.csv'

# Read connection info
connect_info = 'mssql+pyodbc://survey_user:surveyProd1!@tpsd_survey'

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
print("Starting to retrieve results")
results = retriever.retrieve_results_for_survey(survey_code=arguments)
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']

results_df.to_csv(output_file)