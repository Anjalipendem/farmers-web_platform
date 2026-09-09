import mysql.connector


def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="anju@anjali",
        database="farmer_empowerment"
    )

    return connection