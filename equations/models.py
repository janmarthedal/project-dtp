from django.db import models


class Equation(models.Model):
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    html = models.TextField()
    draft_access_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'equations'
        unique_together = ('format', 'math')

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)

    def to_source(self):
        if self.format == 'TeX':
            return '$${}$$'.format(self.math)
        return '${}$'.format(self.math)

    def to_data(self):
        return {'format': self.format, 'math': self.math, 'html': self.html}
