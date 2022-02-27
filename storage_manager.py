import sqlite3
from os.path import exists
from dataclasses import dataclass
import csv
import pandas as pd
import time


def create_db():                # Create the intial database, only called if db does not exist
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    create_table = 'CREATE TABLE members (Last_Name text, First_Name text, email text, role text)'
    cursor.execute(create_table)
    connection.commit()
    connection.close()


def db_stats():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    mentee_query = 'SELECT * FROM members WHERE role=?'
    mentor_query = 'SELECT * FROM members WHERE role=?'

    cursor.execute(mentee_query, ('Mentee',))
    mentee_count = len(cursor.fetchall())

    cursor.execute(mentor_query, ('Mentor',))
    mentor_count = len(cursor.fetchall())

    connection.close()

    return (mentee_count, mentor_count)


def search_db(search_query):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    print(search_query)
    query = 'SELECT * FROM members WHERE First_Name=? OR Last_Name=?'
    cursor.execute(query, (search_query,search_query))
    results = cursor.fetchall()
    connection.close()

    return results

def add_member_to_db(first_name, last_name, email, role):
    """

    """
    member = (first_name, last_name, email, role)
    insert_query = 'INSERT INTO members VALUES(?, ?, ?, ?)'

    db = sqlite3.connect('data.db')
    cursor = db.cursor()
    cursor.execute(insert_query, member)

    db.commit()
    db.close()

    timestamp_db()

def convert_db_to_csv():
    """
    Converts the sqlite db to human preferred formats.

    This method is somewhat expensive and to avoid unnecessary conversions we check and see if our database has
    any updates since the last conversion. If it hasn't then we do not perform the conversion. In db.txt the first line
    represents the last time the db was updated and the second line represents the last time a conversion was made.
    If the first line (time.time() format) > second line (time.time() format) then we need to update.
    """
    timestamp = time.time()


    with open('input/db.txt', 'r+') as txt_file:
        counter = 0
        lines = txt_file.readlines()

        last_db_change = lines[0]
        last_conversion = lines[1]

        print(f"Last change to the database happened on {last_db_change}")
        print(f"Last conversion happened on {last_conversion}")

    if last_db_change > last_conversion:        # DB has been updated since our last conversion
        conn = sqlite3.connect('data.db', isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
        db_df = pd.read_sql_query('SELECT * FROM members', conn)
        db_df.to_csv('output.csv', index=False)

        print('Updating the current csv copy')
        with open('input/db.txt', 'r+') as txt_file:       # Make note that we have an up to date conversion
            for line in lines:
                txt_file.write(str(timestamp) + '\n')
    else:
        print("Not updating the current csv copy. Current copy is most up to date.")


def timestamp_db():
    timestamp = time.time()
    with open('input/db.txt', 'r') as txt_file:
        lines = txt_file.readlines()
    
    with open('input/db.txt', 'w') as txt_file:
        for i, line in enumerate(lines):
            if i == 0:
                txt_file.writelines(str(timestamp) + '\n')
            else:
                txt_file.writelines(line)


def check_latest_entry():       # Checks latest change made to database, creates txt file if does not exist
    if exists('latest_db_change.txt'):
        file = open('latest_db_change.txt', 'r')
        file.readline()
    else:
        pass

if not exists('data.db'):
    create_db()

# convert_db_to_csv()