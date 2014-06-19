from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging
import os
import sys

logging.basicConfig(filename='debug.log',level=logging.WARNING)

config = ConfigurationReader.ConfigurationReader(config_file='config.yaml')

connect_info = 'mssql+pyodbc://survey_user:Survey!1@tpsd_survey'

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
print("Starting to retrieve current results")
results = retriever.retrieve_results_for_survey(survey_code=sys.argv[1])
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']

if len(sys.argv) > 2:
	assert os.path.exists('hist_demographics.xlsx'), "hist_demographics.xlsx expected in current folder"

	print("Starting to retrieve historical results")
	hist_results = retriever.retrieve_results_for_survey(survey_code=sys.argv[1:])
	hist_results_df = pd.DataFrame(hist_results['rows'])
	hist_results_df.columns = hist_results['column_headings']

	print("Starting calculations with historical data")
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
calc.export_to_excel()