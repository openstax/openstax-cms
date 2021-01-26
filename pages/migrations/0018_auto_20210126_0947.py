# Generated by Django 3.0.4 on 2021-01-26 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('pages', '0017_tutorlanding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ourimpactinstitutions',
            name='institutions_ptr',
        ),
        migrations.RemoveField(
            model_name='ourimpactinstitutions',
            name='page',
        ),
        migrations.DeleteModel(
            name='OurImpact',
        ),
        migrations.DeleteModel(
            name='OurImpactInstitutions',
        ),
    ]