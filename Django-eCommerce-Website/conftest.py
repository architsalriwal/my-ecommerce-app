# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\conftest.py

import pytest
from django.conf import settings

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Automatically grant database access to all tests."""
    pass

@pytest.fixture(scope='session', autouse=True)
def celery_eager():
    """
    Forces all Celery .delay() tasks to run synchronously in the same thread.
    This allows us to test async background workers without needing Redis in CI/CD.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_STORE_EAGER_RESULT = True