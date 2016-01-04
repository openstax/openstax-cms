# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('pages', '0012_auto_20160104_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('link_external', models.URLField(blank=True, verbose_name='External link')),
                ('name', models.CharField(help_text='Funder Name', max_length=255)),
                ('description', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='aboutus',
            name='classroom_text',
        ),
        migrations.AddField(
            model_name='aboutus',
            name='funder_intro',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='aboutus',
            name='who_we_are',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='highereducationcarouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='higher_education_carousel_items', to='pages.HigherEducation'),
        ),
        migrations.CreateModel(
            name='AboutUsFunders',
            fields=[
                ('funders_ptr', models.OneToOneField(serialize=False, parent_link=True, primary_key=True, to='pages.Funders', auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, null=True, blank=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='funders', to='pages.AboutUs')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=('pages.funders', models.Model),
        ),
        migrations.AddField(
            model_name='funders',
            name='link_document',
            field=models.ForeignKey(to='wagtaildocs.Document', related_name='+', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='funders',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', related_name='+', null=True, blank=True),
        ),
    ]
