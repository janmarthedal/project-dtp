from django.utils import unittest
from items.helpers import BodyScanner

class BodyScannerTestCase(unittest.TestCase):

    def setUp(self):
        self.bs = BodyScanner("""
First [#non-negative-integer] paragraf
is started [@2222] here

We have
$$
\sum_{k=1}^n k
$$

and [number#positive-integer] then we get $e^x$ the
[@aB2c] result.
""")

    def test_concepts(self):
        concepts = self.bs.getConceptList()
        self.assertEqual(2, len(concepts), "a01")
        self.assertIn("non-negative-integer", concepts, "a02")
        self.assertIn("positive-integer", concepts, "a03")

    def test_itemrefs(self):
        items = self.bs.getItemRefList()
        self.assertEqual(2, len(items), "a01")
        self.assertIn("2222", items, "a02")
        self.assertIn("aB2c", items, "a03")
