Welcome
=======
MacHammer is a deployment system geared specifically for Apple Service Providers.

Installation
============
Download the latest tarball
Install Django:
	
	$ sudo pip install django
	$ cd machammer
	$ ./manage.py syncdb
	$ ./manage.py runserver


Browsing Software Updates
=========================
Go to Settings and enter your SUS URL (e.g.: http://sus.example.com:8080/content/catalogs/index.sucatalog)
Hit save, click on Updates.
The first run takes a while to complete, but consecutive requests are read from the 24-hour cache.

![MacHammer Updates](http://unflyingobject.com/tmp/mh-updates.png)