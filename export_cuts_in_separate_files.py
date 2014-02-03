from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
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
# retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
# print("Starting to retrieve results")
# results = retriever.retrieve_results_for_survey(survey_code='1314F8W')
# results_df = pd.DataFrame(results['rows'])
# results_df.columns = results['column_headings']

# results_df.to_csv('results.csv')
results_df = pd.read_csv('results.csv')

for_historical = False
if os.path.exists('hist_demographics.xlsx') and os.path.exists('hist_results.csv'):
	hist_results_df = pd.read_csv('hist_results.csv')
	print("Starting calculations with historical data")
	for_historical = True
	calc = CalculationCoordinator.CalculationCoordinator(results=results_df,
														demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
														hist_results=hist_results_df,
														hist_demographic_data=pd.read_excel('hist_demographics.xlsx',sheetname="Sheet1"),
														config = config)
else:
	print("Starting calculations")
	calc = CalculationCoordinator.CalculationCoordinator(results=results_df,
														demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
														config = config)
calc.export_cuts_to_files(for_historical=for_historical)