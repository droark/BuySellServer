# BuySellServer

This is a Python program that implements a simple REST interface via HTTP and JSON. An HTTP request can be sent to add a buy (/buy) or sell (/sell) order for a particular commodity, with the ability to receive sorted lists for both order databases (/book). The buy DB will list entries in descending price order, with the sell DB entries listed in ascending price order. In addition, each entry into the DB is unique. Entries may be modified or deleted but adds will be atomic.

When a buy order is sent, the sell DB is searched for the order with the lowest sell price. If the sell price is lower than the buy price, an attempt is made to fill the buy order. If the entire sell order's quantity is consumed, the sell order is removed, and the buy order quantity is updated to reflect the new, lowered quantity. The entry with the next highest price in the sell DB is then processed, with the process continuing until either the buy order is completely filled or no more sell orders with an appropriate price exist. If only part of the sell order's quantity is consumed before the buy order is filled, the sell order is updated with the new quantity. At the end, if the buy order isn't completely filled, the order is added to the buy DB.

Processing new sell orders is basically the same, with the exception that the buy DB entries are sorted in descending order.

Note that, in addition, the aforementioned sort techniques, secondary sorting is applied by internal ID. In other words, if two or more entries have the same price, the entries will be listed starting with the lowest ID. The idea is that, when orders are filled, matching orders are handled in a first-come first-served manner.

**SOFTWARE REQUIREMENTS**:
Install the following packages in the following order but not before reading the installation instructions.

* [Python 2.7](https://www.python.org/)  (sudo apt-get install python-dev)
* [Apache2](https://httpd.apache.org/)  (sudo apt-get install apache2)
* [WSGI](https://code.google.com/archive/p/modwsgi/)  (sudo apt-get install libapache2-mod-wsgi)
* [SQLite](https://www.sqlite.org/)  (sudo apt-get install libsqlite3-0)
* [virtualenv](https://pypi.python.org/pypi/virtualenv)  (sudo apt-get install python-virtualenv)
* [json_reformat](https://lloyd.github.io/yajl/)  (sudo apt-get install yajl-tools)
* [Flask](http://flask.pocoo.org/)  (pip install Flask)  *venv*
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/)  (pip install flask-sqlalchemy)  *venv*
* [SQLAlchemy-migrate](https://pypi.python.org/pypi/sqlalchemy-migrate)  (pip install sqlalchemy-migrate)  *venv*

This code is tested only against Python 2.7; it may or may not run on Python 3.

Note that all the *pip install* steps have a "venv" marking next to them. This is because it's highly recommended that these Python packages be installed only in a virtual environment. See the installation steps for more information.

**INSTALLATION STEPS (Linux)**:
The following steps apply to Linux. Run all the following commands in the same window. Note that this code has not yet been tested under Windows or OS X. In addition, note that usage of *virtualenv* is optional but [highly recommended by Flask's maintainers](http://flask.pocoo.org/docs/0.10/installation/).

* Ensure that Python, Apache, WSGI, and virtualenv are installed.
  * Once WSGI is installed, the command *sudo a2enmod wsgi* may need to be run to ensure that the module is picked up. Run it to be safe. In Ubuntu, this should be sufficient to ensure that Apache will pick up the module and start allowing it to be used.
* Follow the Flask recommendation to [set up virtualenv](http://flask.pocoo.org/docs/0.10/installation/). Run the following commands in order from this project's base directory.
  * *virtualenv venv*
  * *. venv/bin/activate*
* Use *pip* to install the aforementioned Python packages in the virtual environment.
* Run *python db_create.py* to create the SQLite database.
* Run *python BuySellServer.py* to start the server.
* Once you're ready to quit the server, hit <CTRL+C> to quit.
* Execute *deactivate* to turn off the virtual environment created by *virtualenv*.
* If doing file cleanup once done with the server, executing *cleanup.sh* is the easiest thing to do.

By default the server runs at http://localhost:3000/ but can be deployed anywhere.

### Send JSON data to the server ###
[cURL](http://curl.haxx.se/) is used to send JSON data to the server via a POST request. The following are examples of how to send the data.

`curl localhost:3000/sell --data '{"qty":10,"prc":13}' -H "Content-Type: application/json"`
`curl localhost:3000/buy  --data '{"qty":10,"prc":7.4}' -H "Content-Type: application/json"`

Note that the quantity is an integer, and the price is a floating point value. Data must be sent via a POST method, in JSON format.

If the order is successfully added to the DB, no data will be returned. If there was a problem with adding the order, an error message will be returned.

### Read JSON data from the server ###
The server may be queried for the JSON data via a GET request. The following is an example of how to query the DB.

`curl localhost:3000/book | json_reformat`

# GENERAL NOTES #
Please note that this code isn't meant for a production environment, although the code has been kept clean and has been designed to simulate how production code might be deployed. As is, the code is simply a proof-of-concept designed to show the ability of Python to quickly and easily handle various tools in order to create useful programs, web pages, etc. Flask was chosen due to its simplicity and application in "microprojects" that require minimal server resources. In a production environment, a more robust web framework may be more desirable (e.g., Django), or possibly a framework written in a different language (e.g., Ruby on Rails). When considering a framework, many factors msut be considered, including but not limited to framework security, scalability, ability to interface with appropriate tools, and the compatibility of the framework with the overall design of the system. For example, if a [PostgreSQL/bcrypt combo](http://crafted-software.blogspot.com/2011/05/modern-way-to-store-passwords-bcrypt.html) is desired to support sensitive data, will the framework support PostgreSQL and bcrypt?

SQLite was chosen because it's a relatively simple DB that's portable and well-supported. It's also deployed in production environments where concurrency requirements aren't too critical. As such, SQLite is fine for a prototype but will develop issues as more users come online.

Apache 2.x was chosen because it's the default deployment on Ubuntu. Some might argue that nginx is a better choice these days. Whether or not nginx is better, this project is designed to be deployable with as little manual operation by the user as possible.

A script (db_migrate.py) has been included to accommodate cases where the DB view is changed. It shouldn't be needed but is included as a courtesy.
