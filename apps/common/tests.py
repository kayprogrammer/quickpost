from django.test import TestCase
from ninja.testing import TestAsyncClient
from apps.api import api

# Create your tests here.
aclient = TestAsyncClient(api, headers={"content_type": "application/json"})
