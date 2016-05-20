Rotten Microbes
================

"Your sample is out there." (tm)
retrieve samples and sequences from laboratory chaos

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/graik/rotmic&env[TIME_ZONE]=US/Eastern&env[LANGUAGE_CODE]=us-en&env[DATE_FORMAT]=Y-m-d&env[DATETIME_FORMAT]=Y-m-d H:i)

Contents
---------------------

* [Features](#features)
* [Screen shots](#screenshots)
* [Production setup](#production)
* [Setup for development](#devsetup)

Features <a name="features"></a>
--------

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


Screen shots <a name="screenshots"></a>
------------

![Landing page](/screenshots/rotmic_home.png?raw=true)

![DNA sample](/screenshots/rotmic_dnasample.png?raw=true)

See "screenshots" folder for more.


Production setup <a name="production"></a>
-----------------

Within about five minutes, you can have your own rotmic server instance up and
running on the Amazon cloud. For the typical usage of a lab or small
institution, the resources offered for free, should be fully sufficient. There
are two steps involved: (1) Reserve storage space on the Amazon AWS where your
web server will save user-uploaded files -- this is referred to as an 'S3
bucket'. (2) Deploy your webserver using Heroku. Step by step instructions:

Before you start, choose a name for your new web server instance. The new 
server will soon be available as http://*"app-name"*.herokuapp.com

### 1. Set up cloud storage for user-uploaded files (attachments):

1. Go to https://console.aws.amazon.com/
   Create account if needed, verify account, sign in.
   
2. Menu: Services / S3
    1. Click "Create Bucket"
        * BTW, do _not_ use “Frankfurt” as a Region
        * assign name of your choice (*"bucket-name"* below)
3. Menu: Services / IAM (Identity and Access Management)
    1. Go to “Users” (left menu)
    2. Create User
        * choose user name (best: same as *"app-name"*)
        * keep “Generate Access Key for each User” checked
    3. Show or download User Credentials
        * copy Access Key ID and Secret Access Key to safe location (if lost, 
          user needs to be re-generated), these will need to be given to the 
          server as environment variables
    4. Click “Close"
    5. Click on new <app-name> user / go to “Permissions” Tab / “Attach Policy"
        * enter “S3” in search field
        * Activate “AmazonS3FullAccess"
        * Click “Attach Policy"


### 2. Set up Heroku web server instance:

* Click [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/graik/rotmic&env[TIME_ZONE]=US/Eastern&env[LANGUAGE_CODE]=us-en&env[DATE_FORMAT]=Y-m-d&env[DATETIME_FORMAT]=Y-m-d H:i)
    * choose a name for your web server (<app-name>)
    * choose the same region as the one you picked for the S3 storage above (US seems the saves bet)
* Fill in the three parameters for S3 cloud storage:
    * S3 bucket name — use the *"bucket-name"* you chose during “Create Bucket” in AWS
    * AWS_ACCESS_ID_KEY — the ID you noted in point 3.3 above
    * AWS_ACCESS_SECRET_KEY — the even longer secret key, AWS showed you in 3.3 above
    * you can adapt the other variables at any later point
* Click “Deploy"


### 3. Getting started with your new app:

* Go to your new app: *app-name*.herokuapp.com
    * Login: admin
    * Password: rotmic2016
    * Change password!!

Three users have been created automatically:

* admin — for adding users and changing permissions or all other kind of super powerful tasks
* test_labmember — a user with typical end-user permissions
* test_labmanager — can, in addition, create new storage racks and locations and can also create new categories for the classification of DNA, Protein or Chemicals

You should remove the latter two accounts or at least set them to "inactive"
once you have familiarized yourself with the permission and group management.

### Modify and update a running heroku app
   
   - You can use the heroku dashboard to update your app directly from the rotmic.git repo.

   - To make changes to your Rotmic server, clone the app project locally using the [Heroku Toolbelt](https://toolbelt.heroku.com/):

      ```sh
      heroku login
      heroku git:clone --app *app-name*
      ```
   - ... and then update the heroku app from your local computer:

      ```sh
      cd YOURAPPNAME
      git remote add origin https://github.com/graik/rotmic
      git pull origin master # may trigger a few merge conflicts, depending on how long since last update
      git push heroku master
      ```
   - This latter option has the advantage, that you can test changes locally. See section [Setup for development].


Setup for development <a name="devsetup"></a>
----------------------

Download / Checkout the rotmic project into a new folder, create a python
virtual environment and install all the required third-party dependencies:
```shell
    git clone https://github.com/graik/rotmic.git rotmicdjango
    cd rotmicdjango
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
```
You can later leave the virtual environment with the command `deactivate` and 
activate it again with the `source venv/bin/activate` script.

The next commands create tables for django housekeeping tasks (user and session management). Syncdb will not yet create tables for rotmic and third-party packages like reversion and guardian, which are all under south data migration control.
```shell
    cd rotmicdjango
    ./manage.py syncdb
        You just installed Django's auth system, which means you don't have any superusers defined.
        Would you like to create one now? (yes/no): no
```
It is important to NOT create a super user at this point. The rotmic data model introduces a "userprofile" table for saving user-specific settings. This table is "hard-linked" to the django.contrib.auth.User table and can only be created as long as this User table is still empty.
Now create rotmic data structures:

    ./manage.py migrate

Install initial user permission groups and three example users. This will
also create a super user "admin" with password rotmic2016:

    ./manage.py loaddata initial_usergroups.json

Now you are ready to run the development / debugging web server:

    ./manage.py runserver
        Validating models...
        
        0 errors found
        March 31, 2014 - 13:22:49
        Django version 1.6, using settings 'rotmicsite.settings'
        Starting development server at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.

Point your browser to http://127.0.0.1:8000 and start exploring the site. Login as
either `admin` (super user) or `test_user` (user with normal permissions) or
`test_manager` (user who can also create storage locations and categories).

The test server uses a SQLite database (created as `db.sqlite3`) and the built-in django debugging web server. File attachments will be saved in the `dev_uploads/` folder.
