# Blog Service

## Installation

```
1. sudo apt update
2. sudo apt install apt-transport-https ca-certificates curl software-properties-common
3. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
4. sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
5. sudo apt update
6. sudo apt install docker-ce
7. sudo docker --version
8. sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
9. sudo chmod +x /usr/local/bin/docker-compose
10. sudo docker compose version
```
if you get the version of docker compose, everything is ok

## Clone the codes

```
1. git clone git@tiva-git.ir:tiva/blog-service.git
2. git checkout master
```

## Deploy
for run and deploy the code. first put a **.env** file in the directory like [.env.example](.env.example)

change the values of the fields within this file.

and then run these codes:

```
1. sudo docker compose build
2. sudo docker compose run --rm app sh -c "python manage.py makemigrations"
3. sudo docker compose run --rm app sh -c "python manage.py migrate"
```

Now we need to create a admin user for our app

```
4. sudo docker compose run --rm app sh -c "python manage.py createsuperuser"
```
answer to the questions that appear in the terminal

```
5. sudo docker compose up
```

## Enable trigram search:
For trigram search, the pg_term extention must be installed on postgres.

```
sudo docker compose run --rm app sh -c "python manage.py makemigrations --empty core"
```

in the created migration file edit it in this way:

```
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', <'name of the previous migration file'>),
    ]

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;"),
    ]
```