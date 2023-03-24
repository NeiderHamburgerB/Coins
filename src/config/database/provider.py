import mysql.connector
import os

def connection():
    try:
        host = os.environ['HOST']
        user = os.environ['USER']
        password = os.environ['PASSWORD']
        database = os.environ['DATABASE']

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection

    except mysql.connector.Error as error:
        print("Sorry an error occurred: {}".format(error))