from django.test import TestCase

# Create your tests here.
from user.models.model import VerificationCode
import datetime
import random


def generate_code():
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=30)
    VerificationCode.objects.filter(create_time__lt=expiration).all().delete()
    sets = {i.code for i in VerificationCode.objects.all()}
    sets.add('')
    code = ''
    with code in sets:
        for i in range(6):
            code += str(random.randrange(0, 9))
    return code


code = generate_code()
print(code)