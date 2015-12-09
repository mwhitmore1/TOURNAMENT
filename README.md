REQUIRMENTS

This application requires Python 2 to be installed on your computer (available at https://www.python.org/downloads/).  In addition, the following two python modules must also be downloaded: bleach and psycopg2.  You will also need to install PostgreSQL (available at http://www.postgresql.org/download/).  

SETTING UP THE DATABASE

Once you have all the necessary software installed, open the command line, type 'psql,' and press enter to open PostgreSQL.  Next, type '\i tournament.sql' and press enter.  This command will import the tournament database, its tables, and its views into PostgreSQL.  It may take a few seconds for the tournament database to import.  

Once the tournament database and its contents have been imported, type '\q' and press enter.  This will cause you to exit out of PostgreSQL and return you to the command line.  

USE

Once the tournament database has been imported into PostgreSQL, the functions in the tournament.py module can be used in a Python file or on the Python command line to modify the tournament database.  In order to use these functions, you must first import the tournament.py file. The comments in the tournament.py file contain information as to the use of each function.     