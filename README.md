# UW Python 210 SP Student Progress Tracking

A localhost Django app for tracking student progress and generating check in emails. The Student Tracking
spreadsheet should be downloaded from the course OneDrive account and converted to CSV format. The grade
report CSV can be generated and downloaded via the Data Download panel of the EdX learning platform.

## Getting Started

Make sure you are using a virtual environment of some sort (e.g. `virtualenv` or
`pyenv`).

Place an updated copy of the SQLite `dev.db` file in the project root directory.

```
pip install -r requirements.txt
./manage.py migrate
./manage.py loaddata sites
./manage.py runserver
```

Browse to http://localhost:8000/

Create superuser account to access student data in the Django admin:

```
./manage.py createsuperuser
```
