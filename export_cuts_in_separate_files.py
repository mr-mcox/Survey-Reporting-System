from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResponsesRetriever import ResponsesRetriever
import logging
import os

logging.basicConfig(filename='debug.log',level=logging.WARNING)

config = ConfigurationReader.ConfigurationReader(config_file='config.yaml')

# Read connection info
# connect_info_file = open('db_connect_string.txt')
# connect_info = connect_info_file.readline()
# connect_info_file.close()

# engine = create_engine(connect_info)

# conn = engine.connect()
# db = conn
# retriever = ResponsesRetriever.ResponsesRetriever(db_connection=db)
# print("Starting to retrieve responses")
# responses = retriever.retrieve_responses_for_survey(survey_code='1314F8W')
# responses_df = pd.DataFrame(responses['rows'])
# responses_df.columns = responses['column_headings']

# responses_df.to_csv('responses.csv')
responses_df = pd.read_csv('responses.csv')

for_historical = False
if os.path.exists('hist_demographics.xlsx') and os.path.exists('hist_responses.csv'):
	hist_responses_df = pd.read_csv('hist_responses.csv')
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