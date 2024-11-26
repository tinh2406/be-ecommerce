# base_django

Monitor Celery tasks with Flower
```bash
celery -A core flower
```

Run Celery worker
```bash
celery -A core worker
```

Run Celery beat for periodic tasks
```bash
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Generate migrations
```bash
python manage makemigrations
python manage migrate
```
