'''
The Celery app we created in the project root
will collect all tasks defined across all
Django apps listed in the INSTALLED_APPS
'''

import string

from celery import shared_task
from django.utils.crypto import get_random_string

from .models import User


@shared_task
def create_random_user_accounts(total):
    for i in range(total):
        print('i is : {}'.format(i))
    return
    #     username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
    #     email = '{}@example.com'.format(username)
    #     password = get_random_string(50)
    #     User.objects.create_user(username=username, email=email, password=password)
    # return '{} random users created with success!'.format(total)
