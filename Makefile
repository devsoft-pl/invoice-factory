celery_worker:
	celery -A base.celery worker -l info

celery_beat:
	celery -A base.celery beat -l info

coverage_html:
	coverage run -m pytest && coverage html

test_all:
	 pytest .

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

postgres:
	docker compose up postgres -d

postgres-down:
	docker compose down postgres