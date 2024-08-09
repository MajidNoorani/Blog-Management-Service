# Blog Service
This repo contains a fully featured blog management service. It Offers these features:
1. Admin panel for managing posts, users, comments, and contact Us messages
2. Information and statistics about posts, such as total number of views, rating, and total share counts
3. Integrated CKeditor to have rich text field for posts.
4. user friendly admin panel, designed by Jazzmin Django package
5. Google authentication
6. Email verification and forgot passowrd flow
7. Trigram to enable fuzzy search in PostgreSQL



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