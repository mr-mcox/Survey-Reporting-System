from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging
import os
import csv
import pdb

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
print("Starting calculations")
calc = CalculationCoordinator.CalculationCoordinator(results=results_df,
													demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
													config = config)
#Read pilot data
pilot_cms_rows = []
with open('pilot_cms.csv') as f:
	reader = csv.reader(f)
	for row in reader:
		pilot_cms_rows.append([item for item in row])
calc.add_pilot_cms(pilot_cms_rows)
calc.config.add_pilot_cuts(pilot_cms_rows)
calc.export_to_excel()