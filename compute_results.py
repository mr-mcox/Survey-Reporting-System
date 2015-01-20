from sqlalchemy import create_engine
import pandas as pd
from SurveyReportingSystem.CalculationCoordinator import CalculationCoordinator
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader
from SurveyReportingSystem.ResponsesRetriever import ResponsesRetriever
import logging
import os
# import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("surveys", type=str,
                    help="list of survey codes to use",
                    nargs='*')
parser.add_argument("-c", "--config", type=str,
                    help="the config file to use")
args = parser.parse_args()

logging.basicConfig(filename='debug.log', level=logging.WARNING)

config_file = 'config.yaml'
if args.config is not None:
    print("Using config file " + args.config)
    config_file = args.config

config = ConfigurationReader.ConfigurationReader(config_file=config_file)

connect_info = 'mssql+pyodbc://survey_user:surveyProd1!@tpsd_survey'

engine = create_engine(connect_info)

conn = engine.connect()
db = conn
retriever = ResponsesRetriever.ResponsesRetriever(db_connection=db)
print("Starting to retrieve current responses")
responses = retriever.retrieve_responses_for_survey(
    survey_code=args.surveys[0])
responses_df = pd.DataFrame(responses['rows'])
responses_df.columns = responses['column_headings']

if len(args.surveys) > 2:
    assert os.path.exists(
        'hist_demographics.xlsx'), "hist_demographics.xlsx expected in current folder"

    print("Starting to retrieve historical responses")
    hist_responses = retriever.retrieve_responses_for_survey(
        survey_code=args.surveys)
    hist_responses_df = pd.DataFrame(hist_responses['rows'])
    hist_responses_df.columns = hist_responses['column_headings']

    print("Starting calculations with historical data")
    calc = CalculationCoordinator.CalculationCoordinator(responses=responses_df,
                                                         demographic_data=pd.read_excel(
                                                             'demographics.xlsx', sheetname="Sheet1"),
                                                         hist_responses=hist_responses_df,
                                                         hist_demographic_data=pd.read_excel(
                                                             'hist_demographics.xlsx', sheetname="Sheet1"),
                                                         config=config)
else:
    print("Starting calculations")
    calc = CalculationCoordinator.CalculationCoordinator(responses=responses_df,
                                                         demographic_data=pd.read_excel(
                                                             'demographics.xlsx', sheetname="Sheet1"),
                                                         config=config)
calc.export_to_excel()
