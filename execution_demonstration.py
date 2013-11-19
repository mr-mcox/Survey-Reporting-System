from sqlalchemy import create_engine
import sys, os
import pandas as pd
# if not os.path.abspath("/Users/mcox/Dropbox/MDIS/Code/SurveyReportingSystem") in sys.path : sys.path.insert(0, os.path.abspath("/Users/mcox/Dropbox/MDIS/Code/SurveyReportingSystem")) 
from CalculationCoordinator import CalculationCoordinator
from ResultsRetriever import ResultsRetriever
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG)

#Read connection info
connect_info_file = open('db_connect_string.txt')
connect_info = connect_info_file.readline()
connect_info_file.close()

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
print("Starting to retrieve results")
results = retriever.retrieve_results_for_one_survey(survey_code='1314F8W')
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']

print("Starting calculations")
calc = CalculationCoordinator.CalculationCoordinator(results=results_df,demographic_data=pd.read_excel('1314F8W_demographics.xlsx',sheetname="Sheet1"))
calc.compute_aggregation(cut_demographic='ethnicity',result_type='net')
calc.compute_aggregation(cut_demographic='region',result_type='net')
# logging.debug("Computations generated:\n" + str(calc.computations_generated))
calc.replace_dimensions_with_integers()
calc.create_row_column_headers()
calc.export_to_excel('1314F8W_demonstration.xlsx')