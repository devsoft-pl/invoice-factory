celery_worker:
	celery -A base.celery worker -l info

celery_beat:
	celery -A base.celery beat -l info

coverage_html:
	coverage run manage.py test -v 2  && coverage html

test_all:
	 python manage.py test

migrate:
	python manage.py migrate

makemigrations:
	python manage.py migrations

runserver:
	python manage.py runserver