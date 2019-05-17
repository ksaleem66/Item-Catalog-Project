Introduction
------------
The purpose of this project is to develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.

Project Display Example :

1. The homepage displays all current categories with the latest added items.
2. Selecting a specific category shows all the items available for that category.
3. Selecting a specific item shows specific information about that item.
4. After logging in, a user has the ability to add, update, or delete item information that he created himself.

Requirements
------------
1. Linux-based virtual machine (VM) which requires the installation of Oracle VirtualBox (https://www.virtualbox.org) and Vagrant (https://www.vagrantup.com).
2. Python ver 3.6.7 (an interpreter for the python language, download from https://www.python.org/) need to be installed on VM to run the module file. 
3. Installation of Flask and sqlalchemy on python.


Package Files
-------------
The following files are included for this project :

1. application.py	% python program file to run the web server
2. database_setup.py	% python file to create database structure
3. populate_data.py	% python file to populate sample data in the created database
4. README.md		% this file


Installation
------------
The package files need to be downloaded under the same folder on local machine where VM is installed, e.g. a folder with a name of "catalog" under vagrant folder (VM) can be created and the package files to be copied under this folder.


Configuration
-------------
Make sure once Python ver. 3.6.7 is downloaded that the path of Python folder is updated under system environment.


Database creation
-----------------
Before running the web server, sqlite database need to be created and populated with sample data by following below 2 steps :

1. From VM shell command line type >>python3 database_setup.py and hit enter to run the file and create DB structure.
2. From VM shell command line type >>python3 populate_data.py and hit enter to run the file and populate sample data.


How to run ?
-----------------
The Item Catalog (application.py) python program file can be run from linux like virtual machine as per below steps :

1. From VM shell command line type >>python3 application.py and hit enter to run the web server.
2. From web browser address bar you can access the application thru the URL http://localhost:5000


Troubleshooting
---------------------
If the file doesn't run make sure proper installation of :

1. Python ver. 3.6.7
2. Flask python web framework
3. SQLAlchemy python database tool

Maintainers
---------------
This package is developed and maintained by Khalid M Saleem on Mar 29th 2019.

