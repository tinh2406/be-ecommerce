from celery import shared_task


def test_crawl_config(**attrs):
    print("test_crawl_config", attrs)


@shared_task
def crawl_task(**attrs):
    test_crawl_config(**attrs)
    print("crawl_task", attrs)
    return attrs
