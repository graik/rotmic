Rotten Microbes
================

"Your sample is out there." (tm)
retrieve samples and sequences from laboratory chaos

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?env[TIME_ZONE]="US/Eastern")

__Features__

 * keep track of DNA constructs, cell stocks, primers, proteins and
   chemicals (such as fine chemicals or antibodies)

 * categorize and search them

 * add descriptions and file attachments to constructs and samples

 * crosslinks between, for example, cell constructs, the plasmids
   contained in them and the vector backbones shared between
   constructs

 * track sample pedigrees, for example, that a cell stock was derived
   by transformation from a certain DNA sample

 * convenient Excel import (/export) for all types of samples and constructs

 * versioning: all changes to all entries are tracked and can be
   reverted.

 * quick commenting and rating (fresh / rotten) for constructs and
   samples


__Screen shots__

![Landing page](/screenshots/rotmic_home.png?raw=true)

![DNA sample](/screenshots/rotmic_dnasample.png?raw=true)

See "screenshots" folder for more.

__Setting up a test server__

Out of the box, the project is configured for quick set up of a development server, which should only be used for testing purposes. The test server uses a SQLite database (created as rotmicdev.db) and the built-in django debugging web server. File attachments will be saved in the dev_uploads/ folder.

___Dependencies___

 * python 2.7
 * Django 1.6
 * Biopython
 * pysqlite (for development)

Rotmic relies on additional third-party django apps and python modules. For convenience, these apps are cloned in the thirdparty/ folder. This folder will be automagically included in the Python path when you load rotmic:

 * reversion -- versioning (view and revert changes to data records)
 * selectable -- javascript elements for dynamic lookup of related records in forms
 * xlrd -- Excel table import
 * pytz -- time zone management
 * south -- data base migration management (will become part of standard django from version 1.7)
 * markdown -- text formatting (headlines, links, etc.) for description fields

As these packages are included in the project source, they do not need to be installed separately. This minimizes the risk of version conflicts but also means that rotmic may not always be using the latest available version of those packages.

___Rotmic setup___

Download / Checkout the rotmic project into a new folder:


    git clone https://github.com/graik/rotmic.git rotmicdjango


This will create a new folder rotmicdjango in your current directory. The next commands will create a SQLite database, and create tables for django housekeeping tasks (user and session management). Syncdb will not yet create tables for rotmic and third-party packages like reversion and guardian, which are all under south data migration control.

    cd rotmicdjango
    ./manage.py syncdb
        You just installed Django's auth system, which means you don't have any superusers defined.
        Would you like to create one now? (yes/no): no

It is important to NOT create a super user at this point. The rotmic data model introduces a "userprofile" table for saving user-specific settings. This table is "hard-linked" to the django.contrib.auth.User table and can only be created as long as this User table is still empty.

We use the django migration system to create rotmic and reversion data structures:

    ./manage.py migrate

You can now create a super user for site administration -- please give it the username 'admin'.

    ./manage.py createsuperuser
        Username (leave blank to use 'raik'): admin

If you want to start from an empty database, you can fire up the rotmic server now. 
However, if you want to load some small example data set, do it now, **before** running the server for the first time:

    ./manage.py loaddata rotmic/fixtures/users_test.json
        Installed 123 object(s) from 1 fixture(s)
    ./manage.py loaddata rotmic/fixtures/rotmic_test.json
        Installed 154 object(s) from 1 fixture(s)

This will create:
 * three users (a "normal" user raik, an anonymous user without any permissions, and a superuser admin)
 * table access permissions for these users
 * default categories for DNA, proteins, Oligos, Cells and Chemicals
 * Units for volume, mass and amounts
 * a couple of DNA data sheets (markers, vectors, two plasmids) and DNA and cell samples

Note: Some units and default categories are "hard-coded" into the rotmic software (initialTypes.py, initialUnits.py, initialComponents.py). If missing, they will be created automatically during rotmic startup. That's why, it is important to load json data sets '''before''' firing up the server for the first time. Otherwise, primary keys for those entries in the json files may conflict with the primary keys of the newly created entries.

Now you are ready to run the development / debugging web server:

    ./manage.py runserver
        Validating models...
        
        0 errors found
        March 31, 2014 - 13:22:49
        Django version 1.6, using settings 'rotmicsite.settings'
        Starting development server at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.

Point your browser to http://127.0.0.1:8000 and start exploring the site.

Note: While you can get quite far with emacs and vi, for development and debugging, I highly recommend a professional Python development IDE. I have made good experiences with WingIDE.

__Production server setup__

... is better documented by the Django developers. Some notes:

At this point, I recommend cloning directly from github (as described above) so that 
it will be easy to update the server source code. Updating then consists of three easy commands:

    git pull
    ./manage.py collectstatic
    ./manage.py migrate
    sudo /etc/init.d/apache2 restart

The 'collectstatic' command will update the folder from which static file content is served 
(javascript, icons, css) by synchronizing it with rotmic/static. 'migrate' will perform
south database migrations (only if the git pull command has created any additional migration
files in rotmic/migrations/).

`/rotmicsite/settings.py` is checked in as a symbolic link to `settings_dev.py`.
Make a copy of `settings_dev.py`, adapt it to production needs, save it under a different name,
e.g., `settings_prod.py` and then point `settings.py -> settings_prod.py`.

**Important:** Re-generate the private SSH key -- the one in `settings_dev.py` is public on github!!

Other things you will want to change are the database engine used (we are using postgresql). 
`rotmicsite/` also contains django's default` wsgi.py` configuration module for using wsgi / apache. 

If you are using apache, you have to adapt the setting for the `$LANG` environment variable in 
`/etc/apache2/envvars`. Change `LANG=C` to `LANG="en_US.UTF-8"` or another unicode-compatible encoding. 
Otherwise, you will likely run into UniCode encoding errors as soon a user tries to upload a file 
with non-ascii characters in its file name.
