Rotten Microbes
================

"Your sample is out there." (tm)
retrieve samples and sequences from laboratory chaos


Setting up a test server
------------------------

Out of the box, the project is configured for quick set up of a development server, which should only be used for testing purposes. The test server uses a SQLite database (created as rotmicdev.db) and the built-in django debugging web server. File attachments will be saved in the dev_uploads/ folder.

___Dependencies___

 * python 2.7
 * Django 1.6
 * Biopython

Rotmic relies on additional third-party django apps and python modules. For convenience, these apps are cloned in the thirdparty/ folder. This folder will be automagically included in the Python path when you load rotmic:

 * guardian -- object-level permissions (not implemented in the user interface)
 * reversion -- versioning (view and revert changes to data records)
 * selectable -- javascript elements for dynamic lookup of related records in forms
 * xlrd -- Excel table import
 * pytz -- time zone management
 * south -- data base migration management (will become part of standard django from version 1.7)
 * markdown -- text formatting (headlines, links, etc.) for description fields

As these packages are included in the project source, they do not need to be installed separately. This minimizes the risk of version conflicts but also means that rotmic may not always be using the latest available version of those packages.

___Rotmic setup___

Download / Checkout the rotmic project into a new folder:

<code>
git clone https://github.com/graik/rotmic.git rotmicdjango
</code>
This will create a new folder rotmicdjango in your current directory. The next commands will create a SQLite database, and create tables for django housekeeping tasks (user and session management). Syncdb will not yet create tables for rotmic and third-party packages like reversion and guardian, which are all under south data migration control.
{{{
cd rotmicdjango
./manage.py syncdb
  You just installed Django's auth system, which means you don't have any superusers defined.
  Would you like to create one now? (yes/no): no
}}}
It is important to NOT create a super user at this point. The rotmic data model introduces a "userprofile" table for saving user-specific settings. This table is "hard-linked" to the django.contrib.auth.User table and can only be created as long as this User table is still empty.

We use the django migration system to create rotmic, reversion, and guardian data structures:
{{{
./manage.py migrate
}}}

You can now create a super user for site administration -- please give it the username 'admin'.
{{{
./manage.py createsuperuser
  Username (leave blank to use 'raik'): admin
}}}

If you want to start from an empty database, you can fire up the rotmic server now. 
However, if you want to load some small example data set, do it now, '''before''' running the server for the first time:
{{{
./manage.py loaddata rotmic/fixtures/users_test.json
  Installed 123 object(s) from 1 fixture(s)
./manage.py loaddata rotmic/fixtures/rotmic_test.json
  Installed 154 object(s) from 1 fixture(s)
}}}

This will create:
 * three users (a "normal" user raik, an anonymous user without any permissions, and a superuser admin)
 * table access permissions for these users
 * default categories for DNA, proteins, Oligos, Cells and Chemicals
 * Units for volume, mass and amounts
 * a couple of DNA data sheets (markers, vectors, two plasmids) and DNA and cell samples

Note: Some units and default categories are "hard-coded" into the rotmic software (initialTypes.py, initialUnits.py, initialComponents.py). If missing, they will be created automatically during rotmic startup. That's why, it is important to load json data sets '''before''' firing up the server for the first time. Otherwise, primary keys for those entries in the json files may conflict with the primary keys of the newly created entries.

Now you are ready to run the development / debugging web server:
{{{
./manage.py runserver
  Validating models...

  0 errors found
  March 31, 2014 - 13:22:49
  Django version 1.6, using settings 'rotmicsite.settings'
  Starting development server at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.
}}}
Point your browser to http://127.0.0.1:8000 and start exploring the site.

Note: While you can get quite far with emacs and vi, for development and debugging, I highly recommend a professional Python development IDE. I have made good experiences with WingIDE.
