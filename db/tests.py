"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_design_entries(self):
        from models import *
        db = DB.objects()[0]
        db.design_mode()
        print db.design_entries()

