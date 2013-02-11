from django.test import TestCase
from items.models import final_id_to_name, final_name_to_id

class FinalIdTest(TestCase):

    def test_one(self):
        for exp in range(0, 20):
            v = 11**exp
            self.assertEqual(final_name_to_id(final_id_to_name(v)), v)

