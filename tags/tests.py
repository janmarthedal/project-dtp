from django.test import TestCase
from tags.helpers import clean_tag

class CleanTagTest(TestCase):

    def test_one(self):
        self.assertEqual("abc de", clean_tag("abc  de "))
