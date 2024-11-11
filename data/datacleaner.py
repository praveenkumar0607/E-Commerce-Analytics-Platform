import pandas as pd
import pymysql
from sqlalchemy import create_engine, text



class DataCleaner:
    def __init__(self, db_config):
        self.db_config = db_config
        self.df = None
        self.engine = self.create_db_engine()




    def create_db_engine(self):
        user = self.db_config.get('user')
        password = self.db_config.get('password')
        host = self.db_config.get('host')
        database = self.db_config.get('database')
        return create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')



    def list_tables(self):
        connecting_db = self.engine.connect()
        result = connecting_db.execute(text("SHOW TABLES;"))
        tables = result.fetchall()
        connecting_db.close()
        return [table[0] for table in tables]



    def list_columns(self, table_name):
        self.fetch_data(table_name)
        return self.df.columns.tolist()



    def fetch_data(self, table_name):
        self.df = pd.read_sql_table(table_name, self.engine)



    def remove_column(self, table_name, column_name):
        self.fetch_data(table_name)
        self.df.drop(column_name, inplace=True, axis=1)
        self.save_clean(table_name)



    def save_clean(self, table_name):
        self.df.to_sql(table_name, self.engine, if_exists='replace', index=False)




# Directly specify database configuration
db_config = {
    'user': 'root',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'nighwantech',
}


# Initialize DataCleaner instance
data_cleaner = DataCleaner(db_config)



# List all tables
tables = data_cleaner.list_tables()
print("Tables in the database:", tables)



# Use the first table from the list for demonstration
if tables:
    table_name = tables[1]
    print(f"Columns in table '{table_name}':", data_cleaner.list_columns(table_name))
else:
    print("No tables found in the database.")

