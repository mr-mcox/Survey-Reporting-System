from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging
import os
import csv
import pdb
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