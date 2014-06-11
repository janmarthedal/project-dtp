from django.utils.unittest import TestCase
from analysis.models import compute_score

class AnalysisTestCase(TestCase):

    def test_scores(self):
        chain = [(3, None), (2, None), (1, None), (2, 1), (1, 1), (0, 1), ]
        scores = [compute_score(r, p) for (r, p) in chain]
        for i in range(0, len(scores) - 1):
            self.assertLess(scores[i], scores[i+1], 'a{}'.format(i))
