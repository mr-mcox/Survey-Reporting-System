from SurveyReportingSystem.db_migration.migrate import Migrator
from sqlalchemy import create_engine
import sys
import os
import logging

logging.basicConfig(filename='migration.log',level=logging.INFO)

connect_info_file = open(sys.argv[1])
connect_info = connect_info_file.readline().strip()
engine = create_engine(connect_info)
connection = engine.connect()
folder_for_maps = sys.argv[2]
surveys_to_migrate = sys.argv[3:]
# print("surveys_to_migrate are " + str(surveys_to_migrate))

question_category_csv = os.path.join(folder_for_maps,'question_category.csv')
assert os.path.exists(question_category_csv), "question_category.csv expected in folder " + folder_for_maps

survey_title_csv = os.path.join(folder_for_maps,'survey_title.csv')
assert os.path.exists(survey_title_csv), "survey_title.csv expected in folder " + folder_for_maps

cm_id_map_csv = os.path.join(folder_for_maps,'cm_id_map.csv')
assert os.path.exists(cm_id_map_csv), "cm_id_map.csv expected in folder " + folder_for_maps

legal_person_ids_csv = os.path.join(folder_for_maps,'legal_person_ids.csv')
assert os.path.exists(legal_person_ids_csv), "legal_person_ids.csv expected in folder " + folder_for_maps

m = Migrator(engine,
	connection,
	clean_CSI=True,
	clean_CALI=True,
	question_category_csv=question_category_csv,
	survey_title_csv=survey_title_csv,
	cm_id_map_csv=cm_id_map_csv,
	legal_person_ids_csv=legal_person_ids_csv,
	surveys_to_migrate=surveys_to_migrate
	)
m.migrate_to_new_schema()