from sqlalchemy import create_engine
import sys, os
import pandas as pd
# if not os.path.abspath("/Users/mcox/Dropbox/MDIS/Code/SurveyReportingSystem") in sys.path : sys.path.insert(0, os.path.abspath("/Users/mcox/Dropbox/MDIS/Code/SurveyReportingSystem")) 
from NumericOutputCalculator import NumericOutputCalculator
from ResultsRetriever import ResultsRetriever

#Read connection info
connect_info_file = open('db_connect_string.txt')
connect_info = connect_info_file.readline()
connect_info_file.close()

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResultsRetriever.ResultsRetriever(db_connection=db)
results = retriever.retrieve_results_for_one_survey(survey_id=0)
results_df = pd.DataFrame(results['rows'])
results_df.columns = results['column_headings']


calc = NumericOutputCalculator.NumericOutputCalculator(raw_values=results_df)
print("Net results are " + str(calc.compute_net_results()))