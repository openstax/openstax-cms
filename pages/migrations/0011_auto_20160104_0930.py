# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('pages', '0010_homepage_introduction'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Adopters',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='AdoptionForm',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BookDetail',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Books',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='EcosystemAllies',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Give',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HigherEducation',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HigherEducationCarouselItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('embed_url', models.URLField(verbose_name='Embed URL', blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('image', models.ForeignKey(related_name='+', blank=True, null=True, to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(related_name='+', blank=True, null=True, to='wagtaildocs.Document')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='K12',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Research',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='wagtailcore.Page', serialize=False)),
                ('classroom_text', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AddField(
            model_name='highereducationcarouselitem',
            name='link_page',
            field=models.ForeignKey(related_name='+', blank=True, null=True, to='wagtailcore.Page'),
        ),
        migrations.AddField(
            model_name='highereducationcarouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(to='pages.HomePage', related_name='higher_education_carousel_items'),
        ),
    ]
