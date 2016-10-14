## How to set up the virtual dev environment

### after cloning and cding into the repo:

    virtualenv flask
    . flask/bin/activate
    pip install -r requirements.txt

## Set Environment Variables

    export APP_SETTINGS="source.config.DevelopmentConfig"
	
	If necessary:
	
	export APP_MAIL_USERNAME="skedd.mail@gmail.com"
	export APP_MAIL_PASSWORD="cumulonimbus"
	
## For Windows
		setx APP_SETTINGS "source.config.DevelopmentConfig"

### Create DB

    python manage.py create_db
    python manage.py db init
    python manage.py db migrate
    python manage.py create_admin

### Run

    python manage.py runserver
