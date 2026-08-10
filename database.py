import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():

    connection = psycopg2.connect(
        host="localhost",
        database="project_ELN_db",
        user="postgres",
        password="postgres"
    )

    return connection

def get_dict_cursor(connection):

    return connection.cursor(cursor_factory=RealDictCursor)