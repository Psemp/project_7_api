import os
from dotenv import load_dotenv

from psycopg2 import connect

load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

connection_string = f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"

conn = connect(connection_string)

# Use the connection to fetch data from the dashboard_estimator table


def get_table_objects(table: str):

    with conn.cursor() as cursor:
        query = "SELECT name, metrics, auc_conf_image, summary_image, identifier FROM api_estimator"
        cursor.execute(query, (table,))
        objects = cursor.fetchall()

    return objects
