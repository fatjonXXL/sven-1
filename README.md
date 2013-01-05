sven
====

Sven is a django project.

* * *

Installation
===

We tested SVEN on ubuntu systems with Python 2.7 and django 1.4.3, under apache2 server with wsgi module.
To install virtualenv and virtualenv wrapper from pip, follow the
[online documentation](http://virtualenvwrapper.readthedocs.org/en/latest/).

**Git!**
let's assume `/path/to/` as the parent path for sven installation

	$ cd /path/to/
	$ git clone https://github.com/densitydesign/sven.git

Make sure that `settings.py` file is located at `/path/to/sven/settings.py`

Create a sven dedicated virtualenv
---
Once virtualenvwrapper installed, create a virtualenv directory `sven.local`, activate the virtualenv and install the requirements:

	$ source /usr/local/bin/virtualenvwrapper.sh
	$ mkvirtualenv sven.local
	$ workon sven.local
	$ pip install -r requirements.txt

Configure virtualhost
---
You can use the `virtualhost.SAMPLE` file to enable sven site for apache server.
WSGIScriptAlias directive should point to `/path/to/sven/sven.wsgi`.

	$ sudo a2ensite sven
	$ sudo service apache2 reload

Sven site will be available under `http://sven.local` (your ServerName directive).

Configure wsgi
---
You can use the `sven.wsgi.SAMPLE` file: rename it to `sven.wsgi`.
Make the WSGIScriptAlias directive in your virtualhost point to this file.

Change `/path/to/` according to your virtualenv location, e.g.
	             site.addsitedir('/home/daniele/.virtualenvs/sven.local/lib/python2.7/site-packages')

Enable python logging
---
Create a log file for ANTA processes (sven scripts for Pattern library) and make it writable for the apache user.

	$ cd /path/to/sven
	$ mkdir logs
	$ touch logs/anta.log
	$ chown -hR you-user:www-data logs
	$ chmod 0775 -R logs

Configure settings.py file
---
You can use the settings.SAMPLE file and modify variables according to your configuration. Make sure that sven.anta and sven.core appear under installed apps.

	...
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3', 
	        'NAME': '/path/to/sven/sven.db',    
	...
	INSTALLED_APPS = (
    ...
    	# 'django.contrib.admindocs',
    	'sven.anta',
    	'sven.core'
	)
	...

Start your engines
---
Activate your virtualenv if it is not yet activated:

	$ source /usr/local/bin/virtualenvwrapper.sh
	$ workon sven.local
	$ cd /path/to/sven

Then:

	$ python manage.py syncdb

Cross your fingers and go to your sven url...


Create a Corpus
---
A **corpus** is a collection of documents. Standard fidf text analysis will be performed on the whole corpus.
