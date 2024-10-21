# base_django

celery -A core worker \
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

python manage makemigrations

python manage migrate
