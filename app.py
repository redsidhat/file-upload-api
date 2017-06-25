from flask import Flask
import sys
import MySQLdb
app = Flask(__name__)


def initiate_db_connection():
    try:
        cnx = MySQLdb.connect(read_default_group='api')
        print "MySQL connection succeeded.\n"
        return cnx
    except MySQLdb.Error as err:
        print "MySQL connection error %s" %str(err)

def close_db_connection(cnx):
    try:
        cnx.close()
        print "Database connection closed successfully.\n"
    except MySQLdb.Error as err:
        print "Error closing db connection %s" %str(err)
        sys.exit(1)

def db_execute(cnx,sql,select=False):
    try:
        cursor = cnx.cursor()
        cursor.execute(sql)
        if select:
            response = cursor.fetchall()
            print "Select query executed successfully.\n"
            return response
        else:
            cnx.commit()
            print "Update or Insert query executed successfully.\n"

    except MySQLdb.Error as err:
        print "Error executing query %s" %str(err)
        sys.exit(1)

def check_db_status():
    print("db check")
    connector = initiate_db_connection()
    #Checking if table and db doens't exist and creating them if doesn't exist
    db_name = 'files'
    db_table = 'files_metadata'

    print "Creating databse if not existing."
    query = 'CREATE DATABASE IF NOT EXISTS %s' %db_name
    db_execute(connector,query)

    print "Creating table if not existing."
    query = 'CREATE TABLE IF NOT EXISTS %s.%s (fileName varchar(255) NOT NULL, checksum varchar(32) NOT NULL, location varchar(255) NOT NULL, PRIMARY KEY (fileName) );' %(db_name, db_table)
    db_execute(connector,query)
    #Closing mysql connection
    close_db_connection(connector)

def initiate():
    check_db_status()
    app.run(host='0.0.0.0', port=80, debug=True)

@app.route('/')
def index():
    return "Your file upload solution!"

if __name__ == '__main__':
    initiate()
