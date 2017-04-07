from django.db import migrations


def add_data(apps, schema_editor):
    Permission = apps.get_model('permissions', 'Permission')
    for name in ['draft', 'publish', 'validation', 'keyword']:
        Permission.objects.get_or_create(name=name)


def remove_data(apps, schema_editor):
    Permission = apps.get_model('permissions', 'Permission')
    for name in ['draft', 'publish', 'validation', 'keyword']:
        Permission.objects.get(name=name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_data, remove_data),
    ]
