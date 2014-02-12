from django.test import TestCase
from tags.models import Category
from tags.helpers import clean_tag

class TagTestCase(TestCase):

    def test_clean_tag(self):
        self.assertEqual("abc de", clean_tag("abc  de "))

    def test_get_or_create_category(self):
        orig_count = Category.objects.count()
        Category.objects.from_tag_list(['test_root', 'foo', 'bar'])
        self.assertEqual(Category.objects.count(), orig_count + 3, 'a01')
        Category.objects.from_tag_list(['test_root', 'foo'])
        self.assertEqual(Category.objects.count(), orig_count + 3, 'a02')
        Category.objects.from_tag_list(['test_root', 'foo', 'bla'])
        self.assertEqual(Category.objects.count(), orig_count + 4, 'a03')

    def test_get_names(self):
        cat1 = Category.objects.from_tag_list(['test_root', 'foo', 'bar'])
        self.assertEqual(str(cat1), ['test_root', 'foo', 'bar'], 'a01')
