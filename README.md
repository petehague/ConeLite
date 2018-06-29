# ConeLite

This is a lightweight program for converting any table containing sky coordinates into a Conesearch service.

# Software Requirements

This program requires the following Python packages:

* Astropy
* SQLite
* Tornado

All of which can be installed with pip. Use of a virtual environment may make installation easier.

# Caveats

This program uses SQLite to enable the quick deployment of services. Whilst simple and compact, this kind of database has limitations which must be taken into account - https://www.sqlite.org/whentouse.html
