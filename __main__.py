from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG)

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
# results = retriever.retrieve_results_for_one_survey(survey_code='1314F8W')
# results_df = pd.DataFrame(results['rows'])
# results_df.columns = results['column_headings']

# results_df.to_csv('results.csv')
results_df = pd.read_csv('results.csv')

print("Starting calculations")
calc = CalculationCoordinator.CalculationCoordinator(results=results_df,
													demographic_data=pd.read_excel('demographics.xlsx',sheetname="Sheet1"),
													config = config)
calc.export_to_excel()