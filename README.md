## Set up SKEDD locally for acceptance testing

### install postgresSQL if not already installed
#### windows
    https://www.postgresql.org/download/windows/

#### osx
    https://www.postgresql.org/download/macosx/

#### ubuntu
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    sudo -u postgres createuser --interactive

### clone the repo and enter the diector
    https://github.com/CameronOC/SKEDD.git
    cd SKEDD

### set up virtual enviornment
    virtualenv flask
    . flask/bin/activate

### install python requirements
    pip install -r requirements.txt

### Set Environment Variables

#### osx/ubuntu
    export APP_MAIL_USERNAME="skedd.mail@gmail.com"
    export APP_MAIL_PASSWORD="cumulonimbus"
    export APP_SETTINGS="project.config.ProductionConfig"

#### windows
    setx APP_SETTINGS "project.config.ProductionConfig"
    setx APP_MAIL_USERNAME "skedd.mail@gmail.com"
    setx APP_MAIL_PASSWORD "cumulonimbus"

### Set up the database
    python manage.py create_db
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    
### run the server
    gunicorn manage:app

---------------------------------------------------------------

## How to set up the virtual dev environment

### after cloning and cding into the repo:

    virtualenv flask
    . flask/bin/activate
    pip install -r requirements.txt


Email server:

    export APP_MAIL_USERNAME="skedd.mail@gmail.com"
    export APP_MAIL_PASSWORD="cumulonimbus"

for development:

    export APP_SETTINGS="project.config.DevelopmentConfig"

for running tests:

    export APP_SETTINGS="project.config.TestingConfig"

for production:
		
    export APP_SETTINGS="project.config.ProductionConfig"
	
## For Windows

    setx APP_SETTINGS "project.config.DevelopmentConfig"
    setx APP_MAIL_USERNAME "skedd.mail@gmail.com"
    setx APP_MAIL_PASSWORD "cumulonimbus"

### Create DB

    python manage.py create_db
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py create_admin

### Run

    python manage.py runserver

## To run all tests
    cd SKEDD
    nosetests

## To run tests with coverage report
    nosetests --with-coverage --cover-package=project --cover-erase
