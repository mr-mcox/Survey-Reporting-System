from sqlalchemy import create_engine
import pandas as pd
from CalculationCoordinator import CalculationCoordinator
from ConfigurationReader import ConfigurationReader
from ResultsRetriever import ResultsRetriever
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG)

config = ConfigurationReader.ConfigurationReader(config_file='small_demonstration_yaml.yaml')

# Read connection info
connect_info_file = open('db_connect_string.txt')
connect_info = connect_info_file.readline()
connect_info_file.close()

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
print("Starting to retrieve results")
results = retriever.retrieve_results_for_survey(survey_code=['1314MYS','1314F8W','1213EYS','1213MYS','1213F8W'])
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']
results_df = results_df.ix[results_df['question_code'].isin(['CSI1','CSI2','CSI3','CSI4','CSI5','CSI6','CSI7','CSI8','CSI10','CSI12','Culture1'])]
results_df.to_csv('hist_results.csv')
# results_df = pd.read_csv('results.csv')

# print("Starting calculations")
# calc = CalculationCoordinator.CalculationCoordinator(results=results_df,
# 													demographic_data=pd.read_excel('1314F8W_demographics.xlsx',sheetname="Sheet1"),
# 													config = config)
# calc.export_to_excel()