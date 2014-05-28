from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.ResultsRetriever import ResultsRetriever
import logging

logging.basicConfig(filename='debug.log',level=logging.WARNING)

# Read connection info
connect_info_file = open('db_connect_string.txt')
connect_info = connect_info_file.readline()
connect_info_file.close()

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
print("Starting to retrieve results")
results = retriever.retrieve_results_for_survey(survey_code='1314EYS')
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']

results_df.to_csv('results.csv')