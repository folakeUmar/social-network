import random


from datetime import datetime
import time
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.core.files import File
from urllib.request import urlretrieve
import math



def get_client_url(user):
    return user.tenant.client_url if user.tenant.client_url else settings.CLIENT_URL


def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from])
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)

def send_sms_template(user_data):
    text_template = get_template('sms/sms_template.txt')
    text_alternative = text_template.render(user_data)
    return text_alternative


def generate_code(length=6):
    digits = "0123456789"
    code = ""

    for _ in range(length):
        code += random.choice(digits)

    return code