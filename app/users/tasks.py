from celery import shared_task
from django.conf import settings
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from .utils import send_email
from .models import User
from core.celery import APP


@APP.task()
def user_code_email(email_data):
    html_template = get_template('emails/user_code_email.html')
    text_template = get_template('emails/user_code_email.txt')
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email('User Registration',
               email_data['email'], html_alternative, text_alternative)
