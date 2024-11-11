celery_worker:
	celery -A base.celery worker -l info

celery_beat:
	celery -A base.celery beat -l info

coverage_html:
	coverage run manage.py test -v 2  && coverage html

test_all:
	 python manage.py test

runserver:
	python manage.py runserver

createsuperuser:
	python manage.py createsuperuser

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

makemessages:
	python manage.py makemessages -l pl

compilemessages:
	python manage.py compilemessages