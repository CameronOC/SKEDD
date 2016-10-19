## How to set up the virtual dev environment

### after cloning and cding into the repo:

    virtualenv flask
    . flask/bin/activate
    pip install -r requirements.txt

## Set Environment Variables

Email server:

    export APP_MAIL_USERNAME="skedd.mail@gmail.com"
	export APP_MAIL_PASSWORD="cumulonimbus"

for development:

    export APP_SETTINGS="project.config.DevelopmentConfig"

for running tests:

    export APP_SETTINGS="project.config.TestingConfig"
	
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
