import pandas as pd
from sqlalchemy import create_engine
import sys

connect_info_file = open(sys.argv[2])
connect_info = connect_info_file.readline().strip()
engine = create_engine(connect_info)
df = pd.read_csv(sys.argv[1])

df.to_sql('numerical_responses',engine,if_exists='append',index=False)