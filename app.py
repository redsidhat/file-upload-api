from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sys
import MySQLdb
import os
import hashlib
app = Flask(__name__)

TEMP_UPLOAD_FOLDER = 'temp_uploads'
UPLOAD_FOLDER = 'uploads'

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

def check_directories():
    if not os.path.exists(TEMP_UPLOAD_FOLDER):
        os.makedirs(TEMP_UPLOAD_FOLDER)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def initiate():
    check_db_status()
    check_directories()
    app.run(
        host='0.0.0.0', 
        port=80, 
        debug=True
        )

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        #Incase if the file is too big
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def update_metadata(filename, checksum):
    temp_file_path = TEMP_UPLOAD_FOLDER+"/"+filename
    file_path = UPLOAD_FOLDER+"/"+filename
    #check if file name is duplicate.
    query = "SELECT COUNT(*) from files.files_metadata WHERE filename = '%s';" %filename
    connector = initiate_db_connection()
    response = db_execute(connector, query, True)
    for row in response:
        file_name_exist = row[0]
    if file_name_exist == 0:
        #file name doesn't exist in the db. 
        #checking if the md5sum exist
        query = "SELECT COUNT(*) from files.files_metadata WHERE checksum = '%s';" %checksum
        response = db_execute(connector, query, True)
        for row in response:
            checksum_exist = row[0]
        if checksum_exist == 0:
            #checksum doesn't exist
            #moving file from temp path to actualy path.
            try:
                os.rename(temp_file_path, file_path)
            except:
                print "file mving to uploads directory failed"
                return False
            query = 'INSERT INTO files.files_metadata (fileName, checksum, location) VALUES ("%s", "%s", "%s");' %(filename, checksum, file_path)
            response = db_execute(connector, query)
            close_db_connection(connector)
            return True
        else:
            #same file with different names.
            print "removing temp file and inserting entry to databse"
            os.remove(temp_file_path)
            query = "SELECT location from files.files_metadata WHERE checksum = '%s';" %checksum
            response = db_execute(connector, query, True)
            for row in response:
                file_path = row[0]
            query = 'INSERT INTO files.files_metadata (fileName, checksum, location) VALUES ("%s", "%s", "%s");' %(filename, checksum, file_path)
            response = db_execute(connector, query)
            close_db_connection(connector)
            return True
    else:
        print "filename already exist"
        #removing temporary file
        os.remove(temp_file_path)
        return False

def get_file_path(filename):
    file_path = None
    query = "SELECT location from files.files_metadata WHERE fileName = '%s';" %filename
    connector = initiate_db_connection()
    response = db_execute(connector, query, True)
    close_db_connection(connector)
    for row in response:
        file_path = row[0]
    if file_path == None:
        return False
    return file_path    

def delete_file(filename, file_path):
    #removing file from disk
    try:
        os.remove(file_path)
        #file removing from database
        query = "DELETE from files.files_metadata WHERE fileName = '%s';" %filename
        connector = initiate_db_connection()
        response = db_execute(connector, query)
        close_db_connection(connector)
        return True
    except:
        return False

@app.route('/')
def index():
    return "Your file upload solution!"


@app.route('/uploads', methods=['POST'])
def upload():
    file = request.files['files']
    # Make the filename safe, remove unsupported chars
    filename = secure_filename(file.filename)
    #writting the uploaded file
    try:
        file.save(os.path.join(TEMP_UPLOAD_FOLDER, filename))
    except file as err:
        return 'File upload failed %s' %str(err), 500


    temp_file_path = TEMP_UPLOAD_FOLDER+"/"+filename
    checksum = md5(temp_file_path)
    upload_status = update_metadata(filename, checksum)
    if upload_status:
        return 'Success', 200
    else:
        return 'Failed due to conflict in filename', 409

@app.route('/uploads/<path:filename>', methods=['GET'])
def download(filename):
    file_path = get_file_path(filename)
    if not file_path:
        return "File not found."
    print file_path
    return send_from_directory(directory='', filename=file_path)

@app.route('/delete/<path:filename>')
def delete(filename):
    file_path = get_file_path(filename)
    if not file_path:
        return "File not found."
    if delete_file(filename, file_path):
        return "File Deleted successfully"
    else:
        return "File Delete failed", 500


if __name__ == '__main__':
    initiate()
