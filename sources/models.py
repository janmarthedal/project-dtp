from django.db import models
from django.conf import settings
from django.utils import timezone

class RefAuthor(models.Model):
    class Meta:
        db_table = 'ref_author'
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name

def normalize_author_list(authors):
    return sorted(set([s.strip() for s in authors]) - set(['']), key=str.lower)

class RefNodeManager(models.Manager):

    def add_node(self, created_by, sourcetype, authors, editors, field_values):
        node = RefNode(created_by=created_by, sourcetype=sourcetype)
        node.save()

        string_values = { k: None for k in RefNode.STRING_FIELDS }
        string_values.update({ k: field_values[k].lower() for k in RefNode.STRING_FIELDS })
        authors = normalize_author_list(authors)
        editors = normalize_author_list(editors)

        items = [':'.join(authors), string_values['title'], ':'.join(editors)]
        if sourcetype == 'book':
            for n in ['edition', 'series', 'volume', 'number', 'publisher', 'address',
                      'month', 'year', 'isbn10', 'isbn13']:
                items.append(string_values[n])
        elif sourcetype == 'article':
            for n in ['journal', 'volume', 'number', 'pages', 'month', 'year']:
                items.append(string_values[n])
        items.append(string_values['note'])

        node.digest = (';'.join([p or '' for p in items]))[:255]

        node.__dict__.update(string_values)
        node.authors = map(lambda n: RefAuthor.objects.get_or_create(name=n)[0], authors)
        node.editors = map(lambda n: RefAuthor.objects.get_or_create(name=n)[0], editors)
        node.save()

        return node


class RefNode(models.Model):
    class Meta:
        db_table = 'ref_node'
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=False)
    sourcetype = models.CharField(max_length=20, null=False)
    authors    = models.ManyToManyField(RefAuthor, related_name='auth+')
    editors    = models.ManyToManyField(RefAuthor, related_name='ed+')
    title      = models.CharField(max_length=255, db_index=True, null=True)
    publisher  = models.CharField(max_length=255, null=True)
    year       = models.CharField(max_length=255, null=True)
    volume     = models.CharField(max_length=255, null=True)
    number     = models.CharField(max_length=255, null=True)
    series     = models.CharField(max_length=255, null=True)
    address    = models.CharField(max_length=255, null=True)
    edition    = models.CharField(max_length=255, null=True)
    month      = models.CharField(max_length=255, null=True)
    journal    = models.CharField(max_length=255, null=True)
    pages      = models.CharField(max_length=255, null=True)
    isbn10     = models.CharField(max_length=255, null=True)
    isbn13     = models.CharField(max_length=255, null=True)
    note       = models.CharField(max_length=255, null=True)
    digest     = models.CharField(max_length=255, db_index=True, null=False, default='')
    objects = RefNodeManager()
    STRING_FIELDS = ['title', 'publisher', 'year', 'volume', 'number', 'series', 'address', 'edition',
                     'month', 'journal', 'pages', 'isbn10', 'isbn13', 'note']
    def __str__(self):
        if self.pk:
            return 'Source %d' % self.pk
        return 'New source'
    def json_data(self):
        data = dict(id=self.pk, type=self.sourcetype)
        for key in RefNode.STRING_FIELDS:
            if self.__dict__[key]:
                data[key] = self.__dict__[key]
        names = [a.name for a in self.authors.all()]
        if names: data['author'] = names
        names = [a.name for a in self.editors.all()]
        if names: data['editor'] = names
        return data

class ValidationBase(models.Model):
    class Meta:
        abstract = True
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at = models.DateTimeField(default=timezone.now, db_index=False)
    source     = models.ForeignKey(RefNode)
    location   = models.CharField(max_length=255, null=True)
    points     = models.IntegerField(default=0, null=False)
