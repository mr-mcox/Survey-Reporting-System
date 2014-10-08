from SurveyReportingSystem.db_migration.migrate import Migrator
from sqlalchemy import create_engine
import sys

engine = create_engine(sys.argv[1])
connection = engine.connect()

m = Migrator(engine,connection)
m.migrate_to_new_schema()