import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_database_params():
    # Database connection parameters
    database_name = os.getenv("DATABASE_NAME")
    database_host = os.getenv("DATABASE_URL")
    database_user = os.getenv("DATABASE_USER")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_port = os.getenv("DATABASE_PORT", '5432')
    
    db_params = {
        'dbname': database_name,
        'user': database_user,
        'password': database_password,
        'host': database_host,
        'port': database_port
    }
    return db_params

def connect():
    # Establish a connection to the database
    db_params = get_database_params()
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    return conn, cur

def truncate(cur):
    # Truncate the table before insertion
    cur.execute("TRUNCATE TABLE poems")
    print("Table truncated successfully.")

def process_date(datetime_value):
    if pd.isna(datetime_value) or datetime_value == '':
        return None
    try:
        return pd.to_datetime(datetime_value).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def upload(poems):
    conn, cur = connect()
    truncate(cur)

    # Prepare data for insertion
    data_to_insert = poems.apply(lambda row: (
        row['id'],
        process_date(row['date']),
        row['title'],
        row['text'],
        row['topic1'] if not pd.isna(row['topic1']) else None,
        row['topic2'] if not pd.isna(row['topic2']) else None,
        row['topic3'] if not pd.isna(row['topic3']) else None,
        row['embedding']
    ), axis=1).tolist()

    # SQL for inserting data
    insert_sql = """
    INSERT INTO poems (id, date, title, text, topic1, topic2, topic3, embedding)
    VALUES %s
    """

    # Execute the insert
    execute_values(cur, insert_sql, data_to_insert)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

    print("Data insertion complete.")