from SurveyReportingSystem.db_migration.migrate import migrate
import sys
from sqlalchemy import create_engine

connect_info_file = open(sys.argv[1])
connect_info = connect_info_file.readline().strip()
connect_info_file.close()
engine_1 = create_engine(connect_info)
conn_1 = engine_1.connect()

connect_info_file = open(sys.argv[2])
connect_info = connect_info_file.readline().strip()
connect_info_file.close()
engine_2 = create_engine(connect_info)
conn_2 = engine_2.connect()

survey_codes = sys.argv[3:]

migrate(conn_1,conn_2,survey_codes)