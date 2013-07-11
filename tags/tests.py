from django.test import TestCase
from tags.models import Tag, Category
from tags.helpers import clean_tag

class TagTestCase(TestCase):

    def test_clean_tag(self):
        self.assertEqual("abc de", clean_tag("abc  de "))

    def test_get_or_create_category(self):
        orig_count = Category.objects.count()
        cat1 = Category.objects.fetch(['test_root', 'foo', 'bar'])
        self.assertEqual(Category.objects.count(), orig_count + 3, "a01")
        cat2 = Category.objects.fetch(['test_root', 'foo'])
        self.assertEqual(Category.objects.count(), orig_count + 3, "a02")
        cat3 = Category.objects.fetch(['test_root', 'foo', 'bla'])
        self.assertEqual(Category.objects.count(), orig_count + 4, "a03")

    def test_get_names(self):
        cat1 = Category.objects.fetch(['test_root', 'foo', 'bar'])
        self.assertEqual(cat1.get_tag_names(), ['test_root', 'foo', 'bar'], "a01")
