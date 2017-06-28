# File upload API

This is a simple file uploading API written in python flask. It does the following basic operations

  - Upload a file
  - Download a file with a filename
  - Delete a file with a filename

##### Features

  - A file upload can be simple done as follows using curl.
 ```sh
 curl -i -X POST -F files=@test.mp3 http://hostname/upload
 ```
  - Downloading file.
 ```sh
 curl http://hostname/upload/test.mp3
```
 - Deleting a file.
```sh
 curl http://hostname/delete/test.mp3
```

This api also:
  - Reuse the contents to save space if multiple files have similar contents.
  - This convert unsafe filename characters to _



### Tech

This API uses the following techs:

* Python - The programming language used!
* Flask - The framework for python


### Installation

This code requires python 2.7 to run this. This expect mysql-server is configured and the credentials present on /root/.my.cnf unde the name [api]
eg:
```sh
[client]
user=root
password=strongpassword
[api]
user=api_user
password=superstrongpassword
```
The app will take care of checking/creating database and tables everytime it initiates.
##### Extra modules used:
- Flask
- MySQLdb


You may install these using pip
Once the installation is done. Run the app using following command.
```sh
python app.py
```
App runs on port 80 and thus it requires root.
