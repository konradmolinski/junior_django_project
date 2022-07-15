Simple Django project for junior backend engineer position. Main features include image uploading/processing, pagination, generating expiring links.

Follow these instructions to set up the project:
1. In /junior_django_project run "pipenv shell".
2. Install requirements with "pip install -r requirements.txt".
3. Create migrations and apply them with "python manage.py makemigrations" followed by "python manage.py migrate".
4. Load fixtures with "python manage.py loaddata tier_fixtures.json".
5. Last step is to schedule the /junior_django_project/images/management/commands/deleteimage.py script to run repeatedly each couple seconds. The script
deletes binary images from the database upon their expiration date. Could be scheduled with e.g. Cronetab.

Now the project is set up and ready to run some tests with "python manage.py test".
