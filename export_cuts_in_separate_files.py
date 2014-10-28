from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResponsesRetriever import ResponsesRetriever
import logging
import os
import sys

logging.basicConfig(filename='debug.log',level=logging.WARNING)

config = ConfigurationReader.ConfigurationReader(config_file='config.yaml')

connect_info = 'mssql+pyodbc://survey_user:surveyProd1!@tpsd_survey'

engine = create_engine(connect_info)
conn = engine.connect()
db = conn
retriever = ResponsesRetriever.ResponsesRetriever(db_connection=db)
print("Starting to retrieve current results")
results = retriever.retrieve_results_for_survey(survey_code=sys.argv[1])
responses_df = pd.DataFrame(results['rows'])
responses_df.columns = results['column_headings']

for_historical = False
if len(sys.argv) > 2:
	assert os.path.exists('hist_demographics.xlsx'), "hist_demographics.xlsx expected in current folder"

	print("Starting to retrieve historical results")
	hist_responses = retriever.retrieve_results_for_survey(survey_code=sys.argv[1:])
	hist_responses_df = pd.DataFrame(hist_responses['rows'])
	hist_responses_df.columns = hist_responses['column_headings']

	print("Starting calculations with historical data")
	for_historical = True
	calc = CalculationCoordinator.CalculationCoordinator(responses=responses_df,
														demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
														hist_responses=hist_responses_df,
														hist_demographic_data=pd.read_excel('hist_demographics.xlsx',sheetname="Sheet1"),
														config = config)
else:
	print("Starting calculations")
	calc = CalculationCoordinator.CalculationCoordinator(responses=responses_df,
														demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
														config = config)
calc.export_cuts_to_files(for_historical=for_historical)